import os
import matplotlib.pyplot as plt

#filepath="/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/2025-11-11_307677302/2025-11-11_307677302_1.log"
filepath=os.getcwd()
testlogsdir=f"{filepath}/testlogs/"
outputdir=f"{filepath}/output/"
frameworkdir=f"{outputdir}/framwork/"
tracelengthfilter=3

csvheader="now_us,bytes_acked,mss,rtt_us,tp_deliver_rate,tp_interval,tp_delivered,lost_pkt,total_retrans_pkt,app_limited,snd_nxt,sk_pacing_rate"

#outputfilepath="framework.csv"


def processalllogs():
    
    #for (root,dirs,files) in os.walk("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/.",topdown=True):
    for dirs in os.listdir(testlogsdir):
        print("%s\n"%dirs)
        if not os.path.exists(f"{outputdir}{dirs}"):
            os.makedirs(outputdir + dirs)
        if not os.path.exists(f"{frameworkdir}{dirs}"):
            os.makedirs(frameworkdir + dirs)
        for log in os.listdir(f"{testlogsdir}{dirs}"):
            print("%s"%log)
            processlog(f"{dirs}/{log}")
        
def processlog(logfilepath):
    try:
        with open(f"{testlogsdir}{logfilepath}", "r") as inputfile:
            flows = {}
            for line in inputfile:
                # remove "]" at end
                line = line[:-2]
                # remove "[  " auto put in by kernel
                line = line[3:]
                pieces = line.split('] [')
                #TODO no magic number
                if len(pieces) == 6:
                    if pieces[1] == "CCRG":
                        if pieces[2] == "FP":
                            if not pieces[3] in flows:
                                flows[pieces[3]] = []
                            flows[pieces[3]].append((pieces[4], pieces[5].split(',')))
                            print(f"{pieces[3]}")
                            print(f"{flows[pieces[3]]}")
                            #if pieces[4] == "FRAMEWORK":
                                #outputfile.write(pieces[5]+"\n")
            for flowpointer in flows.keys():
                print(f"{flowpointer}")
                curflow = flows.get(flowpointer)
                if len(flows.get(flowpointer)) <= tracelengthfilter:
                    print(f"Shorter than length filter of {tracelengthfilter}, skipping")
                    continue
                else:
                    frameworkfilepath=f"{frameworkdir}{logfilepath[:-4]}_framework.csv"
                    print(f"Writing to {frameworkfilepath}\n")
                    with open(frameworkfilepath, "w+") as outputfile:
                        outputfile.write(csvheader + "\n")
                        for line in curflow:
                            linetype, values = line
                            if linetype == "FRAMEWORK":
                                outputfile.write(",".join(values) + "\n")
    
        
            
    except FileExistsError:
        print(f"{outputfilepath} already exists")
    #except FileNotFoundError:
    #    print("Cannot find file " + logfilepath)
    
processalllogs()
