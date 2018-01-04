sys.path.append('./')
from daikinProtocol import *

p1=DaikinApi()/DaikinHeader()/DaikinReqGetSysVersion()
myResp=DaikinHeader(sendP(p1))
myResp.show()


p=DaikinApi()/DaikinHeader(id=0)/DaikinReqGetZoneProp()
myResp=DaikinHeader(sendP(p))
myResp.show()


p=DaikinApi()/DaikinHeader(id=0)/DaikinReqGetPntProp()
myResp=DaikinHeader(sendP(p))
myResp.show()

for pnt in myResp.payload.pntArray:
    print pnt.tempSetPoint, pnt.tempAmbient

    #   |  id= 16
    #   |  portNumner= 0
    #   |  address= 6
    #   |  pntType= 9
    #   |  innerType= 0
    #   |  iconId= 0
    #   |  shortName= u'1:1-06'
    #   |  longName= u'2006'



p2=DaikinApi()/DaikinHeader()/DaikinReqSetLogin(username="admin", password="loisuites")
myResp=DaikinHeader(sendP('192.168.9.93',p2))
myResp.show()
userId=myResp.arg2


#id to identify zone wanted
p4=DaikinApi()/DaikinHeader(id=0)/DaikinReqGetZonePnt()
myResp=DaikinHeader(sendP('192.168.9.93',p4))
myResp.show()


#this call requires to be authenticated - use userid from login
p5=DaikinApi()/DaikinHeader(id=userId)/DaikinReqGetPntState(reqIds=[
        DaikinStructReqPntState(type=0,id=12),
        DaikinStructReqPntState(type=0,id=13),
        DaikinStructReqPntState(type=0,id=14)
    ])
p5.show()
myResp=DaikinHeader(sendP('192.168.9.93',p5))
myResp.show()

for pnt in myResp.payload.pntStateArray:
    print pnt.tempSetPoint, pnt.tempAmbient


>>> for pnt in myResp.payload.pntStateArray:
...    print pnt.tempSetPoint, pnt.tempAmbient



p6=DaikinApi()/DaikinHeader(id=userId)/DaikinReqGetPntState(reqIds=[
        DaikinStructReqPntState(type=1,id=0),
    ])
p6.show()
myResp=DaikinHeader(sendP(p6))
myResp.show()


p7=DaikinApi()/DaikinHeader(id=userId)/DaikinReqSetLogout()
myResp=DaikinHeader(sendP('192.168.9.93',p7))
myResp.show()







rawResponse=sendP(p3)
myDai=DaikinHeader(rawResponse)


p5=DaikinApi()/DaikinHeader(id=0)/DaikinReqGetPntState(reqIds=[DaikinStructReqPntState(type=0,id=0)])



 myDai.payload.zoneArray[0].longName.decode('utf-16-le')
u'Todas zonas funcionando\x00\x00\x00\x00\x00\x00\x00\x00\x00'



#este recupera el status de todos los equipos (temperaturas,etc)
p=daiApi/Daikin(command=60104, filler=[1,255,255,255,255,255,0x15,0,0x24,0,0x0c,0,0x0d,0,0xe,0,0xd,0,0x10,0,0x11,0,0x1c,0,0x1d,0,0x1e,0,0x1f,0,0x25,0,0x20,0,0x26,0,0x27,0,0x28,0,0x29,0,0x2a,0,0x2b,0,0x2c,0,0x2d])


p=daiApi/Daikin(time=int(time.time()))


