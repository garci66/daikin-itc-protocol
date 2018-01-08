#!/usr/bin/python
import sys, json, traceback, time, os, json
from daikinProtocol import *
from pyzabbix import ZabbixMetric, ZabbixSender

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    fileHostCheck='./myhosts.json'
    
    if not os.path.exists(fileHostCheck):
        return -1
    
    else:
        with open(fileHostCheck, 'rb') as json_data:
            try:
                myHostDict = json.load(json_data)
            except Exception as e:
                print "failed when loading current host json file or parsing the json" + traceback.format_exc()

    zabbixPacket=[]
    for host in list(myHostDict):
        if len(myHostDict[host]['units'])>0 :
            myUser=myHostDict[host]['user']
            myPass=myHostDict[host]['password']
            myHostId=myHostDict[host]['hostId']
            myHostIp=host
            reqArray=[]

            for unit in list(myHostDict[host]['units']):
                reqArray.append(DaikinStructReqPntState(type=0,id=int(unit)))

            pLogin=DaikinApi()/DaikinHeader()/DaikinReqSetLogin(username=myUser, password=myPass)
            respLogin=DaikinHeader(sendP(myHostIp,pLogin))
            if int(respLogin.arg1)!=1:
                print "Login Failure",myHostIp
                continue
            myUserId=respLogin.arg2

            pPntReq=DaikinApi()/DaikinHeader(id=myUserId)/DaikinReqGetPntState(reqIds=reqArray)
            respPnt=DaikinHeader(sendP(myHostIp,pPntReq))
            
            pLogout=DaikinApi()/DaikinHeader(id=myUserId)/DaikinReqSetLogout()
            DaikinHeader(sendP(myHostIp,pLogout))

            for pnt in respPnt.payload.pntStateArray:
                tempPacket=[
                    ZabbixMetric(myHostId,'daikin.pnt[enumDriveMode,{0}]'.format(pnt.id),pnt.enumDriveMode),
                    ZabbixMetric(myHostId,'daikin.pnt[tempAmbient,{0}]'.format(pnt.id),pnt.tempAmbient),
                    ZabbixMetric(myHostId,'daikin.pnt[tempSetPoint,{0}]'.format(pnt.id),pnt.tempSetPoint),
                    ZabbixMetric(myHostId,'daikin.pnt[enumVentMode,{0}]'.format(pnt.id),pnt.enumVentMode),
                    ZabbixMetric(myHostId,'daikin.pnt[enumVentVol,{0}]'.format(pnt.id),pnt.enumVentVol),
                    ZabbixMetric(myHostId,'daikin.pnt[pntState,{0}]'.format(pnt.id),pnt.pntState),
                    ZabbixMetric(myHostId,'daikin.pnt[errorString,{0}]'.format(pnt.id),pnt.errorString),
                    ZabbixMetric(myHostId,'daikin.pnt[iconMode,{0}]'.format(pnt.id),pnt.iconMode),
                    ZabbixMetric(myHostId,'daikin.pnt[iconAppend,{0}]'.format(pnt.id),pnt.iconAppend)
                ]
                zabbixPacket.extend(tempPacket)

    zbx=ZabbixSender('192.168.128.7')
    zbxResp=zbx.send(zabbixPacket)
    print zbxResp

if __name__ == "__main__":
    sys.exit(main())

