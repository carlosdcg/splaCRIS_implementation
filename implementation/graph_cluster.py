#!/usr/bin/python

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os


x = np.array([1,2,4,8,16,32])
a = [2010.44763303,1060.80047798,586.014445066,543.712262154,521.616870165,521.292215109]
b = [2059.06947899,1046.87119007,575.115453959,296.285589933,366.384442091,341.007520199]
c = [2031.25184584,1093.52087283,586.344302893,320.010899067,300.745616913,382.748430014]
d = [2207.35427213,1143.951792,576.370896101,495.507214785,308.374300957,287.340030909]


la = plt.plot(x,a,'y-.',label='1 Node')
lb = plt.plot(x,b,'r--',label='2 Nodes')
lc = plt.plot(x,c,'g:',label='4 Nodes')
ld = plt.plot(x,d,'b-',label='8 Nodes')


da = plt.plot(x,a,'bo',markersize=3)
db = plt.plot(x,b,'bo',markersize=3)
dc = plt.plot(x,c,'bo',markersize=3)
dd = plt.plot(x,d,'bo',markersize=3)

ll = plt.legend(loc='upper right')
lx = plt.xlabel("Workers")
ly = plt.ylabel("Execution time (seconds)")
plt.xticks([1,2,4,8,16,32])


plt.savefig('plot_cluster.eps')
plt.show()
