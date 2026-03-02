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
#headers,data=parseCSV.parseTrace(f"{cwd}{fsep}2026-03-01-00-47-03-503071838_1_45s_FRAMEWORK.csv")
headers,data=parseCSV.parseTrace(f"{cwd}{fsep}2026-03-01-00-22-54-861225650_1_45s_FRAMEWORK.csv")

#print(headers)
#print(data)
initTime=int(data[0][0])


for ack in data:
    oldRTTs.append(int(ack[3]))
    bytesAcked.append(int(ack[1]))
    oldTimes.append(int(int(ack[0]) - int(initTime)))
    #print(ack[3])
    
#print(oldRTTs)
#print(max(oldRTTs))

plt.clf()
plt.ylabel('Old RTTs')
plt.axis((1, len(oldRTTs), min(oldRTTs), max(oldRTTs)))
plt.plot(list(range(1, len(oldRTTs) + 1)), oldRTTs, 'o-', label='stuff')
#plt.ylabel('some numbers')
#plt.show()
plt.clf()


# The first RTT dosent matter!!! only the init time when the ack was recorded
perterbedTimes=oldTimes.copy()
nsecJitter=200000 # 0.2 msec
random_array = np.random.normal(center, nsecJitter, len(perterbedTimes))
pbase = 0
jitteredRTTs.append(oldRTTs[0])

# before rounding
plt.hist(random_array, bins=200)
plt.show()
plt.clf()

print(f" gotta do {len(perterbedTimes)}")
#print(f"{perterbedTimes}")

for i in range(1, len(perterbedTimes) - 1):
    thisrand=int(random_array[i])
    #print(f"1_{int(perterbedTimes[i]) + bufferTime}")
    #print(f"2_{int(int(perterbedTimes[i - 1]) + newpbase)}")
    pti = perterbedTimes[i] + pbase + thisrand
    ptim1 = perterbedTimes[i - 1]
    #print(f"{pti-ptim1}")
    a=int(pti)
    b=int(ptim1)
    while a < b:
        # Update rand so its not having a packet sent before the last was
        #  acked
        thisrand = np.random.normal(center, nsecJitter, 1)[0]
        # Update the random array to track our changes to the distribution
        random_array[i] = thisrand
        pti = perterbedTimes[i] + pbase + thisrand
        a=int(pti)
    #print("Pass")
    #print(newpbase - pbase < 0)
    pbase = pbase + thisrand
    perterbedTimes[i] = int(perterbedTimes[i]) + pbase
    jitteredRTTs.append(int(oldRTTs[i]) + random_array[i])

print("Its plotting time")
plt.title('Old timeline vs Old RTT computed timeline')
print(min(min(perterbedTimes), min(oldTimes)))
print(max(max(perterbedTimes), max(oldTimes)))
plt.axis((1, len(perterbedTimes), min(min(perterbedTimes), min(oldTimes)), max(max(perterbedTimes), max(oldTimes))))
plt.plot(list(range(1, len(perterbedTimes) + 1)), perterbedTimes, color='red', marker=',', label='stuff')
plt.plot(list(range(1, len(oldTimes) + 1)), oldTimes, color='green', marker=',', label='stuff')
#plt.ylabel('some numbers')
plt.show()
plt.clf()

plt.hist(random_array, bins=200)
plt.show()
plt.clf()

for rtt in oldRTTs:
    jitteredRTTS = []


