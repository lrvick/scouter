import os
import sys
import urllib.request
import shutil
import time
from distutils.version import StrictVersion

min_adb_version = "1.0.5"
work_dir = os.path.expanduser("~/.scouter")

def download(url,dest):
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    with urllib.request.urlopen(url) as response, open("%s/%s" % (work_dir,dest), 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def adb(args):
    stdout = ''
    command = 'adb %s' % args
    results = os.popen(command, "r")
    while 1:
        line = results.readline()
        if not line: break
        stdout += line
    return stdout

def fastboot(args):
    stdout = ''
    command = 'fastboot %s' % args
    results = os.popen(command, "r")
    while 1:
        line = results.readline()
        if not line: break
        stdout += line
    return stdout

def sanity_check():

    sys.stdout.write("Checking for adb... ")

    version = adb('version').split(' ')[4].replace('\n','')

    sys.stdout.write('Found %s \n' % version)

    if (StrictVersion(version) < StrictVersion(min_adb_version)):
        sys.stdout.write(
            "ADB Version is too old. Please upgrade to %s or newer"
            % min_adb_version
        )
        return False

    sys.stdout.write("Checking for fastboot... ")

    #if(fastboot('help')):
    #    sys.stdout.write('Found')
    #else:
    #    sys.stdout.write(
    #        "Fastboot missing. Please install and place in $PATH"
    #    )

    return True

if (sanity_check()):

    sys.stdout.write("Downloading rooted boot.img ... ")
    download("https://dl.google.com/glass/xe11/boot.img","boot.img")
    sys.stdout.write("Done \n")

    sys.stdout.write("Rebooting Glass into fastboot mode ... ")
    adb('reboot bootloader')
    while True:
        time.sleep(1)
        devices = fastboot('devices')
        if devices != "":
            break
    sys.stdout.write("Done \n")


