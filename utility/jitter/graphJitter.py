
import os
import argparse
import parseCSV
from parseCSV import numberType

roundTripTimeIndex=1
accumulatedTimeIndex=0



def main():
    desc = '''
    Takes in a trace file and graphs rtt over time and bytes ACKed over time
    '''
    parser =argparse.ArgumentParser(prog=os.path.basename(__file__),description=desc)
    parser.add_argument('fileName',type=str)
    args = parser.parse_args()
    
    
    origName=str(os.path.basename(args.fileName))
    dirname = os.path.dirname(args.fileName)
    if(dirname):
        dirname += os.sep
        dirname = "jitterOutputImages"+os.sep+dirname
    os.makedirs(dirname,exist_ok=True)
    outFileName = f'{dirname}{origName}.png'

    if(os.path.exists(outFileName) and os.path.getmtime(outFileName) > os.path.getmtime(args.fileName)):
        print(f"\tSkipped: {outFileName} is newer than source file")
        exit(0)
    import matplotlib.pyplot as plt
    import numpy as np

    def calcInterpacketTime(t:list[tuple[numberType,numberType]]) -> list[numberType]:
        outlist = [numberType(0)]
        for i in range(1,len(t)):
            diff = t[i][accumulatedTimeIndex]-t[i-1][accumulatedTimeIndex]
            outlist.append(diff)
        return outlist

    def graph(fiilename):
        headers,data=parseCSV.parseTrace(fiilename)

        getRows = ["now_us",'bytes_acked',"rtt_us"]
        cleaned = parseCSV.getRelevant(getRows,headers,data)
        jrtt =calcInterpacketTime([(numberType(j[0]),numberType(j[2])) for j in cleaned])
        
        # cleaner
        m:dict[str,np._ArrayNumber_co] =dict()# list(map(lambda x,y: (x,y) ,getRows,cleaned))
        for row in range(len( getRows)):
            # m[getRows[row]] = np.array()
            temp = []
            for i in range(len(cleaned)):
                temp.append(cleaned[i][row])
            m[getRows[row]] = np.array(temp)
        
        m["now_us"] = np.vectorize(lambda x: float(x)/1000000)(m["now_us"])
        m["rtt_us"] = np.vectorize(lambda x: float(x)/1000000)(m["rtt_us"])
        # print(m["now_us"])

        plt.suptitle(fiilename,fontsize=12)
        
        plt.subplot(3,1,1)
        plt.plot(m["now_us"],m["rtt_us"])
        plt.xlabel("Time (s)")
        plt.ylabel("RTT (s)")
        plt.title("RTT")
        plt.ylim(bottom=0)
        plt.xlim(left=0)
        plt.grid()

        plt.subplot(3,1,2)
        
        plt.plot(m["now_us"],m["bytes_acked"])
        plt.xlabel("Time (s)")
        plt.ylabel("Bytes ACKed")
        plt.title("Throughput")
        plt.ylim(bottom=0)
        plt.xlim(left=0)

        plt.subplot(3,1,3)
        plt.plot(m["now_us"],jrtt)
        plt.xlabel("Time (s)")
        plt.ylabel("InterArrival Time (us)")
        plt.title("Inter-Packet Arrival")
        plt.ylim(bottom=0)
        plt.xlim(left=0)
    
    graph(args.fileName)
    graph(args.fileName2)


    plt.tight_layout()


    
    # print(outFileName)
    plt.savefig(outFileName,bbox_inches='tight')
    
    # plt.show(block=False)
    


if __name__ == '__main__':
    main()