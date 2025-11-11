import os
import matplotlib.pyplot as plt

#filepath="/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/2025-11-11_307677302/2025-11-11_307677302_1.log"

csvheader="now_us,bytes_acked,mss,rtt_us,tp_deliver_rate,tp_interval,tp_delivered,lost_pkt,total_retrans_pkt,app_limited,snd_nxt,sk_pacing_rate"

#outputfilepath="framework.csv"


def processalllogs():
    
    #for (root,dirs,files) in os.walk("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/.",topdown=True):
    for dirs in os.listdir("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/"):
        print("%s\n"%dirs)
        if not os.path.exists("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/output/" + dirs):
            os.makedirs("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/output/" + dirs)
        for log in os.listdir("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/" + dirs):
            print("%s"%log)
            processlog(f"{dirs}/{log}")
        
def processlog(logfilepath):
    try:
        outputfilepath=f"/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/output/{logfilepath[:-4]}_framework.csv"
        with open(outputfilepath, "w+") as outputfile:
            outputfile.write(csvheader + "\n")
            print(f"Writing to {outputfilepath}\n")
    
            outputlines=[]
        
            with open(f"/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/{logfilepath}", "r") as inputfile:
                for line in inputfile:
                    line = line[:-2]
                    line = line[3:]
                    pieces = line.split('] [')
                    if len(pieces) == 6:
                        if pieces[1] == "CCRG":
                            flows = {}
                            if pieces[2] == "FP":
                                flows.setdefault(f"{pieces[3]}", []).append((pieces[4], pieces[5].split(',')))
                                if pieces[4] == "FRAMEWORK":
                                    outputfile.write(pieces[5]+"\n")
                    
    except FileExistsError:
        print(f"{outputfilepath} already exists")
    #except FileNotFoundError:
    #    print("Cannot find file " + logfilepath)
    
processalllogs()
