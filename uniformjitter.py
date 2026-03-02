import numpy as np
import matplotlib.pyplot as plt
times=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
maxd=400.0
center=0.0
numvalues=10000
numbuckets=100
random_array = np.random.normal(center, 100.0, numvalues)
#random_array.sort()
'''
buckets={}
for i in range(-numbuckets,numbuckets):
    eee=(maxd/numbuckets) * i
    buckets[eee] = 0
print(buckets.keys())
i=0
ii=0
#print(random_array)
keystuff=list(buckets.keys())
while i < numvalues and ii < len(keystuff):
    #print(ii)
    while random_array[i] < keystuff[ii]:
        #print(f"{random_array[i]} is less than {keystuff[ii]}")
        buckets[keystuff[ii]] = buckets[keystuff[ii]] + 1
        i = i + 1
    ii = ii + 1
#print(buckets)


xpoints = list(buckets.keys())
ypoints = list(buckets.values())

plt.plot(xpoints, ypoints, marker='o', linestyle='-') # marker='o' plots the points as circles

# Add labels and a title
plt.xlabel('X-axis Label')
plt.ylabel('Y-axis Label')
plt.title('Simple Line Graph Example')

# Display the graph
plt.show()
'''
plt.hist(random_array, bins=200)
plt.show()
