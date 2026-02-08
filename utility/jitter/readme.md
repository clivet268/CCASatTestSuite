# Jitter Inducer

a small tool to add some variance (jitter) to the rtt of a trace file

doesn't accurately simulate all effects of jitter (like jitter effecting when packets are sent)

requires matplotlib and numpy

## input format

a csv of a packet trace with these columns

```
now_us
bytes_acked
mss
rtt_us
tp_deliver_rate
tp_interval
tp_delivered
lost_pkt
total_retrans_pkt
app_limited
snd_nxt
sk_pacing_rate
snd_una
snd_cwnd
```

## Usage

jitter.py saves output files to jitterOutput in pwd

graphJitter.py saves output files to jitterOutputImages in pwd

### jitter.py

```
> python jitter.py [-M] <JitterAmount> <Filename>
```

takes a trace file and applied jitter

jitter amount is in terms of the mean value of the rtt. unless -M is set in which case it is in terms of microseconds

jitter amount is the maximum and minimum values to effect the rtt by. a random value it chosen between the two

### graphJitter.py

```
> python graphJitter.py <Filename>
```

creates a graph of the rtt vs time and bytes acked vs time given a trace csv

### recursiveJitter.sh

```
> ./recursiveJitter.sh [-M] <JitterAmount> <file_or_dir> [more files/dirs...]
```

jitter amount and -M are the same as jitter.py

will apply jitter to every file you have given it and all files found recursively in directories

it assumes every file it gets is in the correct format

### recursiveJitterGraph.sh

```
> ./recursiveJitterGraph.sh <file_or_dir> [more files/dirs...]
```

graphs files (recursively if needed) and saves them. assumess everything is in the correct format