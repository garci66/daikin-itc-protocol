#!/usr/bin/python
import sys, json, traceback, time, os
from daikinProtocol import *

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 6:
        return 1
    
    fileHostCheck='./myhosts.json'
    
    myHost=argv[1]
    myHostId=argv[2]
    myId=argv[3]
    myUser=argv[4]
    myPass=argv[5]

    myHostDict={}

    thisTime=int(time.time())
    lifetime=3600*24

    if os.path.exists(fileHostCheck):
        with open(fileHostCheck, 'rb') as json_data:
            try:
                myHostDict = json.load(json_data)
            except Exception as e:
                print "failed when loading current host json file or parsing the json" + traceback.format_exc()

    if myHost not in myHostDict:
        myHostDict[myHost]={'timestamp':thisTime,'units':{},'user':myUser,'password':myPass,'hostId':myHostId}
    else:
        myHostDict[myHost]['timestamp']=thisTime
        myHostDict[myHost]['user']=myUser
        myHostDict[myHost]['password']=myPass
	myHostDict[myHost]['hostId']=myHostId
    if myId not in myHostDict[myHost]['units']:
        myHostDict[myHost]['units'][myId]=thisTime
    else:
        myHostDict[myHost]['units'][myId]=thisTime

    myNewHostDict={}
    
    for host in list(myHostDict):
        if myHostDict[host]['timestamp']<thisTime-(lifetime):
            myHostDict.pop(host)
        else:
            for unit in list(myHostDict[host]['units']):
                if myHostDict[host]['units'][unit]<thisTime-(lifetime):
                    myHostDict[host]['units'].pop(unit)

    with open(fileHostCheck, 'wb') as fp:
        json.dump(myHostDict, fp, indent=4, sort_keys=True)
    print 1
if __name__ == "__main__":
    sys.exit(main())


