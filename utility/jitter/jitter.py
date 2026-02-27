#!/usr/bin/bash
from datetime import datetime
import random as rand
import os
import argparse
import parseCSV
from parseCSV import numberType


appLimitedIndex=2
roundTripTimeIndex=1
accumulatedTimeIndex=0
minTime = 18

def calcInterpacketTime(t:list[tuple[numberType,numberType]]) -> list[numberType]:
    outlist = [numberType(0)]
    for i in range(1,len(t)):
        diff = t[i][accumulatedTimeIndex]-t[i-1][accumulatedTimeIndex]
        outlist.append(diff)
    return outlist
def calcSentTime(t:list[tuple[numberType,numberType]]) -> list[numberType]:
    outlist = []
    for i in range(0,len(t)):
        diff = t[i][accumulatedTimeIndex]-t[i][roundTripTimeIndex]
        outlist.append(diff)
    return outlist
def calcSentInterpacketTime(t:list[tuple[numberType,numberType]]) -> list[numberType]:
    sent_times = calcSentTime(t)
    outlist = [numberType(0)]
    for i in range(1, len(sent_times)):
        diff = sent_times[i] - sent_times[i-1]
        outlist.append(diff)
    return outlist



def avg(trace:list[tuple[numberType,numberType]]) -> tuple[numberType,numberType]:
    sum1 = 0
    sum2 = 0
    for i in trace:
        sum1 += i[0]
        sum2 += i[1]
    return (numberType(sum1/len(trace)),numberType(sum2/len(trace)))


def applyJitter(prev:tuple[numberType,numberType,bool]|None, cur:tuple[numberType,numberType,bool],srcPrev:tuple[numberType,numberType,bool]|None,span:numberType)->tuple[numberType,numberType,bool]:
    timeToAdd=numberType(((rand.random()*2)-1)*span/2)
    # timeToAdd=numberType(((rand.normalvariate())*span/2))
    #start
    if(prev==None):
        return (cur[accumulatedTimeIndex]+timeToAdd,cur[roundTripTimeIndex]+timeToAdd,bool(cur[appLimitedIndex]))
    diff = (cur[accumulatedTimeIndex]+timeToAdd-prev[accumulatedTimeIndex])
    orderingFix:list[numberType] = [0]*2
    #clamp
    if(diff<minTime):
        timeBetweenPacketBuffer = minTime # i got 18 microseconds
        orderingFix[accumulatedTimeIndex]=prev[accumulatedTimeIndex] + timeBetweenPacketBuffer
        time = orderingFix[accumulatedTimeIndex] - cur[accumulatedTimeIndex]
        orderingFix[roundTripTimeIndex]=max(cur[roundTripTimeIndex] + time,timeBetweenPacketBuffer) # compute min 1gb/s and add here
    # noIssue
    else:
        orderingFix[roundTripTimeIndex]=cur[roundTripTimeIndex]+timeToAdd
        orderingFix[accumulatedTimeIndex]=max(cur[accumulatedTimeIndex]+timeToAdd,minTime)
    return (orderingFix[0],orderingFix[1],bool(cur[appLimitedIndex]))
        
def applyJitter2(prev:tuple[numberType,numberType,bool]|None, cur:tuple[numberType,numberType,bool],srcPrev:tuple[numberType,numberType,bool]|None,span:numberType)->tuple[numberType,numberType,bool]:
    timeToAdd=numberType(((rand.random()*2)-1)*span)
    if(cur[roundTripTimeIndex]+timeToAdd < 0):
        timeToAdd = 0
    if(cur[appLimitedIndex]): # preserve time sent
        #start
        if(prev==None):
            return (cur[accumulatedTimeIndex],cur[roundTripTimeIndex]+timeToAdd,bool(cur[appLimitedIndex]))
        
        diff = (cur[accumulatedTimeIndex]+timeToAdd-prev[accumulatedTimeIndex])
        output:list[numberType] = [0]*2
        # clamp
        if(diff<0):
            timeBetweenPacketBuffer = minTime # i got 18 microseconds
            output[accumulatedTimeIndex]=prev[accumulatedTimeIndex] + timeBetweenPacketBuffer
            time = output[accumulatedTimeIndex]-cur[accumulatedTimeIndex]
            output[roundTripTimeIndex]=cur[roundTripTimeIndex] + time # compute min 1gb/s and add here

        # noIssue
        else:
            output[roundTripTimeIndex]=cur[roundTripTimeIndex]+timeToAdd
            output[accumulatedTimeIndex]=cur[accumulatedTimeIndex]+timeToAdd
    
        return (output[0],output[1],bool(cur[appLimitedIndex]))
    else:
        output:list[numberType] = [0]*2
        if(prev==None or srcPrev ==None):
            return (cur[accumulatedTimeIndex],cur[roundTripTimeIndex]+timeToAdd,bool(cur[appLimitedIndex]))

        srcPrevSendTime = srcPrev[accumulatedTimeIndex]-srcPrev[roundTripTimeIndex]
        curSendTime = cur[accumulatedTimeIndex]-cur[roundTripTimeIndex]
        prevSentTime = prev[accumulatedTimeIndex]-prev[roundTripTimeIndex]

        if(srcPrev[accumulatedTimeIndex]<curSendTime): # if cur was sent after prev was received, keep that proterty

            output[roundTripTimeIndex]=max(cur[roundTripTimeIndex]+timeToAdd,minTime)

            output[accumulatedTimeIndex] = prev[accumulatedTimeIndex]+ (curSendTime-srcPrevSendTime) + output[roundTripTimeIndex]

            assert((output[accumulatedTimeIndex]-output[roundTripTimeIndex])-(prevSentTime)>0)

        else:   # else, keep being set after prev and keep acked after prev, -- cur sent before prev received

            minRTT = (prev[accumulatedTimeIndex ] - ((prevSentTime) + (curSendTime-srcPrevSendTime))) + minTime # acked after prev
            # minRTT =18


            output[roundTripTimeIndex]=max(cur[roundTripTimeIndex]+timeToAdd,minRTT)

            output[accumulatedTimeIndex] = (prevSentTime) + (curSendTime-srcPrevSendTime) +  output[roundTripTimeIndex]

            try:
                assert((output[accumulatedTimeIndex])>(prev[accumulatedTimeIndex])>0)
            except:
                print(output, prev, cur, srcPrev)
            pass


        return (output[0],output[1],bool(cur[appLimitedIndex]))



