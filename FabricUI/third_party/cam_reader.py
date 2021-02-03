# version:1.0.1808.9101
import cv2
import gxipy as gx
from PIL import Image
from abc import ABC,abstractmethod


class Reader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def read(self):
        pass


def acq_color(device):
    """
           :brief      acquisition function of color device
           :param      device:     device object[Device]
           :param      num:        number of acquisition images[int]
    """
    img = None

    # send software trigger command
    device.TriggerSoftware.send_command()

    # get raw image
    raw_image = device.data_stream[0].get_image()
    if raw_image is None:
        print("Getting image failed.")
        return img

    # get RGB image from raw image
    rgb_image = raw_image.convert("RGB")
    if rgb_image is None:
        return img

    # create numpy array with data from raw image
    numpy_image = rgb_image.get_numpy_array()
    if numpy_image is None:
        return img

    # show acquired image
    #img = Image.fromarray(numpy_image, 'RGB')


    # # print height, width, and frame ID of the acquisition image
    # print("Frame ID: %d   Height: %d   Width: %d"
    #       % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))
    return numpy_image



def acq_mono(device):
    """
           :brief      acquisition function of mono device
           :param      device:     device object[Device]
           :param      num:        number of acquisition images[int]
    """
    # send software trigger command
    device.TriggerSoftware.send_command()

    # get raw image
    raw_image = device.data_stream[0].get_image()
    if raw_image is None:
        print("Getting image failed.")
        return None

    # create numpy array with data from raw image
    numpy_image = raw_image.get_numpy_array()
    if numpy_image is None:
        return None

    # show acquired image
    # img = Image.fromarray(numpy_image, 'L')
    # #img.show()

    # # print height, width, and frame ID of the acquisition image
    # print("Frame ID: %d   Height: %d   Width: %d"
    #       % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))
    return numpy_image


class GXCamReader(object):
    setting = {"exposure_time":1000,"gain":25,"binning":4}

    def __init__(self):
        self.cam = None
        # create a device manager
        self.device_manager = gx.DeviceManager()
        dev_num, dev_info_list = self.device_manager.update_device_list()
        if dev_num is 0:
            print("Number of enumerated devices is 0")
            return

        # open the first device
        self.cam = self.device_manager.open_device_by_index(1)

        # send software trigger command
        self.cam.TriggerMode.set(gx.GxSwitchEntry.ON)
        self.cam.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)

        # start data acquisition
        self.cam.stream_on()
        self.init_setting()

    def init_setting(self,**args):
        expo = args.get("exposure_time",1000);
        self.set_expo(expo)
        gain = args.get("gain",0);
        self.set_gain(gain)
        binning = args.get("binning",4)
        #self.set_binning(binning)

    def set_expo(self,exposure_time=1000):
        self.cam.ExposureTime.set(exposure_time)

    def set_gain(self,gain=0):
        self.cam.Gain.set(gain)

    def set_binning(self,binning=4):
        try:  # Because some DH cameras do not support "binning"
            self.cam.BinningHorizontal.set(binning)
            self.cam.BinningVertical.set(binning)
        except Exception as expt:
            print(expt, flag="warning")

    def read(self):
        # camera is color
        if self.cam.PixelColorFilter.is_implemented() is True:
            img = acq_color(self.cam)
        # camera is mono
        else:
            img = acq_mono(self.cam)

        return img

    def __del__(self):
        if hasattr(self,'cam'):
            self.cam.stream_off()
            self.cam.close_device()
            del self.cam
            
            
if __name__ == "__main__":
    reader = GXCamReader()
    while True:
        img = reader.read()
        img = cv2.resize(img, (720,540), cv2.INTER_LINEAR)
        cv2.imshow("gx image", img)
        key = cv2.waitKey(100)&0xff
        if chr(key) == 'q':
            break;