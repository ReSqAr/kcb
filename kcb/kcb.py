import os
import time
import argparse
import subprocess
import pathlib
import stat
import psutil

import xdg
from xml.etree import ElementTree

# Debian package: python3-pydbus
import pydbus

from .lib.terminal import print_blue, print_red, print_green
from .lib.cd import cd

#
# Constants
#
BASH_PATH = xdg.XDG_CONFIG_HOME
if not BASH_PATH:
    BASH_PATH = os.path.expanduser('~/.config')
BASH_PATH = pathlib.Path(BASH_PATH) / "kcb"

DBUS_KDEC = 'org.kde.kdeconnect.daemon'
DBUS_KDEC_DEVICES = '/modules/kdeconnect/devices'

#
# Code.
#

# Create global session bus.
session_bus = pydbus.SessionBus()


def create_args_parser():
    """Create the argument parser."""

    parser = argparse.ArgumentParser()
    parser.add_argument('devices', nargs='*', help="device names")
    return parser


def dbus_get_nodes(obj):
    """Get nodes of the introspection data."""

    output = []
    xml_string = obj.Introspect()
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            output.append(child.attrib['name'])
    return output


def kdec_list_all_devices():
    """Create KDEConnect device ID -> KDEConnect device name mapping."""

    map_kdec_id_2_name = {}

    # Get DBUS KDEConnect device root.
    dbus_kdec_device_list = session_bus.get(DBUS_KDEC, DBUS_KDEC_DEVICES)

    # Use introspection to list all nodes (which are the devices).
    kdec_device_id_list = dbus_get_nodes(dbus_kdec_device_list)

    # Go through the devices and find their name.
    for kdec_device_id in kdec_device_id_list:
        kdec_device = session_bus.get(DBUS_KDEC, DBUS_KDEC_DEVICES + '/' + kdec_device_id)
        map_kdec_id_2_name[kdec_device_id] = kdec_device.name

    return map_kdec_id_2_name


def kdec_find_device_by_name(device_name):
    """Find KDEConnect device ID by KDEConnect device name."""

    # Find KDEConnect device ID -> KDEConnect device name mapping.
    map_kdec_id_2_name = kdec_list_all_devices()

    # Filter by name.
    kdec_ids = [kdec_id for kdec_id, name in map_kdec_id_2_name.items() if name == device_name]

    # Error handling: none or multiple devices found -> abort.
    if len(kdec_ids) == 0:
        all_device_names = ', '.join(sorted(map_kdec_id_2_name.values()))
        print_red('device name not found, available names are: {}'.format(all_device_names))
        return
    elif len(kdec_ids) > 1:
        print_red('multiple devices found with this name, skipping')
        return

    # At this point there is only KDEConnect device ID left.
    [kdec_id] =  kdec_ids
    return kdec_id


def kdec_mount_device(device_id):
    """Mount a device by its KDEConnect device ID, returns the mount path."""

    # Acquire DBUS sftp connection.
    kdec_sftp = session_bus.get(DBUS_KDEC, DBUS_KDEC_DEVICES + '/' + device_id + '/sftp')

    # Try mounting up to 10 times.
    for i in range(10):
        kdec_sftp.mount()

        # Stop if indeed mounted.
        if kdec_sftp.isMounted():
            break

        # Wait for a second.
        time.sleep(1)

    # Find mount path.
    for key, value in kdec_sftp.getDirectories().items():
        if "all files" in value.lower():
            return key
    else:
        print_red("mount point not found")
        return


def kdec_get_sftp_information(device_id):
    """Retrieve the sftp login information.
    
    Implementation note:
    We can't get this information directly, hence we have
    to extract it from the sshfs's command line parameters.
    """

    # Acquire DBUS sftp connection.
    kdec_sftp = session_bus.get(DBUS_KDEC, DBUS_KDEC_DEVICES + '/' + device_id + '/sftp')

    # Get the mount point.
    mount_point = kdec_sftp.mountPoint()

    for p in psutil.process_iter():
        p = p.as_dict(attrs=['exe', 'cmdline'])

        # Find the process which mounts our device.
        if p['exe'] == '/usr/bin/sshfs' and mount_point in p['cmdline']:
            cmdline = p['cmdline']
            # Example:
            # ['/usr/bin/sshfs', 'kdeconnect@192.168.178.50:/', '/run/user/1000/ff2885349915cc50', '-p', '1740', ...]
            [address] = [part for part in cmdline if '@' in part]
            username = address.split('@')[0]
            ip = address.split('@')[1].split(':/')[0]
            port = cmdline[cmdline.index('-p') + 1]

            return username, ip, port

    return None, None, None


def execute_device(device_name):
    """Run bash script identified by the given device name."""

    print()
    print_blue('executing device {}'.format(device_name))

    # Find device.
    kdec_device_id = kdec_find_device_by_name(device_name)
    # Error handling: device not found (error message already printed).
    if kdec_device_id is None:
        return
    else:
        print('device id: {}'.format(kdec_device_id))

    # Acquire device.
    kdec_device = session_bus.get(DBUS_KDEC, DBUS_KDEC_DEVICES + '/' + kdec_device_id)
    # Error handling: check active status.
    if not kdec_device.isReachable:
        print_red('device not reachable, skipping')
        return
    else:
        print('device is active')

    # Mount device.
    kdec_mount_point = kdec_mount_device(kdec_device_id)
    # Error handling: mount point not found (error message already printed).
    if kdec_mount_point is None:
        return
    else:
        print('mounted on: {}'.format(kdec_mount_point))

    # Create path to bash file (with some sanitation, no . or / or ;).
    bash_name = device_name.replace('.', '_').replace('/', '_').replace(';', '_') + '.sh'
    bash_path = BASH_PATH / bash_name
    # Error handling: check if the bash file exists.
    if not bash_path.exists():
        print_red('bash file ({}) not found, skipping'.format(bash_path))
        return
    else:
        print('bash file: {}'.format(bash_path))

    # Make bash file executable (user only) if necessary.
    mod = bash_path.stat().st_mode
    mod_new = mod | stat.S_IXUSR
    if mod != mod_new:
        print('making bash file executable...')
        bash_path.chmod(mod_new)

    # Build command from bash script path.
    bash_cmd = ["/bin/bash", str(bash_path)]

    # Build the scripts environment variables.
    bash_env = os.environ.copy()
    username, ip, port = kdec_get_sftp_information(kdec_device_id)
    if username:
        bash_env['SFTP_USERNAME'] = username
    if ip:
        bash_env['SFTP_IP'] = ip
    if port:
        bash_env['SFTP_PORT'] = port

    # Execute bash file in the mounted directory.
    with cd(kdec_mount_point):
        print_green('executing {}'.format(' '.join(bash_cmd)))
        subprocess.check_call(bash_cmd, env=bash_env)
        print_green('execution finished')


def run_app():
    """Run the app."""

    # Read arguments.
    parser = create_args_parser()
    args = parser.parse_args()

    # If arguments are given, use them, alternatively, use all of them.
    if len(args.devices) > 0:
        device_names = args.devices
    else:
        # Empty -> all devices.
        device_names = sorted(set(kdec_list_all_devices().values()))

    # Output.
    print('Requested the following {} device(s): {}'.format(len(device_names), ', '.join(device_names)))

    # Iterate over the desired devices.
    for device_name in device_names:
        execute_device(device_name)
