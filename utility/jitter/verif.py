import sys
import matplotlib.pyplot as plt
def main():
    file = sys.argv[1]
    avgs:list =[]
    fname:list =[]
    lists:list[list] =[]
    timeLimit = 2*1000000
    with open(file,"r") as f:
        for line in f:
            line = line.strip()
            parts = line.split(" ")
            # print(parts)
            def isCanBeInt(s):
                try:
                    int(s)
                    return True
                except ValueError:
                    return False
            if(parts[0] in ["clamp","start","reg"]):
                if(int(parts[3])>timeLimit):
                    continue
                if(parts[0] == 'reg'):
                    assert(parts[1]==parts[2])
                if(parts[0]=="start"):
                    lists.append([])

                if(parts[0]=='clamp'):
                    # continue
                    pass

                lists[-1].append(parts)
                
            elif(isCanBeInt(parts[0])):
                avgs.append(int(parts[0]))
            else:
                fname.append(parts[1])
                # print(line)
    lis = []
    lisT = []
    stage = []
    stageT = []
    colors:dict[str,plt.Color] ={"start":"green", "clamp":"#ff000030","reg":"blue"}
    for j in lists:
        i = sorted(j,key=lambda x : int(x[1]))
        ii = sorted(j,key=lambda x : int(x[2])) # i don't like that this needs to be sorted to get the colors correct
        lis.append([int(x[1]) for x in i])
        lisT.append([int(x[2]) for x in ii])
        stage.append([colors[x[0]] for x in i])
        stageT.append([colors[x[0]] for x in ii])
        print(stage[-1])
        print(lis[-1])
        print(stageT[-1])
        print(lisT[-1])


    
    
    plt.eventplot(lis,orientation="vertical",lineoffsets=[x*3 for x in range(len(avgs))],colors=stage)
    plt.eventplot(lisT,orientation="vertical",lineoffsets=[x*3+1.2 for x in range(len(avgs))],colors=stageT)
    plt.xticks([x*3 for x in range(len(avgs))], labels=avgs)

    plt.show()


if __name__ == "__main__":
    main()