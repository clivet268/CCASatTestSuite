

numberType = int

def parseTrace(fileName:str)->tuple[list[str],list[list[str]]] :
    ll = []
    format_l =None
    with open(fileName) as f:
        line =f.readline().strip()
        line = line.split(",")
        format_l = line
        while l :=f.readline().strip():
            l = l.split(",")
            ll.append(l)
    return (format_l,ll)

def getRelevant(getRows:list[str],headers:list[str],trace:list[list[str]])->list[list[numberType]]:
    indexes = []
    for i in getRows:
        indexes.append(headers.index(i))
    # print(indexes)
    outList:list[list[numberType]] = []
    for i in trace:
        tempList = []
        for j in indexes:
            tempList.append(int(i[j]))
        outList.append((tempList))

    return outList


def writeNew(outFileName:str,updatedTimes:list[list[numberType]], setRows:list[str],headers:list[str], oldData:list[list[str]])->None:
    indexes = []
    for i in setRows:
        indexes.append(headers.index(i))
    with open(outFileName,mode="w") as f:
        h = ','.join(headers) + '\n'
        f.write(h)
        for k in range(len(updatedTimes)):
            j = 0
            newData=[]
            for i in range(len(oldData[k])):
                dat = oldData[k][i]
                if( i in indexes):
                    dat = str(updatedTimes[k][j])
                    j+=1
                # print(dat)
                newData.append(dat)
            f.write(','.join(newData)+'\n')
            



    
    pass
