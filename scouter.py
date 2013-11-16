import os
import sys
import urllib.request
import shutil
import time
import subprocess
import zipfile
from distutils.version import StrictVersion

min_adb_version = "1.0.5"
work_dir = os.path.expanduser("~/.scouter")

def download(url,dest):
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    with urllib.request.urlopen(url) as response, open("%s/%s" % (work_dir,dest), 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def run(cmd):
    p = subprocess.check_output(cmd.split(" "))
    return p.decode("utf-8")

def extract(filename) :
   zipFile = zipfile.ZipFile("%s/%s" % (work_dir,filename))
   zipFile.extractall(work_dir)

def sanity_check():

    sys.stdout.write("Checking for adb... ")

    if(shutil.which('adb')):

        version = run('adb version').split(' ')[4].replace('\n','')

        sys.stdout.write('Found %s \n' % version)

        if (StrictVersion(version) < StrictVersion(min_adb_version)):
            sys.stdout.write(
                "ADB Version is too old. Please upgrade to %s or newer"
                % min_adb_version
            )
            return False
    else:
        sys.stdout.write('Missing \n')
        sys.stdout.write(
            "adb is missing. Please install and place in $PATH"
        )

    sys.stdout.write("Checking for fastboot... ")

    if(shutil.which('fastboot')):
        sys.stdout.write('Found \n')
    else:
        sys.stdout.write('Missing \n')
        sys.stdout.write(
            "Fastboot missing. Please install and place in $PATH"
        )

    return True


if (sanity_check()):

    sys.stdout.write("Downloading boot.img ... ")
    download("https://dl.google.com/glass/xe11/boot.img","boot.img")
    sys.stdout.write("Done \n")

    sys.stdout.write("Downloading superuser.zip ... ")
    download("http://download.clockworkmod.com/superuser/superuser.zip","superuser.zip")
    sys.stdout.write("Done \n")

    sys.stdout.write("Rebooting Glass into fastboot mode ... ")
    run('adb reboot bootloader')
    while True:
        time.sleep(1)
        devices = run('fastboot devices')
        if devices != "":
            break
    sys.stdout.write("Done \n")

    sys.stdout.write("Unlocking Bootloader ... ")
    run('fastboot oem unlock')
    run('fastboot oem unlock')
    sys.stdout.write("Done \n")

    sys.stdout.write("Flashing boot.img ... ")
    run('fastboot flash boot %s/boot.img' % work_dir)
    sys.stdout.write("Done \n")

    sys.stdout.write("Rebooting ... ")
    run('fastboot reboot')
    sys.stdout.write("Done \n")

    sys.stdout.write("Installing Superuser and su ... \n")
    extract('superuser.zip')
    # replace with something to detect when thing is actually rebooted
    # for now sleep for one min
    time.sleep(60)
    run("adb root")
    run("adb install %s/Superuser.apk" % work_dir)
    run("adb push %s/armeabi/su /system/bin/" % work_dir)
    run("adb push %s/armeabi/su /system/xbin/" % work_dir)
    run("adb shell 4755 /system/bin/su")
    run("adb shell 4755 /system/xbin/su")
    sys.stdout.write("Done \n")
