#!/usr/bin/python
import sys, json
from daikinProtocol import *

def zabbixfyFields(fieldName):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', fieldName)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()
    return '{{#DAIKIN_{}}}'.format(s2)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 2:
        return 1
    
    myHost=argv[1]
    #myUser=argv[2]
    #myPass=argv[3]

    p=DaikinApi()/DaikinHeader(id=0)/DaikinReqGetPntProp()
    myResp=DaikinHeader(sendP(myHost,p))

    myReturn=[]
    for pnt in myResp.payload.pntArray:
        tempDict={}
        for field in pnt.fields:
            tempDict[zabbixfyFields(field)] = pnt.fields[field]
        myReturn.append(tempDict)
    print json.dumps(myReturn, indent=4)

if __name__ == "__main__":
    sys.exit(main())

