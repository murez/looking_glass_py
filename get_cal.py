from struct import unpack
import json
import hid
from math import cos, atan

USB_VID = 0x04d8
USB_PID = 0xef7e


def hid_multiread(dev):
    data = dev.read(128, timeout_ms=10)
    res = data

    while len(data) > 0:
        data = dev.read(128, timeout_ms=10)
        res.extend(data)

    return res


def hid_query(dev, addr):
    # 68 byte request, might actually need 64, but not clear
    # when hid versus hidraw is used.
    buffer = bytearray([0] * 68)

    buffer[0] = 0  # Report ID
    buffer[1] = 0
    buffer[2] = addr >> 8  # Page to read
    buffer[3] = addr & 0xff

    res = dev.send_feature_report(buffer)
    assert res >= 0

    res = hid_multiread(dev)
    assert res[:4] == list(buffer[:4])

    return res[4:]


class Calibration:

    def __init__(self, json_in):
        config = json_in

        self.screenW = int(config['screenW']['value'])
        self.screenH = int(config['screenH']['value'])
        self.DPI = int(config['DPI']['value'])
        self.pitch = config['pitch']['value']
        self.slope = config['slope']['value']
        self.center = config['center']['value']

        # Physical image width
        self.screenInches = self.screenW / self.DPI

        self.pitch = self.pitch * self.screenInches * cos(atan(1.0 / self.slope))
        self.tilt = self.screenH / (self.screenW * self.slope)
        self.subp = 1.0 / (3 * self.screenW) * self.pitch


def lg_json(usb_vid=USB_VID, usb_pid=USB_PID, save_flag=False, json_name="LookingGlassConfig.json"):
    '''
    :param usb_vid: Looking Glass USB port VID, look up by 'sudo lsusb | grep Microchip'
    :param usb_pid: Looking Glass USB port PID, look up by 'sudo lsusb | grep Microchip'
    :param save_flag: whether to save the json
    :param json_name: save json name
    :return: a Calibration class of the Looking Glass
    '''
    devs = list(hid.enumerate(usb_vid, usb_pid))
    # print(devs)
    assert len(devs) == 1
    devinfo = devs[0]

    dev = hid.device()
    dev.open_path(devinfo['path'])
    # dev.set_nonblocking(1)

    # Data is read in pages of 64 bytes. First page (0) starts with a
    # 4 byte header denoting the length of the calibration data (in JSON
    # format)
    page = hid_query(dev, 0)

    json_size = unpack('>I', bytes(page[:4]))[0]
    # print('JSON size: %d' % json_size)

    json_data = page[4:]
    addr = 1
    while len(json_data) < json_size:
        page = hid_query(dev, addr)
        json_data.extend(page)
        addr += 1

    json_data = json_data[:json_size]
    json_data = bytes(json_data)
    json_data = json_data.decode('utf8')

    # Pretty print
    parsed = json.loads(json_data)
    print(json.dumps(parsed, indent=4))
    if save_flag:
        with open(json_name, 'w') as outfile:
            outfile.write(json.dumps(parsed, indent=4))
    return Calibration(parsed)