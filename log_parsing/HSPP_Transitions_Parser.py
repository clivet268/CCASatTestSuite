
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
    segmentsInSS = 0
    segmentsInCSS = 0
    totalTime = 0.0
    totalTimeSS = 0.0
    totalTimeCSS = 0.0
    percentSS = 0.0
    percentCSS = 0.0
    jitter = 0.0
    jitterType = "PC"


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




    with open(filename) as f:
        for line in f:
            line = line.strip()
            for fg in flags:
                if fg in line:
                    match fg:
                        case FG.CSS:
                            segmentsInCSS +=1
                            break
                        case FG.SS:
                            segmentsInSS +=1
                            break
                        case FG.EXIT:
                            break
                        case FG.SUMMARY:
                            totalTime = float(f.readline().split(sep='=')[1].strip()[:-1])
                            totalTimeSS = float(f.readline().split(sep='=')[1].split(sep=' ')[0].strip()[:-1])
                            totalTimeCSS =float(f.readline().split(sep='=')[1].split(sep=' ')[0].strip()[:-1])
                            # totalTimeEXIT = float(f.readline().split(sep='=')[1].strip()[:-1])
                            break
                pass
        pass
    
    data = dataformat()
    
    data.segmentsInSS = segmentsInSS
    data.segmentsInCSS = segmentsInCSS
    data.totalTime = totalTime
    data.totalTimeSS = totalTimeSS
    data.totalTimeCSS = totalTimeCSS
    data.percentSS = totalTimeSS/(totalTimeSS+totalTimeCSS)
    data.percentCSS = 1-(totalTimeSS/(totalTimeSS+totalTimeCSS))
    data.jitter = jitterAmount
    data.jitterType = jitterType
    
    return data

def mainmain():
    desc = "parse transitions file\n"
    parser = ap.ArgumentParser(prog=os.path.basename(__file__),description=desc)
    parser.add_argument('fileNames',nargs="+")
    args = parser.parse_args()
    
    mdf = pd.read_csv(datastoreFile)
    pattern = r'(?<=\d)(?=\D)|(?<=\D)(?=\d)'
    look = "-jitter_"
    looklen = len(look)
    # print(args.fileNames)
    for file in args.fileNames:
        file:str = file
        if(not os.path.isfile(file)):
            print("WARNING: filename: \"{file}\" does not exist -- skipping",file = sys.stderr)
            continue
        else:
            print("PROCESSING: FILE \"{file}\"")

        pos = file.find(look)
        jitterAmount = 0.0
        jitterType = "PC"
        if(pos > -1):
            strt = file[pos+looklen:-1]
            jitterType =  "MS" if "MS" in strt else "PC"
            if(jitterType=="MS"):
                jitterAmount = float(strt[:-7])
            else:
                jitterAmount = float(strt[:-4])
        df = main(file,jitterAmount,jitterType)
        # mdf.insert([df.__dict__()])
        print(df.__dict__)
    
    # mdf.to_csv(datastoreFile)

    pass


if __name__ =="__main__":
    mainmain()
