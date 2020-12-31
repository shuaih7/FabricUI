import RPi.GPIO as GPIO
import time

def signal_detector(input_pin = 18):
    # set default value
    prev_value = None

    # set to BCM mode
    GPIO.setmode(GPIO.BCM)
    # set the pin as input
    GPIO.setup(input_pin, GPIO.IN)
    print('Starting demo now! Press CTRL+C to exit')

    try:
        # set start time to measure second used per round
        start = time.time()
        while True:
            value = GPIO.input(input_pin)
            if value != prev_value:
                # GPIO is HIGH when no signal coming in
                if value == GPIO.HIGH:
                    value_str = 'HIGH'
                # GPIO changed to LOW when signal coming in
                else:
                    value_str = 'LOW'
                    # calculate second used per round
                    spr = time.time() - start
                    # calculate RPM
                    rpm = 60 / spr
                    # reset start time for next round
                    start = time.time()
                    print('Current RPM is %.2f' % rpm)
                print("Value read from pin {} : {}".format(input_pin, value_str))
                prev_value = value
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    signal_detector()
