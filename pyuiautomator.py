import os
from time import sleep

import uiautomator2 as u2

package_name = 'cn.homelabs.gica'
device = '192.168.1.234'


def capture(times):
    for i in range(times):
        # 拍照
        d(resourceId="%s:id/capture" % package_name).click()
        sleep(6)
        pic_path = r'sdcard/Android/data/%s/files/Pictures/Samples' % package_name
        dst_path = r'E:\111\Samples\%s\Pic-%d' % (device, i)
        pics = d.adb_shell('ls', pic_path).split()
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        for p in pics:
            d.pull('%s/%s' % (pic_path, p), os.path.join(dst_path, p))


d = u2.connect(device)

# 启动拍照app
d.app_start(package_name)
capture(1)
