"""
adb cmd
"""
import os


class Device:
    def __init__(self, dev_id, name, product=None, model=None):
        self.__dev_id = dev_id
        self.__name = name
        self.__product = product
        self.__model = model

    def __str__(self):
        return 'Device: id=%s name=%s product=%s model=%s' % (self.__dev_id, self.__name, self.__product, self.__model)

    __repr__ = __str__

    @property
    def dev_id(self):
        return self.__dev_id


def execute_cmd(command) -> str:
    print(command)
    return os.popen(command).read().strip()


def execute_adb(dev_id, cmd):
    cmd_adb_shell_dev = "adb -s {dev_id} {cmd}"
    return execute_cmd(cmd_adb_shell_dev.format(dev_id=dev_id, cmd=cmd))


def execute_adb_shell(dev_id, cmd):
    cmd_adb_shell_dev = "adb -s {dev_id} shell '{cmd}'"
    return execute_cmd(cmd_adb_shell_dev.format(dev_id=dev_id, cmd=cmd))


def get_devices() -> list:
    def _get_device(dev_info) -> Device:
        dev_id = dev_info[0]
        d = []
        [d.append(e) if len(e) > 1 else print('') for e in [s.split(':') for s in dev_info]]
        dev_dict = dict(d)
        return Device(dev_id, dev_dict['device'], dev_dict['product'], dev_dict['model'])

    out = execute_cmd('adb devices -l')
    lines = out.splitlines()[1:]
    return [_get_device(l.split()) for l in lines]


def adb_pull(dev, src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    print(execute_adb(dev.dev_id, 'pull {src} {dst}'.format(src=src, dst=dst)))


def input_number(max_len) -> int:
    while True:
        try:
            val = int(input('Please Select:'))
            if 0 <= val < max_len:
                return val
            else:
                print('You have input invalid number.Should between 0 and', max_len)
        except ValueError:
            print('input a valid number.')


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
    path = input('Input Saved Path:')
    while path != 'exit':
        if path and len(path.strip()):
            adb_pull(device, r'sdcard/Android/data/cn.homelabs.algorithm.sample/files/Pictures/Samples',
                     r'E:\111\Samples\%s' % path.strip())
        path = input('Input Saved Path:')
