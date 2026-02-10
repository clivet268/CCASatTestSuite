import os
import sys

def parseHSPPLog(str:tuple[str,str]) ->dict:

    out = dict()
    data = str[1].split(',')
    out["now_us"] = data[0]
    match str[0]:
        case "HSPP":
            out["HSPP_STATE"] = data[1]
        case"HSPP BASELINE NEW BASELINEMINRTT":
            out["HSPP_NEW_BASELINE_MINRTT"] = data[1]
        case"HSPP BASELINE OLD BASELINEMINRTT":
            out["HSPP_OLD_BASELINE_MINRTT"] = data[1]
        case"HSPP CSS AND ROUND COUNTER DIFF EXCEEDS":
            out["HSPP_CSS_ROUND_COUNTER_EXCEEDSBY"] = data[1]
        case"HSPP ENTERED AT ROUND":
            out["HSPP_CSS_ENTERED_AT_ROUND"] = data[1]
        case"HSPP NEW ENTERED CSS AT ROUND":
            out["HSPP_NEW_CSS_ENTERED_AT_ROUND"] = data[1]
        case"HSPP OLD ENTERED CSS AT ROUND":
            out["HSPP_OLD_CSS_ENTERED_AT_ROUND"] = data[1]
        case"HSPP NEW LAST ROUND MINRTT":
            out["HSPP_NEW_CSS_LAST_ROUND_MINRTT"] = data[1]
        case"HSPP OLD LAST ROUND MINRTT":
            out["HSPP_OLD_CSS_LAST_ROUND_MINRTT"] = data[1]
        case"HSPP ROUND COUNTER":
            out["HSPP_ROUND_COUNTER"] = data[1]
        case"HSPP ROUND COUNTER DIFF":
            out["HSPP_ROUND_COUNTER_DIFF"] = data[1]
        case "HSPP SND_CWND":
            out["HSPP_SND_CWND"] = data[1]
        case "HSPP SND_CWND_CNT":
            out["HSPP_SND_CWND_CNT"] = data[1]
        case "HSPP HSPP_END_SEQ":
            out["HSPP_END_SEQ"] = data[1]
        case "HSPP HSPP_RTTSAMPLE_COUNTER":
            out["HSPP_RTTSAMPLE_COUNTER"] = data[1]
        case "HSPP HSPP_CURRENT_ROUND_MINRTT":
            out["HSPP_CURRENT_ROUND_MINRTT"] = data[1]
        
        case _:
            out["EXTRA"+str[0]] = data[1] 
            print("Unexpected input", str[0])
    return out

def HSPPLogTOFrameworkOutput(l:list[dict]) ->list[str]:
    lp = []
    loss_flag = 0
    start =0
    for i in range(len (l)):
        if 'HSPP_ROUND_COUNTER' not in l[i].keys():
            continue
        item = l[i]
        if(start==0):
            start = int(item["now_us"])
        if((not loss_flag) and (item["lost_pkt"] != "0")):
            loss_flag = 1
            # out = ""
        out = f"""Line {i}:
  now_us: {int(item["now_us"])-start}
  snd_cwnd: {item["HSPP_SND_CWND"]}
  snd_cwnd_cnt: {item["HSPP_SND_CWND_CNT"]}
  hspp_end_seq: {item["HSPP_END_SEQ"]}
  hspp_rttsample_counter: {item["HSPP_RTTSAMPLE_COUNTER"]}
  hspp_current_round_minrtt: {item["HSPP_CURRENT_ROUND_MINRTT"]}
  hspp_round_counter: {item["HSPP_ROUND_COUNTER"]}
  hspp_entered_css_at_round: {item["HSPP_CSS_ENTERED_AT_ROUND"]}
  hspp_css_baseline_minrtt: {item["HSPP_NEW_BASELINE_MINRTT"] if ('HSPP_NEW_BASELINE_MINRTT' in item.keys())else 0}
  hspp_last_round_minrtt: {item["HSPP_NEW_CSS_LAST_ROUND_MINRTT"]}
  hspp_flag: { 0 if item["HSPP_STATE"]=='SS' else (1 if item["HSPP_STATE"]=='CSS' else 2) }
  snd_una: {item["snd_una"]}
  loss happen: {loss_flag }

"""
        lp.append(out)

    return lp


