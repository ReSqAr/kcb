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

BASH_PATH = '~/.config/kdecb/'
BASH_PATH = os.path.expanduser(BASH_PATH)
BASH_PATH = pathlib.Path(BASH_PATH)

DBUS_KDECONNECT = 'org.kde.kdeconnectd'
DBUS_KDEC_DEVICES = '/modules/kdeconnect/devices'

session_bus = pydbus.SessionBus()

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('devices', nargs='*', help="device names")
    return parser


def dbus_get_nodes(obj):
    output = []
    xml_string = obj.Introspect()
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            output.append(child.attrib['name'])
    return output


def mount_device(kdec_device_id):
    
    proxy = session_bus.get_object(DBUS_KDECONNECT,"/modules/kdeconnect/devices/45a1761fbc4f34c3/sftp")

    try:
        if proxy.mountAndWait() == False:
            print("mount failed")
            return
    except dbus.exceptions.DBusException as e:
        print("\033[91mCannot connect.\033[0m")
        return
        

    # find mount mount
    for key,value in proxy.getDirectories().items():
        if "Camera pictures(Internal storage)" in value:
            mount_path = key
            break
    else:
        print("Could not find mount point.")

    # set arguments
    source = pathlib.Path( str(mount_path) )
    destination = pathlib.Path( "/home/yasin/Pictures/annex-yy/Yasins Smartphone - 2 - G4/" )
    state_file = pathlib.Path( "/home/yasin/Pictures/.config/YasinsSmartphone_2_LG4.state" )


def kdec_list_all_devices():
    # find kde connect id -> device name mapping
    map_kdec_id_2_name = {}
    
    dbus_kdec_device_list = session_bus.get(DBUS_KDECONNECT,DBUS_KDEC_DEVICES)
    kdec_device_id_list = dbus_get_nodes(dbus_kdec_device_list)
    
    for kdec_device_id in kdec_device_id_list:
        kdec_device = session_bus.get(DBUS_KDECONNECT,DBUS_KDEC_DEVICES + '/' + kdec_device_id)
        map_kdec_id_2_name[kdec_device_id] = kdec_device.name
        
    return map_kdec_id_2_name


def kdec_find_device_by_name(device_name):
    # find kde connect id -> device name mapping
    map_kdec_id_2_name = kdec_list_all_devices()
    
    # look for kdeconnect ids which are connected to the given device name
    kdec_ids = [ kdec_id for kdec_id, name in map_kdec_id_2_name.items() if name == device_name]
    
    # error handling
    if len(kdec_ids) == 0:
        print_red('device name not found, potential names are: {}'.format(', '.join(map_kdec_id_2_name.values())))
        return
    elif len(kdec_ids) > 1:
        print_red('multiple devices found with this name, skipping')
        return
    
    # at this point there is only id left
    return kdec_ids[0]


def kdec_mount_device(device_id):
    # acquire sftp connection
    kdec_sftp = session_bus.get(DBUS_KDECONNECT,DBUS_KDEC_DEVICES + '/' + device_id + '/sftp')

    # mount up to 10 times    
    for i in range(10):
        kdec_sftp.mount()
        
        if kdec_sftp.isMounted():
            break
        
        time.sleep(1)
    
    # find mount mount
    for key,value in kdec_sftp.getDirectories().items():
        if "all files" in value.lower():
            return key
    else:
        print_red("mount point not found")
        return


def execute_device(device_name):
    print()
    print_blue('executing device {}'.format(device_name))
    
    # find device
    kdec_device_id = kdec_find_device_by_name(device_name)
    # error handling: device not found
    if kdec_device_id is None:
        return

    print('device id: {}'.format(kdec_device_id))


    # acquire device
    kdec_device = session_bus.get(DBUS_KDECONNECT,DBUS_KDEC_DEVICES + '/' + kdec_device_id)
    # error handling: check active status
    if not kdec_device.isReachable:
        print_red('device not reachable, skipping')
        return
    
    print('device is active')


    # mount device
    kdec_mount_point = kdec_mount_device(kdec_device_id)
    # error handling: mount point not found
    if kdec_mount_point is None:
        return

    print('mounted on: {}'.format(kdec_mount_point))

    
    # find desired file
    bash_name = device_name.replace('.','_').replace('/','_') + '.sh'
    bash_path = BASH_PATH / bash_name
    
    # error handling: check if the file exists
    if not bash_path.exists():
        print_red('bash file ({}) not found, skipping'.format(bash_path))
        return

    print('bash file: {}'.format(bash_path))

    # make executable if necessary
    mod = bash_path.stat().st_mode
    mod_new = mod | stat.S_IXUSR
    if mod != mod_new:
        print('making bash file executable...')
        bash_path.chmod(mod_new)
    
    # change directory
    with cd(kdec_mount_point):
        print_green('executing {}'.format(bash_path))
        subprocess.check_call(str(bash_path),shell=True)
        print_green('execution finished')


def run_app():
    parser = create_parser()
    args = parser.parse_args()
    
    print('Requested the following {} device(s): {}'.format(len(args.devices),', '.join(args.devices)))
    
    for device_name in args.devices:
        execute_device(device_name)
    
