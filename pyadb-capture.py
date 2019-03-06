"""
adb cmd
"""
import os
from time import sleep

from pyadb import get_devices, execute_adb_shell, execute_adb, input_number

package_name = "cn.homelabs.gica"


def capture(dev, times):
    for i in range(times):
        # x=501.20844, y=168.93204
        print(execute_adb_shell(dev.dev_id, 'input tap 501.20844 168.93204'))
        sleep(16)

        pic_path = r'sdcard/Android/data/%s/files/Pictures/Samples' % package_name
        dst_path = r'E:\111\Samples\%s\Pic-%d' % (dev.name, i)
        pics = execute_adb_shell(dev.dev_id, 'ls %s' % pic_path).split()
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        for p in pics:
            execute_adb(dev.dev_id, 'pull %s/%s %s' % (pic_path, p, os.path.join(dst_path, p)))


devices = get_devices()
[print('%d: Device: %s' % (i, devices[i].dev_id)) for i in range(len(devices))]
device = None
if not devices:
    print('no devices connected')
elif len(devices) == 1:
    device = devices[0]
else:
    device = devices[input_number(len(devices))]
if device:
    ret = execute_adb_shell(device.dev_id, 'monkey -p %s -c android.intent.category.LAUNCHER 1' % package_name)
    print(ret)

    capture(device, 100)
