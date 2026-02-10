import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import parseCSV

def main():
    desc = '''
    Takes in a trace file and graphs rtt over time and bytes ACKed over time
    '''
    parser =argparse.ArgumentParser(prog=os.path.basename(__file__),description=desc)
    parser.add_argument('fileName',type=str)
    args = parser.parse_args()
    
    
    
    headers,data=parseCSV.parseTrace(args.fileName)

    getRows = ["now_us",'bytes_acked',"rtt_us"]
    cleaned = parseCSV.getRelevant(getRows,headers,data)
    
    # cleaner
    m:dict[str,np._ArrayNumber_co] =dict()# list(map(lambda x,y: (x,y) ,getRows,cleaned))
    for row in range(len( getRows)):
        # m[getRows[row]] = np.array()
        temp = []
        for i in range(len(cleaned)):
            temp.append(cleaned[i][row])
        m[getRows[row]] = np.array(temp)
    
    m["now_us"] = np.vectorize(lambda x: float(x)/1000000)(m["now_us"])
    # print(m["now_us"])

    plt.suptitle(args.fileName,fontsize=12)
    
    plt.subplot(3,1,1)
    plt.plot(m["now_us"],m["rtt_us"])
    plt.xlabel("Time (us)")
    plt.ylabel("RTT (us)")
    plt.title("RTT")
    plt.grid()

    plt.subplot(3,1,2)
    
    plt.plot(m["now_us"],m["bytes_acked"])
    plt.xlabel("Time (us)")
    plt.ylabel("Bytes ACKed")
    plt.title("Throughput")
    # plt.grid()

    #To double check that nothing got reordered
    # plt.subplot(3,1,3)
    # xx = []
    # prev = -1
    # for i in list(map(lambda x: x[0], enumerate(m["now_us"]))):
    #     xx.append(i-prev)
    #     prev = i
    # plt.plot(xx)



    plt.tight_layout()


    origName=str(os.path.basename(args.fileName))
    dirname = os.path.dirname(args.fileName)
    if(dirname):
        dirname += os.sep
        dirname = "jitterOutputImages"+os.sep+dirname
    os.makedirs(dirname,exist_ok=True)
    outFileName = f'{dirname}{origName}.png'
    # print(outFileName)
    plt.savefig(outFileName,bbox_inches='tight')
    
    # plt.show(block=False)
    


if __name__ == '__main__':
    main()