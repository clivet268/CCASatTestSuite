import os
import matplotlib.pyplot as plt
import argparse

#filepath="/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/2025-11-11_307677302/2025-11-11_307677302_1.log"
filepath=os.getcwd()
testlogsdir=f"{filepath}/testlogs/"
outputdir=f"{filepath}/output/"
frameworkdir=f"{outputdir}/framework/"
tracelengthfilter=60
desiredparsedlogs=["FRAMEWORK"]

csvheader="now_us,bytes_acked,mss,rtt_us,tp_deliver_rate,tp_interval,tp_delivered,lost_pkt,total_retrans_pkt,app_limited,snd_nxt,sk_pacing_rate"

#outputfilepath="framework.csv"
bytesgraphcont=[("FRAMEWORK", [0,1]), ("HSPP", [0,1])]
#rttgraphcont=[("FRAMEWORK", [0,3]), ("HSPP", [0,1])]
graphs=[bytesgraphcont]#, rttgraphcont]
#graphcontents=[[()]] * len(graphs)

def scaletomin(x):
    scalemin = min(x)
    xscaled = [0] * len(x)
    for i in range(len(x)):
        xscaled[i] = x[i] - scalemin
    return xscaled

def creategraphs(curflow, logtypeset, outputdir, flowpointer):
    if "HSPP" in logtypeset:
        bytesgraphcont=[("FRAMEWORK", [0,1]), ("HSPP", [0,1])]
    else:
        bytesgraphcont=[("FRAMEWORK", [0,1]), ("HS", [0,1])]
    
    #print(f"graphing {flowpointer} with {curflow}")
    scalefactor = 1000000 # ms
    bytescale = 2 * 1000000 # 1 x 1MB
    bytemin = 0 * 1000000 # 1 x 1MB
    displayseconds = 1 # seconds window size
    displayoffset = 0 # seconds start offset
    graphcontents=0
    graphcontents=[[]] * len(graphs)
    # For every line in the current flow
    for line in curflow:
        linetype, values = line
        # Check if a graph needs this info, and if so append it to the graph's info
        for i in range(len(graphs)):
            graph = graphs[i]
            for graphsource in graph:
                targetlinetype, targetvalues = graphsource
                #TODO
                if linetype == targetlinetype:
                    #print(f"graph #{i} {values[targetvalues[0]]} {values[targetvalues[1]]}")
                    graphcontents[i].append((values[targetvalues[0]],values[targetvalues[1]]))
              
    #i dont like this but it will work for now
    deltatimestart = 0
    for i in range(len(graphcontents)):
        #print(i)
        #print(graphcontents)
        contents = graphcontents[i]
        contents.sort(key=lambda a:a[0])
        xs = [xy[0] for xy in contents]
        if xs:
            minscale = int(min(xs))
        else:
            continue
        
        #print(f"contents: {contents}")

        colormap = {"SS":"Blue", "CSS":"Yellow", "CA":"Red"}
        
        numsections = 0
        graphsections = []
        #:(
        sectionx=[]
        sectiony=[]
        lastcolor=""
        for i in range(len(contents)):
            x,y = contents[i]
            #print(f"y: {y}")
            try:
                int(x)
                if (deltatimestart == 0):
                    deltatimestart = int(x)
            except ValueError:
                print("Malformed input, skipping")
                continue
            try:
                #print("an int!!")
                sectiony.append(int(y))
                sectionx.append(int(x))
            except ValueError:
                #print(f"a string: {y}")
                color = "Pink"
                print("enter " + y + "at " + str((int(x)-deltatimestart)/scalefactor))
                if y in colormap:
                    color = colormap.get(y)
                if lastcolor == "":
                    lastcolor = color
                # A state change indicator does not have all the packet info, get the next viable 
                #  packet to close this section
                while i < len(contents)-1:
                    x,y = contents[i+1]
                    try:
                        sectiony.append(int(y))
                        sectionx.append(int(x))
                        break
                    except ValueError:
                        i += 1
                if sectionx and sectiony:
                    graphsections.append((sectionx, sectiony, lastcolor))
                lastcolor = color
                
                sectionx=[]
                sectiony=[]
                numsections += 1
        if sectionx:
            # If we get to the end and no state changes have been made, use last state
            #  color and append the rest
            graphsections.append((sectionx, sectiony, lastcolor))
        #plt.close()
        
        for section in graphsections:
            #TODO dynamic scaling
            for i in range(len(section[0])):
                # Adjust all x to the first value being 0
                section[0][i] -= minscale 
                # Adjust all x from nsec to msec
                section[0][i] = section[0][i]/scalefactor
            #print(f"uhstar {section[0]}")
            #plt.figure(1)
            tcolor = section[2] 
            if tcolor == "":
                tcolor = "Pink"
                #TODO why
                print("!!!!!!")
            plt.plot(section[0], section[1], color=tcolor)
        ax = plt.gca()
        #in nsecs
        ax.set_xlim([displayoffset * 1000000000/scalefactor, displayseconds * 1000000000/scalefactor])
        ax.set_ylim([bytemin, bytescale])
        plt.title(flowpointer)

        #plt.show()
        plt.savefig(f"{outputdir}{flowpointer}_graphtest.png")
        plt.clf()

