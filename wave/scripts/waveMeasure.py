import spidev
import time
import RPi.GPIO as GPIO
import numpy as np
import matplotlib.pyplot as plt


spi = spidev.SpiDev()


def initSpiAdc():
    spi.open(0, 0)
    spi.max_speed_hz = 1600000
    print ("SPI for ADC have been initialized")


def deinitSpiAdc():
    spi.close()
    print ("SPI cleanup finished")


def getAdc():
    adcResponse = spi.xfer2([0, 0])
    adc = ((adcResponse[0] & 0x1F) << 8 | adcResponse[1]) >> 1

    return adc


def getMeanAdc(samples):
    sum = 0
    for i in range(samples):
        sum += getAdc()
    
    return int(sum / samples)


def waitForOpen():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.IN)

    print('GPIO initialized. Wait for door opening...')

    while GPIO.input(2) < 1:
        pass

    GPIO.cleanup()
    print('The door is open. GPIO has been cleaned up. Start sampling...')


def saveMeasures(measures, count, samplesInMeasure, start, finish):
    experimentDuration = finish - start
    samplingPeriod = experimentDuration / count
    samplingFrequency = count / experimentDuration
    
    filename = 'wave-data {}.txt'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))

    with open(filename, "w") as outfile:
        outfile.write('- Wave Lab\n\n')
        outfile.write('- Experiment date = {}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
        outfile.write('- Experiment duration = {:.2f} s\n'.format(experimentDuration))
        outfile.write('- Number of samples in measure = {}\n'.format(samplesInMeasure))
        outfile.write('- Sampling period = {:.2f} us\n'.format(samplingPeriod * 1e6))
        outfile.write('- Sampling frequency = {} Hz\n'.format(int(samplingFrequency)))
        outfile.write('- Samples count = {}\n\n'.format(count))
        
        outfile.write('- adc12bit\n')
        np.savetxt(outfile, np.array(measures).T, fmt='%d')


def showMeasures(measures, count, samplesInMeasure, start, finish):
    samplingTime = finish - start
    samplingPeriod = samplingTime / count
    samplingFrequency = count / samplingTime

    print('Experiment date = {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))))
    print('Experiment duration = {:.2f} s'.format(samplingTime))
    print('Number of samples in measure = {}\n'.format(samplesInMeasure))
    print('Sampling period = {:.2f} us'.format(samplingPeriod * 1e6))
    print('Sampling frequency = {} Hz'.format(int(samplingFrequency)))
    print('Samples count = {}'.format(count))

    plt.plot(measures)
    plt.show()



initSpiAdc()

try:
    # 1. колибровка
    for i in range(6):
        print("\n\n\n")
        h = input("Write height wather (mm): ")
        #сбор данных
        sample = []
        start = time.time()
        while True:
            finish = time.time()
            if finish - start >= 10:
                break
            sample.append(getAdc())

        #сохранение данных в файл
        saveMeasures(sample, len(sample), 1, start, finish)
        showMeasures(sample, len(sample), 1, start, finish)
    

    # 2. Измерения
    input("press Enter to start experement")
    #сбор данных
    sample = []
    waitForOpen()
    print("start experement")
    start = time.time()
    while True:
        finish = time.time()
        if finish - start >= 30:
            break
        sample.append(getAdc())
    
    #сохранение данных в файл
    saveMeasures(sample, len(sample), 1, start, finish)
    showMeasures(sample, len(sample), 1, start, finish)

finally:
    deinitSpiAdc()