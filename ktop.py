#!/usr/bin/python
#This code runs on python 2.7
import os
import sys
import subprocess
import re

### Output ###
#Node	   RUT	CPU(%)              Mem(%)
#node1	0/0/24	    24 [##        ]    	 8 [#         ]


class color:
    GREEN    = '\033[92m'
    CYAN     = '\033[96m'
    DARKCYAN = '\033[36m'
    RED      = '\033[91m'
    TERMINAL = '\033[0m'
#end: class color


class Node:
    def __init__(self):
	self.sHOSTNAME = ''
	self.fCPU      = 0.0
	self.fMEMTOT   = 0.0
	self.fMEMUSE   = 0.0
	self.fMEM      = 0.0
	#self.sRESV     = ''
	#self.sUSED     = ''
	#self.sTOT      = ''
	self.sRUT      = '' #Resv,Used,Tot
    #end1: def __init__

    def getInfo(self, lst):
	try:
	    funcGigaMega   = lambda x: x[:-1] if (x[-1] == 'G') else (float(x[:-1]))/1000
	    self.sHOSTNAME = lst[0]
	    self.fCPU      = round(float(lst[3])/(float(lst[2])-3)*100,1)
	    self.fMEMTOT   = float(lst[4][:-1])
	    self.fMEMUSE   = float(funcGigaMega(lst[5]))
	    self.fMEM      = round(self.fMEMUSE / float(self.fMEMTOT) * 100, 1)
	    self.sRUT      = lst[-1]
	    #lResvUsedTot   = lst[8].split("/")
	    #self.sRESV     = lResvUsedTot[0]
	    #self.sUSED     = lResvUsedTot[1]
	    #self.sTOT      = lResvUsedTot[2]
	except ValueError:   # ValueError occurs when calculate fCPU,fMEMUSE, because value is "-" not number..
	    self.sRUT      = lst[-1]
	#end2: try except
    #end1: def getInfo
#end: class Node


#[jhan@cm35 scripts]$ qstat -f
#queuename                      qtype resv/used/tot. load_avg arch          states
#---------------------------------------------------------------------------------
#QNAME.q@node1                  BIP   0/1/24         1.50     lx24-amd64
#---------------------------------------------------------------------------------
#QNAME.q@node2                  BIP   0/0/24         0.19     lx24-amd64
#---------------------------------------------------------------------------------
#
# Get NodeName, resv/used/tot
def getQSTAT():
    dQSTAT = {}
    qstat  = subprocess.check_output(["qstat","-f"])
    lqstat = qstat.split('\n')
    for i in range(2,len(lqstat),2):
	sNode = (re.split(" +",lqstat[i])[0]).split("@")[1]
	sResvUsedTot = re.split(" +",lqstat[i])[2]
	dQSTAT[sNode] = sResvUsedTot
    #end1: for i
    return dQSTAT
#end: def getQSTAT


### $ qhost
#[0]                     [1]          [2]   [3]   [4]     [5]     [6]     [7]
#HOSTNAME                ARCH         NCPU  LOAD  MEMTOT  MEMUSE  SWAPTO  SWAPUS
#-------------------------------------------------------------------------------
#node1                   lx24-amd64     xx  0.03   x.xG    x.xG   xx.xG   xx.xK
#node2                   lx24-amd64     xx  0.00   x.xG    x.xG   xx.xG   xx.xK
# ...
#nodeN                   lx24-amd64     xx  0.04   xxxG   xxxxM   xx.xG   xx.xM
# Get NodeName, NCPU, LOAD, MEMTOT, MEMUSE

def getQHOST(dQSTAT):
    qhost = subprocess.check_output(["qhost"])
    lst   = []
    lNode = []
    for i in qhost.split('\n'):
	if i.startswith('cm'):
	    lst = (re.split(" +",i))
	    lst.append(dQSTAT[lst[0]])
	    cNode = Node()
	    cNode.getInfo(lst)
	    lNode.append(cNode)
	#end2: if i
    #end1: for i
    return lNode
#end: def getQHOST

def printScreen(lNode):
    print "%s%16s%36s%36s" % ('Node','resv/used/tot','CPU(%) [#########################]','MEM(%) [#########################]')
    for i in lNode:
	sCPU_INDICATOR = color.GREEN + '#'*int(round(float(i.fCPU)/4,0)) + color.TERMINAL
	sMEM_INDICATOR = color.RED + '#'*int(round(float(i.fMEM)/4,0)) + color.TERMINAL
	if 100 <= float(i.fCPU) < 200:
	    sCPU_INDICATOR = color.GREEN + '#'*(50-int(round(float(i.fCPU)/4,0))) + color.CYAN + '#'*(int(round(float(i.fCPU)/4,0))-25) + color.TERMINAL
	#end2: if 100
	if float(i.fCPU) >= 200:
	    sCPU_INDICATOR = color.CYAN + '#'*25 + color.TERMINAL
	#end2: if float
	print "%s%16s%8s [%-34s]%8s [%-34s]" % (i.sHOSTNAME, i.sRUT, i.fCPU, sCPU_INDICATOR, i.fMEM, sMEM_INDICATOR)
    #end1: for
    print "\n\n"
#end: printScreen


if __name__ == "__main__":
    dQSTAT = getQSTAT()
    lNode  = getQHOST(dQSTAT)
    printScreen(lNode)
#end: if main
