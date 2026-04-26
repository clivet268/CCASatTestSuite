
import argparse as ap
import sys
import os
import pandas as pd


flags = [
    '[CSS ENTRY]',
    '[CSS ABORT->SS]',
    '[HSPP exit]',
    '[STATE DURATION SUMMARY]',
        ]
class FG:
    CSS = flags[0]
    SS = flags[1]
    EXIT = flags[2]
    SUMMARY = flags[3]

class dataformat:
    def __init__(self,filename='') -> None:
        self.filename = filename

        self.segmentsInSS = 0
        self.segmentsInCSS = 0
        self.transitions = 0
        self.totalTime = 0.0
        self.totalTimeSS = 0.0
        self.firstCSSTime = 0.0
        self.totalTimeCSS = 0.0
        self.percentSS = 0.0
        self.percentCSS = 0.0
        self.jitter = 0.0
        self.jitterType = "PC"
        pass
    # segmentsInSS = 0
    # segmentsInCSS = 0
    # totalTime = 0.0
    # totalTimeSS = 0.0
    # totalTimeCSS = 0.0
    # percentSS = 0.0
    # percentCSS = 0.0
    # jitter = 0.0
    # jitterType = "PC"


datastoreFile = "aggregrateTransitions.csv"

def main(filename, jitterAmountHint:float, jitterTypeHint:str):
    
    segmentsInSS = 1
    segmentsInCSS = 0
    totalTime = 0.0
    totalTimeSS = 0.0
    totalTimeCSS = 0.0
    # totalTimeEXIT = 0.0
    # jitterTypes = {"MS":0,"PC":1}
    jitterAmount = jitterAmountHint
    jitterType = jitterTypeHint
    transitions = 0
    firstCSSTime = 0.0




    with open(filename) as f:
        for line in f:
            line = line.strip()
            for fg in flags:
                if fg in line:
                    match fg:
                        case FG.CSS:
                            segmentsInCSS +=1
                            transitions +=1
                            if firstCSSTime <=0:
                                pos = line.find("time=")
                                pos2 = line.find("s")
                                t = float(line[pos+5:pos2])
                                firstCSSTime = t
                            break
                        case FG.SS:
                            segmentsInSS +=1
                            transitions +=1
                            break
                        case FG.EXIT:
                            break
                        case FG.SUMMARY:
                            # totalTime = float(f.readline().split(sep='=')[1].strip()[:-1])
                            f.readline()
                            totalTimeSS = float(f.readline().split(sep='=')[1].split(sep=' ')[0].strip()[:-1])
                            totalTimeCSS =float(f.readline().split(sep='=')[1].split(sep=' ')[0].strip()[:-1])
                            totalTime = totalTimeSS+totalTimeCSS
                            # totalTimeEXIT = float(f.readline().split(sep='=')[1].strip()[:-1])
                            break
                pass
        pass
    
    data = dataformat(filename=filename)
    
    data.segmentsInSS = segmentsInSS
    data.segmentsInCSS = segmentsInCSS
    data.totalTime = totalTime
    data.totalTimeSS = totalTimeSS
    data.totalTimeCSS = totalTimeCSS
    data.percentSS = totalTimeSS/(totalTimeSS+totalTimeCSS)
    data.percentCSS = 1-(totalTimeSS/(totalTimeSS+totalTimeCSS))
    data.jitter = jitterAmount
    data.jitterType = jitterType
    data.transitions = transitions
    data.firstCSSTime = firstCSSTime
    
    return data

def mainmain():
    desc = "parse transitions file\n"
    parser = ap.ArgumentParser(prog=os.path.basename(__file__),description=desc)
    parser.add_argument('fileNames',nargs="+")
    args = parser.parse_args()
    
    if(not os.path.isfile(datastoreFile)):
        # print(dataformat().__dict__)
        var = dataformat()
        print(var.__dict__)
        sdf = pd.DataFrame([var.__dict__],)
        sdf.to_csv(datastoreFile,index=False)


    mdf = pd.read_csv(datastoreFile)
    look = "-jitter_"
    looklen = len(look)
    for file in args.fileNames:
        file:str = file
        if(not os.path.isfile(file)):
            print("WARNING: filename: \"{file}\" does not exist -- skipping",file = sys.stderr)
            continue
        else:
            print(f"PROCESSING: FILE \"{file}\"")

        pos = file.find(look)
        jitterAmount = 0.0
        jitterType = "PC"
        if(pos > -1):
            strt = file[pos+looklen:-1]
            after = strt.find("_")
            jitterType =  "MS" if "MS" in strt else "PC"
            if(jitterType=="MS"):
                jitterAmount = float(strt[:after-3])
            else:
                jitterAmount = float(strt[:after])
        df = main(file,jitterAmount,jitterType)
        mdf = pd.concat([mdf,pd.DataFrame([df.__dict__])],ignore_index=True)
    
    mdf.to_csv(datastoreFile,index=False)

    pass


if __name__ =="__main__":
    mainmain()
