__author__ = 'Chris'

#Read serial data, validate it and write it to a csv file.  Start a new file daily at midnight
#Uploads file to web server via an http POST

import serial
import time
import requests


def makeName(seconds):
    '''Produce a file name string in the form YYYYMMDD.csv'''
    return time.strftime('%Y%m%d.csv', time.gmtime(seconds))

def uploadFile(fileName):
    ''' Send File to webserver using http POST'''
    url = 'http://cjones.org.uk/humidity/uploader.php'
    password = "K77ENDx9GwU2hV3PZpZr"   # Not great to have this in the source file
    payload = {'pass': password}
    files = {'uploadedfile': open(fileName, 'r')}
    r = requests.post(url, files=files, data=payload)
    print r.text

inputDev = serial.Serial(2, 9600, timeout=70)

startTime = 0
outFile = 0

for line in inputDev:
    if makeName(startTime) != makeName(time.time()): # Not comparing times, comparing file names (and therefore dates)
        # It's a new day, time for a new file.
        if outFile != 0:
            # We have finished a file
            outFile.close()
            uploadFile(makeName(startTime))
        startTime = time.time()
        outFile = open(makeName(startTime), "a")
        # Header line might appear mid file outFile.write("Time, Humidity, Temperature\n")

    lineList = line.split(',')
    if len(lineList) < 3:
        print line
        print 'Is too short'
        continue
    if 'OK' != lineList[0]:
        print line
        print 'Bad status'
        continue
    humid = float(lineList[1])  # Catch ValueError?
    temp = float(lineList[2])
    print 'Humidity: {0}  Temp: {1}'.format(humid,  temp)
    outFile.write('{0}, {1}, {2}\n'.format(int(time.time() * 1000), humid, temp))
    outFile.flush()

outFile.close()
inputDev.close()