def jitter(trace:list[tuple[numberType,numberType,bool]],amount:float,useAmountAsTime:bool=False):
    outList:list[tuple[numberType,numberType,bool]] = []
    mean:tuple[numberType,numberType] = avg([(x[:2]) for x in trace])
    span:numberType = numberType((mean[roundTripTimeIndex] if not useAmountAsTime else 1 )*amount)
    print(span)
    outList.append( applyJitter(None,trace[0],None,span))
    for i in range(1,len(trace)):
        outList.append( applyJitter(outList[i-1],trace[i],trace[i-1],span))
    t = outList[0][accumulatedTimeIndex]
    return [(numberType(x[0]-t),numberType(x[1]),numberType(x[2])) for x in outList]


def test():
    def reseed():
        rand.seed(42)
    reseed()
    def genSimpleTrace(n:int,gap:numberType):
        outList = []
        orderingFix =[0]*2
        orderingFix[accumulatedTimeIndex]=0
        orderingFix[roundTripTimeIndex]=0
        outList.append((orderingFix[0],orderingFix[1]))
        for i in range(1,n):
            orderingFix[accumulatedTimeIndex]=i*gap
            orderingFix[roundTripTimeIndex]=gap
            outList.append((orderingFix[0],orderingFix[1]))
        return outList
    
    a = genSimpleTrace(20,100)
    print()
    print("Source\n",a)



    print()
    b = jitter(a,0)
    print("Control\n",b)
    print()


    reseed()
    c = jitter(a,1.5)
    print()
    print("\nUsing avg instead")
    print("AccTime\n",list(map(lambda x: x[accumulatedTimeIndex],c)))
    print()
    print("DiffTime\n",list(map(lambda x: x[roundTripTimeIndex],c)))
    print("\nUsing MS instead")
    
    
    reseed()
    print()
    d = jitter(a,1.5,True)
    print()
    print("AccTime\n",list(map(lambda x: x[accumulatedTimeIndex],d)))
    print()
    print("DiffTime\n",list(map(lambda x: x[roundTripTimeIndex],d)))
    

    pass



def main():
    desc = '''
    Takes in a trace file and applies jitter to the packet timings. By default jitter is based on the average inter-packet arrival time of the trace. 

    The amount of jitter per packet is a random value from 0 to jitterAmount * mean or, if -M is set, 0 to jitterAmount.
    '''
    parser =argparse.ArgumentParser(prog=os.path.basename(__file__),description=desc)
    parser.add_argument('-M',action='store_true',help="Interprets jitterAmount as a time")
    parser.add_argument('fileName',type=str)
    parser.add_argument('jitterAmount',type=float,help="A percent (with 1 as 100%%) of the average inter-packet arrival time to jitter by")
    args = parser.parse_args()
    
    rand.seed(datetime.now().timestamp())
    
    headers,data=parseCSV.parseTrace(args.fileName)
    # print(headers,data)
    getRows = ["now_us","rtt_us","app_limited"]
    cleaned = parseCSV.getRelevant(getRows,headers,data)

    formatCleaned = list(map(lambda x :  (x[0],x[1],bool(x[2])),cleaned))
    # print(cleaned)
    jittered = jitter(formatCleaned,args.jitterAmount,args.M)
    origName=str(os.path.basename(args.fileName)).split('.')
    dirname = os.path.dirname(args.fileName)

    # validrate order preserved
    preserved = True
    failIndex = -1
    for i in range(1,len(jittered)):
        if jittered[i][accumulatedTimeIndex] < jittered[i-1][accumulatedTimeIndex] + minTime:
            failIndex = i
            preserved = False
            break
    
    if(not preserved):
        print("Something went wrong and could not preserve packet order at " + str(failIndex))
        # exit(0)


    if(dirname):
        dirname += os.sep
        dirname = "jitterOutput"+os.sep+dirname
    os.makedirs(dirname,exist_ok=True)
    outFileName = f'{dirname}{origName[0]}-jitter_{args.jitterAmount}{"-MS" if args.M else ""}{f".{origName[-1]}" if len(origName)>1 else ".trace"}'
    # print(outFileName)
    parseCSV.writeNew(outFileName,list(map(lambda x :  list(x),jittered)),getRows,headers,data)


if __name__ == '__main__':
    main()