# TODO: Implement
def parseCUBICLog(str:tuple[str,str])->dict:
    out = dict()
    data = str[1].split(',')
    out["now_us"] = data[0]
    match str[0]:
        case "CUB":
            out["CUBIC_STATE"] = data[1]
        #...
        case _:
            out["EXTRA"+str[0]] = data[1] 
            print("Unexpected input", str[0])
    return out
    
# TODO: Implement
def CUBICLogTOFrameworkOutput(l:list[dict]) ->list[str]:
    lp = []
    loss_flag = 0
    start =0
#     for i in range(len (l)):
#         if 'HSPP_ROUND_COUNTER' not in l[i].keys():
#             continue
#         item = l[i]
#         if(start==0):
#             start = int(item["now_us"])
#         if((not loss_flag) and (item["lost_pkt"] != "0")):
#             loss_flag = 1
#         out = f"""Line {i}:
#   now_us: {int(item["now_us"])-start}
#   snd_cwnd: {item["HSPP_SND_CWND"]}
#   snd_cwnd_cnt: {item["HSPP_SND_CWND_CNT"]}
#   hspp_end_seq: {item["HSPP_END_SEQ"]}
#   hspp_rttsample_counter: {item["HSPP_RTTSAMPLE_COUNTER"]}
#   hspp_current_round_minrtt: {item["HSPP_CURRENT_ROUND_MINRTT"]}
#   hspp_round_counter: {item["HSPP_ROUND_COUNTER"]}
#   hspp_entered_css_at_round: {item["HSPP_CSS_ENTERED_AT_ROUND"]}
#   hspp_css_baseline_minrtt: {item["HSPP_NEW_BASELINE_MINRTT"] if ('HSPP_NEW_BASELINE_MINRTT' in item.keys())else 0}
#   hspp_last_round_minrtt: {item["HSPP_NEW_CSS_LAST_ROUND_MINRTT"]}
#   hspp_flag: { 0 if item["HSPP_STATE"]=='SS' else (1 if item["HSPP_STATE"]=='CSS' else 2) }
#   snd_una: {item["snd_una"]}
#   loss happen: {loss_flag }

# """
#         lp.append(out)

    return lp



# TODO: Implement
def parseHSLog(str:tuple[str,str])->dict:

    out = dict()
    data = str[1].split(',')
    out["now_us"] = data[0]

    match str[0]:
        case "HS":
            out["HS_STATE"] = data[1]
    #    printf("  now_us: %u\n", now_us);
    #    printf("  end_seq: %u\n", ca->end_seq);
    #    printf("  delay_min: %u\n", ca->delay_min);
    #    printf("  sample_count: %u\n", ca->sample_cnt);
    #    printf("  curr_rtt: %u\n", ca->curr_rtt);
    #    printf("  hystart_found: %u\n", ca->found);
    #    printf("  round_start: %u\n", ca->round_start);
    #    printf("  app_limited: %u\n", app_limited);
        #...
        case _:
            out["EXTRA"+str[0]] = data[1] 
            print("Unexpected input", str[0])
    return out
    return out

# TODO: Implement
def HSLogTOFrameworkOutput(l:list[dict]) ->list[str]:
    lp = []
    loss_flag = 0
    start =0
