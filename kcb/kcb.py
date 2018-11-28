import os
import sys
import time
import argparse
import subprocess
import pathlib
import stat
from xml.etree import ElementTree

import pydbus # python3-pydbus

from .lib.terminal import print_blue, print_red, print_green
from .lib.cd import cd


#
# constants
#
BASH_PATH = '~/.config/kcb/'
BASH_PATH = os.path.expanduser(BASH_PATH)
BASH_PATH = pathlib.Path(BASH_PATH)

DBUS_KDEC = 'org.kde.kdeconnectd'
DBUS_KDEC_DEVICES = '/modules/kdeconnect/devices'


#
# code
#

# create global session bus
session_bus = pydbus.SessionBus()


def create_parser():
    """ create the argument parser """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('devices', nargs='*', help="device names")
    return parser


def dbus_get_nodes(obj):
    """ get nodes of the introspection data """
    
    output = []
    xml_string = obj.Introspect()
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            output.append(child.attrib['name'])
    return output


def kdec_list_all_devices():
    """ create KDEConnect device ID -> KDEConnect device name mapping """
    
    map_kdec_id_2_name = {}
    
    # get DBUS KDEConnect device root
    dbus_kdec_device_list = session_bus.get(DBUS_KDEC,DBUS_KDEC_DEVICES)
    
    # use introspection to list all nodes (which are the devices)
    kdec_device_id_list = dbus_get_nodes(dbus_kdec_device_list)
    
    # go through the devices and find their name
    for kdec_device_id in kdec_device_id_list:
        kdec_device = session_bus.get(DBUS_KDEC,DBUS_KDEC_DEVICES + '/' + kdec_device_id)
        map_kdec_id_2_name[kdec_device_id] = kdec_device.name
        
    return map_kdec_id_2_name


def kdec_find_device_by_name(device_name):
    """ find KDEConnect device ID by KDEConnect device name """
    
    # find KDEConnect device ID -> KDEConnect device name mapping
    map_kdec_id_2_name = kdec_list_all_devices()
    
    # filter by name
    kdec_ids = [ kdec_id for kdec_id, name in map_kdec_id_2_name.items() if name == device_name]
    
    # error handling: none or multiple devices found -> abort
    if len(kdec_ids) == 0:
        print_red('device name not found, available names are: {}'.format(', '.join(sorted(map_kdec_id_2_name.values()))))
        return
    elif len(kdec_ids) > 1:
        print_red('multiple devices found with this name, skipping')
        return
    
    # at this point there is only KDEConnect device ID left
    return kdec_ids[0]


def kdec_mount_device(device_id):
    """ mount a device by its KDEConnect device ID, returns the path """
    
    # acquire DBUS sftp connection
    kdec_sftp = session_bus.get(DBUS_KDEC,DBUS_KDEC_DEVICES + '/' + device_id + '/sftp')

    # mount up to 10 times    
    for i in range(10):
        kdec_sftp.mount()
        
        # stop if indeed mounted
        if kdec_sftp.isMounted():
            break
        
        # wait for a second
        time.sleep(1)
    
    # find mount path
    for key,value in kdec_sftp.getDirectories().items():
        if "all files" in value.lower():
            return key
    else:
        print_red("mount point not found")
        return


def execute_device(device_name):
    """ run bash script for the given device name """
    
    print()
    print_blue('executing device {}'.format(device_name))
    
    
    # find device
    kdec_device_id = kdec_find_device_by_name(device_name)
    # error handling: device not found (error message already printed)
    if kdec_device_id is None:
        return
    else:
        print('device id: {}'.format(kdec_device_id))


    # acquire device
    kdec_device = session_bus.get(DBUS_KDEC,DBUS_KDEC_DEVICES + '/' + kdec_device_id)
    # error handling: check active status
    if not kdec_device.isReachable:
        print_red('device not reachable, skipping')
        return
    else:
        print('device is active')


    # mount device
    kdec_mount_point = kdec_mount_device(kdec_device_id)
    # error handling: mount point not found (error message already printed)
    if kdec_mount_point is None:
        return
    else:
        print('mounted on: {}'.format(kdec_mount_point))

    
    # create path to bash file (with some sanitation, no . or /)
    bash_name = device_name.replace('.','_').replace('/','_') + '.sh'
    bash_path = BASH_PATH / bash_name
    # error handling: check if the bash file exists
    if not bash_path.exists():
        print_red('bash file ({}) not found, skipping'.format(bash_path))
        return
    else:
        print('bash file: {}'.format(bash_path))


    # make bash file executable (user only) if necessary
    mod = bash_path.stat().st_mode
    mod_new = mod | stat.S_IXUSR
    if mod != mod_new:
        print('making bash file executable...')
        bash_path.chmod(mod_new)
    
    
    # execute bash file in the mounted directory
    with cd(kdec_mount_point):
        print_green('executing {}'.format(bash_path))
        subprocess.check_call('"{}"'.format(bash_path),shell=True)
        print_green('execution finished')


def run_app():
    """ run the app """
    
    # read arguments
    parser = create_parser()
    args = parser.parse_args()
    
    
    # if arguments are given, use them, alternatively, use all of them
    if len(args.devices) > 0:
        device_names = args.devices
    else:
        # empty -> all devices
        device_names = sorted(set(kdec_list_all_devices().values()))
    
    
    # output
    print('Requested the following {} device(s): {}'.format(len(device_names),', '.join(device_names)))
    
    
    # iterate over the desired devices
    for device_name in device_names:
        execute_device(device_name)
    
