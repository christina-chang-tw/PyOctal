# -*- coding: utf-8 -*-
# Python 3.5

import time
import win32com.client # requires "pip install pypiwin32"
import matplotlib.pyplot as plt # requires "pip install matplotlib"
import numpy

#Settings
configuration = "C:\\Users\\Public\\Documents\\\
Photonic Application Suite\\AgEngineIL.agconfig"
#print (configuration)

EngineMgr = win32com.client.Dispatch("AgServerIL.EngineMgr")
Engine = EngineMgr.NewEngine()
Engine.LoadConfiguration(configuration)
Engine.Activate()
activating = 0
while activating == 0:
    time.sleep(0.5) 
    activating = Engine.Active
Engine.StartMeasurement()
busy = 1
while busy == 1:
    time.sleep(0.1)
    busy = Engine.Busy
IOMRFile = Engine.MeasurementResult

namelist = IOMRFile.GraphNames
IOMRGraph = IOMRFile.Graph("RXTXAvgIL")
YData = IOMRGraph.YData
noChannels = IOMRGraph.noChannels
dataPerCurve = IOMRGraph.dataPerCurve

XStart = IOMRGraph.XStart
XStep = IOMRGraph.XStep
XData = []

for i in range(dataPerCurve):
    lastX = XStart + i * XStep
    XData.append(lastX)
    
XData = tuple(numpy.divide(XData, 1e-9))
    
for i in range(noChannels):
    YCurve = tuple(numpy.negative(YData[i*dataPerCurve:(i+1)*dataPerCurve]))
    plt.plot(XData, YCurve)

plt.xlabel('wavelength (nm)')
plt.ylabel('Insertion Loss (dB)')
plt.title('IL Plot')
plt.grid(True)
#plt.savefig("test.png")
plt.show()


Engine.Deactivate
del Engine
del EngineMgr

    