#     for i in range(len (l)):
#         if 'HSPP_ROUND_COUNTER' not in l[i].keys():
#             continue
#         item = l[i]
#         if(start==0):
#             start = int(item["now_us"])
#         if((not loss_flag) and (item["lost_pkt"] != "0")):
#             loss_flag = 1
#         out = f"""Line {i}:
#   now_us: {int(item["now_us"])-start}
#   snd_cwnd: {item["HSPP_SND_CWND"]}
#   snd_cwnd_cnt: {item["HSPP_SND_CWND_CNT"]}
#   hspp_end_seq: {item["HSPP_END_SEQ"]}
#   hspp_rttsample_counter: {item["HSPP_RTTSAMPLE_COUNTER"]}
#   hspp_current_round_minrtt: {item["HSPP_CURRENT_ROUND_MINRTT"]}
#   hspp_round_counter: {item["HSPP_ROUND_COUNTER"]}
#   hspp_entered_css_at_round: {item["HSPP_CSS_ENTERED_AT_ROUND"]}
#   hspp_css_baseline_minrtt: {item["HSPP_NEW_BASELINE_MINRTT"] if ('HSPP_NEW_BASELINE_MINRTT' in item.keys())else 0}
#   hspp_last_round_minrtt: {item["HSPP_NEW_CSS_LAST_ROUND_MINRTT"]}
#   hspp_flag: { 0 if item["HSPP_STATE"]=='SS' else (1 if item["HSPP_STATE"]=='CSS' else 2) }
#   snd_una: {item["snd_una"]}
#   loss happen: {loss_flag }

# """
#         lp.append(out)

    return lp


# TODO: Implement
def parseSEARCHLog(str:tuple[str,str])->dict:
    out = dict()
    data = str[1].split(',')
    out["now_us"] = data[0]
    match str[0]:
        case "SEARCH":
            out["SEARCH_STATE"] = data[1]
        #...
        case _:
            out["EXTRA"+str[0]] = data[1] 
            print("Unexpected input", str[0])
    return out

    return out

# TODO: Implement
def SEARCHLogTOFrameworkOutput(l:list[dict]) ->list[str]:
    lp = []
    loss_flag = 0
    start =0
#     for i in range(len (l)):
#         if 'HSPP_ROUND_COUNTER' not in l[i].keys():
#             continue
#         item = l[i]
#         if(start==0):
#             start = int(item["now_us"])
#         if((not loss_flag) and (item["lost_pkt"] != "0")):
#             loss_flag = 1
#         out = f"""Line {i}:
#   now_us: {int(item["now_us"])-start}
#   snd_cwnd: {item["HSPP_SND_CWND"]}
#   snd_cwnd_cnt: {item["HSPP_SND_CWND_CNT"]}
#   hspp_end_seq: {item["HSPP_END_SEQ"]}
#   hspp_rttsample_counter: {item["HSPP_RTTSAMPLE_COUNTER"]}
#   hspp_current_round_minrtt: {item["HSPP_CURRENT_ROUND_MINRTT"]}
#   hspp_round_counter: {item["HSPP_ROUND_COUNTER"]}
#   hspp_entered_css_at_round: {item["HSPP_CSS_ENTERED_AT_ROUND"]}
#   hspp_css_baseline_minrtt: {item["HSPP_NEW_BASELINE_MINRTT"] if ('HSPP_NEW_BASELINE_MINRTT' in item.keys())else 0}
#   hspp_last_round_minrtt: {item["HSPP_NEW_CSS_LAST_ROUND_MINRTT"]}
#   hspp_flag: { 0 if item["HSPP_STATE"]=='SS' else (1 if item["HSPP_STATE"]=='CSS' else 2) }
#   snd_una: {item["snd_una"]}
#   loss happen: {loss_flag }

# """
#         lp.append(out)

    return lp



def parseFRAMEWORKLog(strp:tuple[str,str])->dict:
    out = dict()
    li = strp[-1].split(',')
    header = "now_us,bytes_acked,mss,rtt_us,tp_deliver_rate,tp_interval,tp_delivered,lost_pkt,total_retrans_pkt,app_limited,snd_nxt,sk_pacing_rate,snd_una,snd_cwnd".split(',')
    for i in range(len(li)):
        out[header[i]] = li[i]
    return out

