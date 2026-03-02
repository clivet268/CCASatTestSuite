import numpy as np
import matplotlib.pyplot as plt
import parseCSV
from parseCSV import numberType
import os
times=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
maxd=400.0
center=0.0
numvalues=10000
numbuckets=100
random_array = np.random.normal(center, 100.0, numvalues)

# Graphs are bytes vs time or for rtts just nth rtt sample
# RTT based timeline is just old 
# For the jittered timeline, ignore old timestamps, just use rtts
# Graph just old rtts based timeline vs old timeline for verification
# Graph old rtts vs jittered rtts
# Graph old rtts based timeline vs jittered based timeline

initTime=0
oldTimes=[]
#oldRTTs=[0,1,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5,2,3,4,5]
oldRTTs=[]
oldRTTBasedTimes=[268]
jitteredRTTs=[]
jitteredRTTBasedTimes=[]
bytesAcked=[]
bufferTime=14000000 # 14 msec according to it

cwd=os.getcwd()
fsep=os.sep
print(fsep)
headers,data=parseCSV.parseTrace(f"{cwd}{fsep}2026-03-01-00-47-03-503071838_1_45s_FRAMEWORK.csv")
headers,data=parseCSV.parseTrace(f"{cwd}{fsep}log_data_testframework1.csv")

#print(headers)
#print(data)
initTime=data[0][0]


for ack in data:
    oldRTTs.append(int(ack[3]))
    bytesAcked.append(int(ack[1]))
    oldTimes.append(int(ack[0]))
    #print(ack[3])
    
#print(oldRTTs)
#print(max(oldRTTs))

plt.clf()
plt.ylabel('Old RTTs')
plt.axis((1, len(oldRTTs), min(oldRTTs), max(oldRTTs)))
plt.plot(list(range(1, len(oldRTTs) + 1)), oldRTTs, 'o-', label='stuff')
#plt.ylabel('some numbers')
plt.show()
plt.clf()


# The first RTT dosent matter!!! only the init time when the ack was recorded
perterbedTimes=oldTimes
nsecJitter=1000000 # 1 msec
random_array = np.random.normal(center, nsecJitter, len(perterbedTimes))

for i in range(1, len(perterbedTimes)):
    newpbase = pbase + int(random_array[i])
    while (perterbedTimes[i] + bufferTime) < (perterbedTimes + newpbase):
        newpbase = pbase + np.random.normal(center, nsecJitter, 1)
    perterbedTimes[i] = perterbedTimes + pbase
    jitteredRTTs.append(int(oldRTTs) + random_array[i])
    
plt.title('Old timeline vs Old RTT computed timeline')
print(type(oldRTTBasedTimes[0]))
print(type(min(oldRTTBasedTimes)))
plt.axis((1, len(oldRTTBasedTimes), min(min(perterbedTimes), min(oldTimes)), max(max(perterbedTimes), max(oldTimes))))
plt.plot(list(range(1, len(oldRTTBasedTimes) + 1)), oldRTTBasedTimes, color='red', marker='o', label='stuff')
plt.plot(list(range(1, len(oldTimes) + 1)), oldTimes, color='green', marker='o', label='stuff')
#plt.ylabel('some numbers')
plt.show()
plt.clf()

'''
random_array = np.random.normal(center, 100.0, len(oldRTTs))
plt.hist(random_array, bins=200)
plt.show()

for rtt in oldRTTs:
    jitteredRTTS = []

'''
