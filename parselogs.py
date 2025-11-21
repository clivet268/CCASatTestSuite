import os
import matplotlib.pyplot as plt

#filepath="/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/2025-11-11_307677302/2025-11-11_307677302_1.log"
filepath=os.getcwd()
testlogsdir=f"{filepath}/testlogs/"
outputdir=f"{filepath}/output/"
frameworkdir=f"{outputdir}/framework/"
tracelengthfilter=10

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
    for i in range(len(graphcontents)):
        #print(i)
        #print(graphcontents)
        contents = graphcontents[i]
        contents.sort(key=lambda a:a[0])
        xs = [xy[0] for xy in contents]
        minscale = int(min(xs))
        
        #print(f"contents: {contents}")

        colormap = {"SS":"Blue", "CSS":"Yellow", "CA":"Red"}
        
        numsections = 0
        graphsections = []
        #:(
        sectionx=[]
        sectiony=[]
        lastcolor="Pink"
        for i in range(len(contents)):
            x,y = contents[i]
            #print(f"y: {y}")
            try:
                int(x)
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
                if y in colormap:
                    color = colormap.get(y)
                
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
                    graphsections.append((sectionx, sectiony, color))
                
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
                #section[0][i] = section[0][i]/1000000
            #print(f"uhstar {section[0]}")
            #plt.figure(1)
            plt.plot(section[0], section[1], color=section[2])
        ax = plt.gca()
        ax.set_xlim([0, 1000000000])
        ax.set_ylim([0, 500000])
        plt.title(flowpointer)

        #plt.show()
        plt.savefig(f"{outputdir}{flowpointer}_graphtest.png")
        plt.clf()
    
def processalllogs():
    #for (root,dirs,files) in os.walk("/home/clivet268/Downloads/KernelLearnel/CCASatTestSuite/testlogs/.",topdown=True):
    for dirs in os.listdir(testlogsdir):
        #isdir = os.path.isdir(os.path.join(testlogsdir,dirs))
        #print(f"{dirs} {isdir}\n")
        if os.path.isdir(f"{testlogsdir}{dirs}"):
            print(f"{dirs}\n")
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
            #might want to enforce using this to make it backwards compatible?
            #collections.OrderedDict()
            flows = {}
            for line in inputfile:
                # remove "]" at end
                line = line[:-2]
                # trim to our log stuff only
                if not "[CCRG]" in line:
                    continue
                line = line[line.index("[CCRG]"):]
                #print(line)
                pieces = line.split('] [')
                logtypeset = set()
                
                #TODO no magic number
                if len(pieces) == 5:
                    if pieces[1] == "FP":
                        if not pieces[2] in flows:
                            flows[pieces[2]] = []
                        flows[pieces[2]].append((pieces[3], pieces[4].split(',')))
                        logtypeset.add(pieces[3])
                        #print(f"{pieces[2]}")
                        #print(f"{flows[pieces[2]]}")
                        #if pieces[4] == "FRAMEWORK":
                            #outputfile.write(pieces[5]+"\n")
            #Create all different log types relevant to this run
            for flowpointer in flows.keys():
                print(f"Flowpointer:{flowpointer}")
                curflow = flows.get(flowpointer)
                if len(curflow) <= tracelengthfilter:
                    print(f"Shorter than length filter of {tracelengthfilter}, skipping")
                    continue
                else:
                    for logtype in logtypeset:
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
processalllogs()