def parseLogLine(strs:list[str]) -> dict:
    TAG_INDEX = -2
    DATA_INDEX = -1


    item = (strs[TAG_INDEX],strs[DATA_INDEX])
    if "FRAMEWORK" in strs[TAG_INDEX] :
        return parseFRAMEWORKLog(item)
    if("HSPP" in strs[TAG_INDEX]):
        return parseHSPPLog(item)
    if("SEARCH" in strs[TAG_INDEX]):
        return parseSEARCHLog(item)
    if("HS" in strs[TAG_INDEX]):
        return parseHSLog(item)
    if("CUB" in strs[TAG_INDEX]):
        return parseCUBICLog(item)
    if("TCP State Change" in strs[TAG_INDEX]):
        i = item[1].split(',')
        out = dict()
        out["now_us"] = i[0]
        out["TCP_STATE_CHANGE"] = i[1]
        return out
    assert(False)
    # return dict()

def parseLog(log:list[list[str]]) -> list[dict]:
    li = []

    # it = 0
    temp = []
    for i in range(len(log)):
        temp.append(parseLogLine(log[i]))
    def d( x): 
        return int(x["now_us"])
    temp.sort(key=d)



    it = 0
    t = temp[0]["now_us"]
    out = dict()
    while it < len(temp):
        if t == temp[it]["now_us"]:
            out.update(temp[it])
            it+=1
        else:
            t = temp[it]["now_us"]
            li.append(out)
            out = dict()
    return li

def stateIfyLogs(traces: list[dict])->list[dict]:
    state = dict()
    lis:list[dict] = []
    for i in traces:
        state.update(i)
        lis.append(state.copy())
    return lis

def getFileThings(str) -> list[str]:
    l = []
    with open(str) as f:
        while line:= f.readline():
            line = line.strip()
            ind = line.find(": [")
            if ind >0 and "CCRG" in line:
                l.append(line[ind+2:])
        pass

    return l

def maxFPlines(strs:list[str]) -> list[list[str]]:
    l = []
    counts:dict[str,int] = dict()
    for line in strs:
        items = list(map(lambda x: x.strip()[1:],line[line.index("[CCRG]"):].split("]")))[:-1]
        fp = items[2]
        counts[fp] = counts[fp]+1 if fp in counts.keys() else 0
        pass
    m = ("",-1)
    for i in counts:
        if m[1] < counts[i]:
            m = (i,counts[i])
    for line in strs:
        items = list(map(lambda x: x.strip()[1:],line[line.index("[CCRG]"):].split("]")))[:-1]
        if(m[0] in items):
            l.append(items)

    return l
    pass



def main():

    if(len(sys.argv)<4):
        print("Usage: <HSPP | CUBIC | SEARCH | HS>  <kernaLogFile> <outputFile>\n  a flag for which log format\n  a kernal log file from our congestion control algorithms with logging\n  and a output file\n\nCreates a framework output file form our kernel logs. A utility script so we\ncan graph framework outputs and actual runs with the same graphing script\nwithout much modification")
        sys.exit(-1)

    caAlg =sys.argv[1]
    inputfile= sys.argv[2]
    output:str= sys.argv[3]

    packetTrace =  stateIfyLogs(parseLog(maxFPlines(getFileThings(inputfile))))
    
    pks = []
    match caAlg:
        case "HSPP":
            pks = HSPPLogTOFrameworkOutput(packetTrace)
        case "CUBIC":
            pks = CUBICLogTOFrameworkOutput(packetTrace)
        case "SEARCH":
            pks = SEARCHLogTOFrameworkOutput(packetTrace)
        case "HS":
            pks = HSLogTOFrameworkOutput(packetTrace)

    os.makedirs(os.path.dirname(output),exist_ok=True)
    with open(output, "w") as outfile:
                outfile.write("Transformed K-Log to framework output:" + inputfile+"\n\n")
                for i in pks:
                    outfile.write(i)

if __name__ == "__main__":
    main()