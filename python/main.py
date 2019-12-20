#-*- coding:utf-8 -*-

import RPi.GPIO as GPIO
import time,os
import control
import sys
from pathlib import Path
from multiprocessing import Process, Manager, Event

defaultGlobalConfig = {
    'GPIO' : {
        'ledWhitePin' : 16,
        'ledYellowPin' : 20,
        'ledRedPin' : 21,
        'lightSensorPin' : 26,
        'fireSensorPin' : 19,
        'pirSensorPin' : 17,
        'pirSensorEPin' : 23,
        'buzPin' : 12
    },
    'Hat' : {
        'serialDeviceName' : '/dev/ttyUSB0',
        'sendSerPort' : '16868'
    }
}

GPIO.setmode(GPIO.BCM)

CommonConfigDir = './config/'
configNameList = ['GPIO', 'Hat']


configManager = Manager().dict()
sensorDataList = Manager().dict()

hatEvent = Event()
saveConfigEvent = Event()
offEvent = Event()



def main():
    # GPIO.setup(gpio_light_sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.setup(gpio_pir_sensor_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # GPIO.add_event_detect(gpio_light_sensor, GPIO.BOTH, callback=a, bouncetime=200)
    # GPIO.add_event_detect(gpio_light_sensor, GPIO.BOTH, callback=a, bouncetime=200)
    # GPIO.add_event_callback()
    # GPIO.cleanup()

    # Load config
    if control.initConfig(defaultGlobalConfig , configNameList) & control.loadConfig(configManager ,configNameList):
        pass
    else:
        sys.exit(2)
    
    # Setup GPIO status
    chanOutHighList = []
    chanOutLowList = [int(configManager['buzPin']),int(configManager['ledWhitePin'])]
    GPIO.setup(chanOutLowList, GPIO.OUT, initial=GPIO.LOW)

    chanInList = []
    GPIO.setup(chanInList, GPIO.IN)





    dataGetProcess = Process(target = control.getSensorData, args = (sensorDataList, hatEvent, configManager['serialDeviceName']))
    dataSendSerProcess = Process(target = control.creatDataSendServer, args = (sensorDataList, hatEvent, int(configManager['sendSerPort']),))
    configSaveProcess = Process(target = control.wattingSaveConfig, args = (defaultGlobalConfig, configManager, configNameList, saveConfigEvent))
    
    dataGetProcess.start()
    dataSendSerProcess.start()
    configSaveProcess.start()

    
    dataSendSerProcess.join()

    


if __name__ == "__main__":
    try:
        main()
    except:
        # print('Some error')
        pass
    finally:
        GPIO.cleanup()
        control.saveConfig(defaultGlobalConfig, configManager, configNameList)
        print('Programm exit')