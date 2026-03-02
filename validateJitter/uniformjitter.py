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
oldRTTBasedTimes=[]
jitteredRTTs=[]
jitteredRTTBasedTimes=[]
bytesAcked=[]
bufferTime=14000000 # 14 msec according to it

cwd=os.getcwd()
fsep=os.sep
#print(fsep)
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
nsecJitter=200000000 # 0.2 msec
random_array = np.random.normal(center, nsecJitter, len(perterbedTimes))
# before rounding
plt.hist(random_array, bins=400)
plt.show()
plt.clf()
random_array2=random_array.copy()

print(f" gotta do {len(perterbedTimes)}")
#print(f"{perterbedTimes}")
# First rtt dosent matter, it already happend
#jitteredRTTs.append(oldRTTs[0])
for i in range(1, len(perterbedTimes)):
    deltaack = max(perterbedTimes[i] - perterbedTimes[i - 1], 0)
    # Perterb with the stddev being the current delta
    randomval = (np.random.normal(center, deltaack * 10, 1)[0])
    ## CHANGE THIS TO DEMONSTRATE THE CHANGE
    xchange=abs(randomval/100000000)
    xdim=1.0
    randomval = int(randomval / xdim) - (abs(randomval) * xchange)
    #randomval = 0
    origindeltaack = deltaack
    deltaack = deltaack + randomval
    if(max(perterbedTimes[i - 1], deltaack) - perterbedTimes[i -1] > 0):
        print(f"{i}  {max(perterbedTimes[i - 1], deltaack) - perterbedTimes[i -1]}")
        print(f"{i}  {deltaack} {perterbedTimes[i -1]}")
        
    jitteredRTTs.append(max(perterbedTimes[i - 1], deltaack) - perterbedTimes[i -1])
    perterbedTimes[i] = max(perterbedTimes[i - 1], perterbedTimes[i - 1] + deltaack)
    random_array2[i] = randomval
    random_array[i] = perterbedTimes[i] - origindeltaack

jitteredRTTs.append(jitteredRTTs[-1])
print("Its plotting time")
plt.title('Old timeline vs Jittered computed timeline')
print(min(min(perterbedTimes), min(oldTimes)))
print(max(max(perterbedTimes), max(oldTimes)))
plt.axis((1, len(perterbedTimes), min(min(perterbedTimes), min(oldTimes)), max(max(perterbedTimes), max(oldTimes))))
plt.plot(list(range(1, len(perterbedTimes) + 1)), perterbedTimes, color='red', marker=',', label='stuff')
plt.plot(list(range(1, len(oldTimes) + 1)), oldTimes, color='green', marker=',', label='stuff')
#plt.ylabel('some numbers')
plt.show()
plt.clf()


plt.hist(random_array2, bins=400)
plt.show()
plt.clf()

plt.hist(random_array, bins=400)
plt.show()
plt.clf()

print("Its rttplot time")
print(max(jitteredRTTs[2:]))
plt.title('Old timeline vs Old RTT computed timeline')
print(min(min(oldRTTs[:-2]), min(jitteredRTTs[2:])))
print(max(max(oldRTTs[:-2]), max(jitteredRTTs[2:])))
plt.axis((1, len(oldRTTs), min(min(jitteredRTTs), min(oldRTTs)), max(max(jitteredRTTs[10:]), max(oldRTTs[:-2]))))
plt.plot(list(range(11, len(jitteredRTTs) + 1)), jitteredRTTs[10:], color='red', marker=',', label='stuff')
plt.plot(list(range(1, len(oldRTTs) + 1)), oldRTTs, color='green', marker=',', label='stuff')
#plt.ylabel('some numbers')
plt.show()
plt.clf()

