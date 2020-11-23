import gxipy as gx
import time
import datetime
import json
import os
from PIL import Image
import cv2

def main(num, folder_size):
    # default image save path
    path = './test_img/'

    # load camera config file
    with open('./camera_config.json', 'r', encoding='utf8') as f:
        camera_config = json.load(f)
        SN = camera_config['DeviceSerialNumber']
        ExposureTime = camera_config['ExposureTime']
        Gain = camera_config['Gain']
        Binning = camera_config['Binning']

    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num == 0:
        print("Number of enumerated devices is 0")
        return

    # open the first device
    cam = device_manager.open_device_by_sn(SN)

    # set exposure & gain
    cam.ExposureTime.set(ExposureTime)
    cam.Gain.set(Gain)
    cam.BinningHorizontal.set(Binning)
    cam.BinningVertical.set(Binning)

    # set trigger mode and trigger source
    # cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
    cam.TriggerMode.set(gx.GxSwitchEntry.ON)
    cam.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)

    # start data acquisition
    cam.stream_on()

    for i in range(num):
        start_time = time.time()

        # send software trigger command
        cam.TriggerSoftware.send_command()

        # get raw image
        raw_image = cam.data_stream[0].get_image()
        if raw_image is None:
            print("Getting image failed.")
            continue

        # create numpy array with data from raw image
        img = raw_image.get_numpy_array()
        if img is None:
            continue

        # show acquired image
        cv2.imshow('frame', img)
        cv2.waitKey(1)

        # img = Image.fromarray(img, 'L')  
        # img = img.resize((352, 352))
        print('Image %d capture time: %.3f' % (i, time.time() - start_time))
        # save image if folder has <= folder_size images, remove from the 1st 
        # image if folder has > folder_size images
        files = os.listdir(path)
        files = sorted(files, key=lambda x: os.path.getctime(os.path.join(path, x)))
        img_num = len(files)
        if img_num < folder_size:
            cv2.imwrite(path + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f') + '.bmp', img)
            # img.save(path + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f') + '.bmp')
        else:
            os.remove(os.path.join(path, files[0]))
            cv2.imwrite(path + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f') + '.bmp', img)
            # img.save(path + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.%f') + '.bmp')

        # print frame ID & running time for each image
        print("Frame ID: %d   Running time: %.3f"
              % (raw_image.get_frame_id(), (time.time() - start_time)))

    # stop acquisition
    cam.stream_off()

    # close device
    cam.close_device()


if __name__ == "__main__":
    main(200, 100)