# looking_glass_py
a Looking Glass Python Lib

## get_cal.py
Get a Calibration class of the Looking Glass from the usb port

    :param usb_vid: Looking Glass USB port VID, look up by 'sudo lsusb | grep Microchip'
    
    :param usb_pid: Looking Glass USB port PID, look up by 'sudo lsusb | grep Microchip'
    
    :param save_flag: whether to save the json
    
    :param json_name: save json name
    
    :return: a Calibration class of the Looking Glass

### usage

```
import get_cal
c = get_cal.lg_json()
```

> notice: please insure that you have the right to the usb permession and install all the required python modules correctly.
