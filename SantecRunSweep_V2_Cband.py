# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pyvisa as visa

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

  
def initialize_Santec():
    #Getting resource manager
    rm = visa.ResourceManager()
    
    #printing resources list and instrument ID
    print("----------RESOURCES-------------")
    print(rm.list_resources())
    print('\n')
    my_instrument = rm.open_resource('GPIB0::1::INSTR')
    my_instrument.read_termination = '\n'
    my_instrument.write_termination = '\n'
    print("----------INSTRUMENT-------------")
    print(my_instrument.query('*IDN?'))
    print('\n')
    
    #Setting sweep state to stopped
    my_instrument.write(':WAV:SWE:MOD 0')
    print('sweep mode:'+my_instrument.query(':WAV:SWE:MOD?'))
    #Setting number of cycles to 1
    my_instrument.write(':WAV:SWE:CYCL 1')
    
    #Pinging for ESE and OPC values
    print("ESE? - "+my_instrument.query('*ESE?'))
    print("OPC? - "+my_instrument.query('*OPC?'))
    
    
    return my_instrument

def initialize_Keithley():
    #Getting resource manager
    rm = visa.ResourceManager()
    
    #printing resources list and instrument ID
    print("----------RESOURCES-------------")
    print(rm.list_resources())
    print('\n')
   
    k2400 = rm.open_resource('GPIB0::16::INSTR')
    k2400.read_termination = '\n'
    k2400.write_termination = '\n'
    
    print("----------INSTRUMENT-------------")
    print(k2400.query('*IDN?'))
    print('\n')
    
    
    
    
    #Setting current compliance limit and voltage for detection
    #Setting current compliance limit and voltage for detection
    uA=10**(-6)
    mA=10**(-3)
    CurrentLimit = 150*mA
    Voltage=0
  
    #Restoring GPIB defaults and setting status to preset
    k2400.write("*rst; status:preset;")
    #print(k2400.query(':SYST:ERR?'))
    
    #Specifying default setup parameters
    DefaultSetup = ('*ESE 1;*SRE 32;*CLS;:FUNC:CONC ON;:FUNC:ALL;'
            ':TRAC:FEED:CONT NEV;:SENS:RES:MODE MAN;')
    #*ESE 1 - enables OPC reporting
    #*SRE 32 -enables standard event bits for OPC reporting
    #*CLS - clears status
    #FUNC:CONC ON - Enables concurrent measurements
    #FUNC:ALL - enables all function readings
    #TRAC:FEED:CONT:NEV - disables data buffer
    #SENS:RES:MODE MAN - disables auto resistance

    #executing default setup
    k2400.write(DefaultSetup)
    
    #Set source to voltage, set current limit, and enable current auto range
    k2400.write('SOUR:FUNC VOLT;:SOUR:VOLT '+str(Voltage)+';'
                ':CURR:PROT '+ str(CurrentLimit) +';:CURR:RANG:AUTO ON;')
    
    #Enable display to show current reading and set sensing to current for measurement
    k2400.write('SYST:KEY 22;')
    k2400.write('SENSE:FUNC "CURR"') 

    return k2400
    


def Santec_SIMPLESWEEP(params):
    #unpacking params
    wav_resolution=params[0]
    wav_sweepstart=params[1]
    wav_sweepstop=params[2]
    Santec_instrument=params[3]
    Keithley=params[4]

    #Number of points to iterate through and record wavelength data
    points=int((wav_sweepstop-wav_sweepstart)/wav_resolution)+1
    
    #Creating data holders
    wav=[]
    volt=[]
    
    #Setting keithley output and putting santec at start wavelength
    Keithley.write(':OUTP ON;')
    Santec_instrument.write('WAV ' + str(wav_sweepstart))
    
    #giving delay for laser to settle
    time.sleep(1)
    
    #Iterating over wavelength and recording voltage
    dt=1e-6
    for i in range(points):
        Santec_instrument.write('WAV ' + str(wav_sweepstart+i*wav_resolution))
        
        #waiting for completion signal
        while (Santec_instrument.query('*OPC?')==0):
            time.sleep(dt)
        
        #recording voltage
        volt=volt+[Keithley.query_ascii_values(':READ?',delay=dt)]
        
        #waiting for completion signal
        while (Keithley.query('*OPC?')==0):
            time.sleep(dt)
        
        #recording wavelength and setting delay, may need longer delay for bigger wavelength jumps
        wav=wav+[Santec_instrument.query('WAV? ',delay=dt)]
        
        
        
    #Keithley.write(':OUTP OFF;')

   
    
    wav=[float(i) for i in wav]
    v1=np.asarray(volt)[:,0]
    v2=np.asarray(volt)[:,1]
    v3=np.asarray(volt)[:,2]
    v4=np.asarray(volt)[:,3]
    
    print(np.shape(v1))
    data=np.vstack((wav,v1,v2,v3,v4))
    
    df=pd.DataFrame(data.T,columns=['Wavelength (nm)','V1','V2','V3','V4'])
    print(df)
    
    
    # path for saved files
    directory=r'C:\semspace\Saved GC Data'

    # get filename from user
    filename = input("Enter filename: ")   
    filename = filename + ".csv"

    print(directory)
    #print(filename)

    #df.to_csv (filepath, index = False)
    df.to_csv(os.path.join(directory, filename))

    
    plt.plot(df['Wavelength (nm)'],abs(df['V2']))
    #plt.legend()
    plt.show()
    
    
