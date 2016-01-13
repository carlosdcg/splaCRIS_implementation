#!/usr/bin/python

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os


x = np.array([1,2,4,8,16,32])
a = [2340.49874687,1815.53766394,1277.07213902,1261.50432801,1228.88657498,1239.03921103]
b = [1720.23300004,882.108999968,512.611000061,405.686000109,452.302999973,454.023000002]
c = [2000.19254589,1028.65357995,575.064716101,297.404046059,287.986929893,284.941044807]



la = plt.plot(x,a,'b-',label='Node 1')
lb = plt.plot(x,b,'r--',label='Node 2')
lc = plt.plot(x,c,'g:',label='Node 3')


da = plt.plot(x,a,'bo',markersize=3)
db = plt.plot(x,b,'bo',markersize=3)
dc = plt.plot(x,c,'bo',markersize=3)

ll = plt.legend(loc='upper right')
lx = plt.xlabel("Workers")
ly = plt.ylabel("Execution time (seconds)")
plt.xticks([1,2,4,8,16,32])


plt.savefig('comp_plot_nodes_workers.eps')
#plt.show()
