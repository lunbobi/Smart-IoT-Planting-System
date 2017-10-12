#This is the file executing while STM32 MCU bootup, and in this file,  
#it will call other functions to fullfill the project.
#Communication module: LoRa.
#Communication method with gateway via LoRa.
#Uart port drive LoRa module.
#Parse JSON between device and gateway via LoRa channel.
#LoRa module: E32-TTL-100
#Pin specification:
#Module         MCU
#M0(IN)    <--> GPIO(X3)(OUT)     #mode setting, can not hang
#M1(IN)    <--> GPIO(X4)(OUT)     #mode setting, can not hang
#RXD(IN)   <--> X1(TX)(OUT)   #UART4
#TXD(OUT)  <--> X2(RX)(IN)    #UART4
#AUX(OUT)  <--> GPIO/INT(IN)  #module status detecting
#VCC
#GND
#Communication mode is 0, need to set M0 and M1 to 0.

import pyb
from pyb import Pin
from pyb import Timer
from pyb import UART  
import micropython
import irrigate
#Import light intensity needed module 
import LightIntensity
import time
import json

micropython.alloc_emergency_exception_buf(100)

Pin('Y11',Pin.OUT_PP).low() #GND
Pin('Y9',Pin.OUT_PP).high() #VCC

#Set LoRa module with mode-0.
M0 = Pin('X3', Pin.OUT_PP)
M1 = Pin('X4', Pin.OUT_PP)
M0.low()
M1.low()
#Init uart4 for LoRa module.
u4 = UART(4,9600)  
u4.init(9600, bits=8, parity=None, stop=1)  
cmd_online = '{"ID":"1", "CMD":"Online", "TYPE":"N", "VALUE":"N"}\n'
#Send Online command to gateway while it power on to obtain its status data from gateway's database.
u4.write(cmd_online)

#LED shining regularly(using timer) to indicate the program is running correctly
tim1 = Timer(1, freq=1)
tim1.callback(lambda t: pyb.LED(1).toggle())

 
#Read the light intensity value from sensor regularly.

lightVlaue = 0
#time2 callback function, obtain value from light intensity sensor and send it to gateway via LoRa module.
def getLightInten():
  global lightValue
  lightValue = LightIntensity.readLight()
  #print(lightValue)
  u4.write('{"ID":"1", "CMD":"ENV", "TYPE":"light", "VALUE":"+lightValue+"}\n')
	
'''
#Get soil moisture and send it to gateway, if the current value is lower than standard, gateway
#will send 'irrigate' command to device, device will control steering engine to open the tap and water the plants.
def moisture():
  global moisture
  moisture = moisture.readMoisture()
  u4.write('{"ID":"1", "CMD":"ENV", "TYPE":"moisture", "VALUE":"+moisture+"}\n')
'''	

tim2 = Timer(2, freq=1)
tim2.callback(getLightInten())

if __name__=='__main__':
  while True:
    #Waiting for the message from UART4 to obtain LoRa data.
    len = u4.any()
    if(len > 0): 
      recv = u4.read()
      print(recv)
      json_lora = json.loads(recv)
      #Parse JSON from gateway.
      if (json_lora.get("CMD") == 'Online' and json_lora.get("TYPE") == 'Light2' ): #Control the light(led on TPYBoard)
        if json_lora.get("VALUE") == 'On':
          pyb.LED(2).on()
        else:
          pyb.LED(2).off()
      elif json_lora.get("CMD") == 'irrigate': # irrigate the plants
        if json_lora.get("VALUE") == 'Open':
          irrigate.irrigate_start()
        else:
          irrigate.irrigate_stop()
	#print(LightIntensity.readLight())