def processDir(parent, dir):
    for dirs in os.listdir(f"{testlogsdir}{parent}{dir}"):
        #isdir = os.path.isdir(f"{testlogsdir}{parent}{dir}{dirs}")
        #print(f"{testlogsdir}{parent}{dir}{dirs} {isdir}\n")
        if os.path.isdir(f"{testlogsdir}{dir}{dirs}"):
            if not os.path.exists(f"{outputdir}{parent}{dir}{dirs}"):
                os.makedirs(f"{outputdir}{parent}{dir}{dirs}")
            if not os.path.exists(f"{frameworkdir}{parent}{dir}{dirs}"):
                os.makedirs(f"{frameworkdir}{parent}{dir}{dirs}")
            processDir("",f"{parent}{dir}{dirs}/")
        else:
            if f"{dirs[-4:]}" == ".log":
                processlog(f"{parent}{dir}{dirs}")

def processalllogs():
    #for (root,dirs,files) in os.walk("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/.",topdown=True):
    if not os.path.exists(f"{outputdir}"):
        os.makedirs(f"{outputdir}")
    for dirs in os.listdir(testlogsdir):
        #isdir = os.path.isdir(f"{testlogsdir}{dirs}")
        #print(f"{testlogsdir}{dirs} {isdir}\n")
        if os.path.isdir(f"{testlogsdir}{dirs}"):
            if not os.path.exists(f"{outputdir}{dirs}"):
                os.makedirs(f"{outputdir}{dirs}")
            if not os.path.exists(f"{frameworkdir}{dirs}"):
                os.makedirs(f"{frameworkdir}{dirs}")
            processDir("",f"{dirs}/")
        else:
            if f"{dirs[-4:]}" == ".log":
                processlog(f"{dirs}")


def processlog(logfilepath):
    try:
        with open(f"{testlogsdir}{logfilepath}", "r") as inputfile:
            #might want to enforce using this to make it backwards compatible?
            #collections.OrderedDict()
            flows = {}
            logtypeset = set()
            for line in inputfile:
                # remove "]" at end
                line = line[:-2]
                # trim to our log stuff only
                if not "[CCRG]" in line:
                    continue
                line = line[line.index("[CCRG]"):]
                #print(line)
                pieces = line.split('] [')
                
                #TODO no magic number
                if len(pieces) == 5:
                    if pieces[1] == "FP":
                        if not pieces[2] in flows:
                            flows[pieces[2]] = []
                        flows[pieces[2]].append((pieces[3], pieces[4].split(',')))
                        logtypeset.add(f"{pieces[3]}")
                        print(f"{pieces[3]}")
            print(f"{flows}")
            print(f"{logtypeset}")
            #Create all different log types relevant to this run
            for flowpointer in flows.keys():
                print(f"Flowpointer:{flowpointer}")
                curflow = flows.get(flowpointer)
                #print(f"all of curflow in file{logfilepath}:{curflow}")
                if len(curflow) <= tracelengthfilter:
                    print(f"Shorter than length filter of {tracelengthfilter}, skipping")
                    continue
                else:
                    for logtype in logtypeset:
                        if logtype in desiredparsedlogs:
                            # Parsing to general log types
                            logspecificfilepath=f"{outputdir}{logfilepath[:-4]}_{logtype}.csv"
                            #print(f"Writing to {logspecificfilepath}\n")
                            with open(logspecificfilepath, "w+") as outputfile:
                                outputfile.write(csvheader + "\n")
                                for line in curflow:
                                    linetype, values = line
                                    if linetype == logtype:
                                        outputfile.write(",".join(values) + "\n")
                    creategraphs(curflow, logtypeset, f"{outputdir}{logfilepath[:-4]}", flowpointer)

    except FileExistsError:
        print(f"{outputfilepath} already exists")
    #except FileNotFoundError:
    #    print("Cannot find file " + logfilepath)
    

#parser = argparse.ArgumentParser()
#parser.add_argument("-wab", "--maxb", maxb="{w}indow m{a}x mega{b}ytes")
#parser.add_argument("-wib", "--minb", minb="{w}indow m{i}n mega{b}ytes")
#parser.add_argument("-wss", "--startsec", startsec="{w}indow {s}tarting {s}econds")
#parser.add_argument("-wes", "--endsec", endsec="{w}indow {e}nding {s}econds")
#args = parser.parse_args()
#for arg in args:
#    if arg:
        #todo
processalllogs()
