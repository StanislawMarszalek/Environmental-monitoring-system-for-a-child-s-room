#!/usr/bin/env python3

import sys
from time import sleep
import sqlite3
import serial


parameters:dict[str,int]={"CO[ppm]":0,"LPG[ppm]":0,"IsTooLoud":0,"Humidity[%]":0,"Temperature[c]":0}
PARAMETERS_KEYS:list[str]=["CO[ppm]","LPG[ppm]","IsTooLoud","Humidity[%]","Temperature[c]"]


#----Preperaing serial communication-----
try:
    #opening serial for communiactions
    serialConn:serial.Serial=serial.Serial("/dev/ttyACM0",115200,timeout=7.5)

except serial.serialutil.SerialException:
    print("Cannot find the device \'/dev/ttyACM0\'")
    sys.exit(-1)

try:
    sleep(4) #a few seconds for arduino to restart and prepare serial communication
    serialConn.reset_input_buffer()
    print("Serial is ready")

except KeyboardInterrupt:
    print("\n Closing serial and programm")
    serialConn.close()
    sys.exit(-1)


try:
    while True:
        sleep(0.01)
        with sqlite3.connect("/home/nullpointer/Desktop/app/ChildRoom.db") as conn:
            cursor=conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS ENV_PARAMETERS (time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,CO INT,LPG INT,IsTooLoud INT,Humidity INT,Temperature INT);")
            if serialConn.in_waiting>0:
                data=serialConn.readline().decode("utf-8").rstrip().split("|")

                try:
                    cursor.execute("INSERT INTO ENV_PARAMETERS (CO,LPG,IsTooLoud,Humidity,Temperature) \
                                   VALUES(?,?,?,?,?)",tuple(data))

                except (sqlite3.OperationalError,sqlite3.DataError,sqlite3.ProgrammingError) as e:
                    print("Error while inserting",e)


except KeyboardInterrupt:
    print("\nClosing Serial")
    serialConn.close()
except serial.serialutil.SerialException as NoDataOrMultipleDevices:
    print("Device reports readiness to read but returned no data")
    print("\nClosing Serial")
    serialConn.close()
except OSError as NoInput:
    print("Cannot read from the device \nCheck the connection and reboot the raspberry")
    print("\nClosing Serial")
    serialConn.close()
