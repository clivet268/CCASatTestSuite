#!/usr/bin/bash
from datetime import datetime
import random as rand
import os
import argparse
import parseCSV
from parseCSV import numberType


roundTripTimeIndex=1
accumulatedTimeIndex=0

def avg(trace:list[tuple[numberType,numberType]]) -> tuple[numberType,numberType]:
    sum1 = 0
    sum2 = 0
    for i in trace:
        sum1 += i[0]
        sum2 += i[1]
    return (numberType(sum1/len(trace)),numberType(sum2/len(trace)))

def applyJitter(prev:tuple[numberType,numberType]|None, cur:tuple[numberType,numberType],span:numberType):
    timeToAdd=numberType(((rand.random()*2)-1)*span)
    #start
    if(prev==None):
        return (cur[accumulatedTimeIndex],cur[roundTripTimeIndex]+timeToAdd)
    diff = (cur[accumulatedTimeIndex]+timeToAdd-prev[accumulatedTimeIndex])
    orderingFix:list[numberType] = [0]*2
    #clamp
    if(diff<0):
        timeBetweenPacketBuffer = 18 # i got 18 microseconds
        orderingFix[accumulatedTimeIndex]=prev[accumulatedTimeIndex] + timeBetweenPacketBuffer
        time = orderingFix[accumulatedTimeIndex] - cur[accumulatedTimeIndex]
        orderingFix[roundTripTimeIndex]=cur[roundTripTimeIndex] + time # compute min 1gb/s and add here
        # orderingFix[accumulatedTimeIndex]=orderingFix[roundTripTimeIndex]-cur[roundTripTimeIndex] 
    # noIssue
    else:
        orderingFix[roundTripTimeIndex]=cur[roundTripTimeIndex]+timeToAdd
        orderingFix[accumulatedTimeIndex]=cur[accumulatedTimeIndex]+timeToAdd
    return (orderingFix[0],orderingFix[1])

def jitter(trace:list[tuple[numberType,numberType]],amount:float,useAmountAsTime:bool=False):
    outList:list[tuple[numberType,numberType]] = []
    mean:tuple[numberType,numberType] = avg(trace)
    span:numberType = numberType((mean[roundTripTimeIndex] if not useAmountAsTime else 1 )*amount)
    print(span)
    outList.append( applyJitter(None,trace[0],span))
    for i in range(1,len(trace)):
        outList.append( applyJitter(outList[i-1],trace[i],span))
    return outList


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
    getRows = ["now_us","rtt_us"]
    cleaned = parseCSV.getRelevant(getRows,headers,data)
    # print(cleaned)
    jittered = jitter(list(map(lambda x :  (x[0],x[1]),cleaned)),args.jitterAmount,args.M)
    origName=str(os.path.basename(args.fileName)).split('.')
    dirname = os.path.dirname(args.fileName)
    if(dirname):
        dirname += os.sep
        dirname = "jitterOutput"+os.sep+dirname
    os.makedirs(dirname,exist_ok=True)
    outFileName = f'{dirname}{origName[0]}-jitter_{args.jitterAmount}{"-MS" if args.M else ""}{f".{origName[-1]}" if len(origName)>1 else ".trace"}'
    # print(outFileName)
    parseCSV.writeNew(outFileName,list(map(lambda x :  list(x),jittered)),getRows,headers,data)


if __name__ == '__main__':
    main()