def sleep_Keithley():
    #Getting resource manager
    rm = visa.ResourceManager()
   
    k2400 = rm.open_resource('GPIB0::16::INSTR')
    k2400.read_termination = '\n'
    k2400.write_termination = '\n'
    
    #Setting current compliance limit and voltage for detection
    #Setting current compliance limit and voltage for detection
    uA=10**(-6)
    mA=10**(-3)
    CurrentLimit = 150*mA
    Voltage=0
  
    #Restoring GPIB defaults and setting status to preset
    k2400.write("*rst; status:preset;")
    #print(k2400.query(':SYST:ERR?'))
    
    #Specifying default setup parameters
    DefaultSetup = ('*ESE 1;*SRE 32;*CLS;:FUNC:CONC ON;:FUNC:ALL;'
            ':TRAC:FEED:CONT NEV;:SENS:RES:MODE MAN;')
    #*ESE 1 - enables OPC reporting
    #*SRE 32 -enables standard event bits for OPC reporting
    #*CLS - clears status
    #FUNC:CONC ON - Enables concurrent measurements
    #FUNC:ALL - enables all function readings
    #TRAC:FEED:CONT:NEV - disables data buffer
    #SENS:RES:MODE MAN - disables auto resistance

    #executing default setup
    k2400.write(DefaultSetup)
    
    #Set source to voltage, set current limit, and enable current auto range
    k2400.write('SOUR:FUNC VOLT;:SOUR:VOLT '+str(Voltage)+';'
                ':CURR:PROT '+ str(CurrentLimit) +';:CURR:RANG:AUTO ON;')
    
    #Enable display to show current reading and set sensing to current for measurement
    k2400.write('SYST:KEY 22;')
    k2400.write('SENSE:FUNC "CURR"') 

    return k2400

def sleep_Santec():
    sleep_wavelength=1550
    
    #Getting resource manager
    rm = visa.ResourceManager()
    
    #printing resources list and instrument ID
    my_instrument = rm.open_resource('GPIB0::1::INSTR')
    my_instrument.read_termination = '\n'
    my_instrument.write_termination = '\n'
    
    #Setting sweep state to stopped
    my_instrument.write(':WAV:SWE:MOD 0')
    #Setting number of cycles to 1
    my_instrument.write(':WAV:SWE:CYCL 1')
    my_instrument.write('WAV ' + str(sleep_wavelength))
    

    
#--------------------------------------------------------   
#-------------------------------------------------------- 
# Beginning of Program
#--------------------------------------------------------
#--------------------------------------------------------  
    
wav_resolution=0.1 #sweep resolution in nm
wav_sweepstart=1525 #start wavelength of sweep (nm)
wav_sweepstop=1575 #stop wavelength of sweep (nm)
Keithley=initialize_Keithley() #laser instrument variable
Santec=initialize_Santec() #laser instrument variable

#Consolidating sweep parameters
sweep_params=[wav_resolution,wav_sweepstart,wav_sweepstop,Santec,Keithley]

times=1
for i in range(times):
    Santec_SIMPLESWEEP(sweep_params)

sleep_Keithley()
sleep_Santec()
exit()