import struct,copy,socket,collections,time
from scapy.all import *
EPOCH = time.mktime((1970, 1, 2, 0, 0, 0, 3, 1, 0))-86400

class StrFixedLenFieldFmt(StrField):
    __slots__ = ["length_from", "add_fmt", "get_fmt"]
    def __init__(self, name, default, length=None, length_from=None, add_fmt=lambda x:x, get_fmt=lambda x:x):
        StrField.__init__(self, name, default)
        self.length_from  = length_from
        if length is not None:
            self.length_from = lambda pkt,length=length: length
        self.add_fmt=add_fmt
        self.get_fmt=get_fmt
    def i2repr(self, pkt, v):
        if type(v) is str:
            v = v.rstrip("\0")
        return repr(v)
    def getfield(self, pkt, s):
        l = self.length_from(pkt)
        return s[l:], self.get_fmt(self.m2i(pkt,s[:l]))
    def addfield(self, pkt, s, val):
        l = self.length_from(pkt)
        return s+struct.pack("%is"%l,self.i2m(pkt, self.add_fmt(val)))
    def randval(self):
        try:
            l = self.length_from(None)
        except:
            l = RandNum(0,200)
        return RandBin(l)

class LEUTF16FixedLenField(StrFixedLenFieldFmt):
    def __init__(self, name, default, length=None, length_from=None, add_fmt=lambda x:x, get_fmt=lambda x:x):
        StrFixedLenFieldFmt.__init__(self, name, default, length, length_from, 
            add_fmt=lambda x:x.encode('utf-16-le'), 
            get_fmt=lambda x:x.decode('utf-16-le').rstrip('\x00'))


class LenField2(Field):
    __slots__ = ["adjust"]
    def __init__(self, name, default, fmt="H", adjust=lambda x: x):
        Field.__init__(self, name, default, fmt)
        self.adjust = adjust
    def i2m(self, pkt, x):
        if x is None:
            x = self.adjust(len(pkt.payload))
            print pkt, pkt.payload
        return x

class LEUTCTimeField(LEIntField):
    __slots__ = ["epoch", "delta", "strf", "use_nano"]
    def __init__(self, name, default=None, epoch=None, use_nano=False, strf="%a, %d %b %Y %H:%M:%S +0000"):
        if default is None:
            default=int(time.time())
        LEIntField.__init__(self, name, default)
        if epoch is None:
            mk_epoch = EPOCH
        else:
            mk_epoch = time.mktime(epoch)
        self.epoch = mk_epoch
        self.delta = mk_epoch - EPOCH
        self.strf = strf
        self.use_nano = use_nano
    def i2repr(self, pkt, x):
        if x is None:
            x = 0
        elif self.use_nano:
            x = x/1e9
        x = int(x) + self.delta
        t = time.strftime(self.strf, time.gmtime(x))
        return "%s (%d)" % (t, x)
    def i2m(self, pkt, x):
        return int(x) if x != None else 0


class DaikinApi(Packet):
    name = "Daikin HTTP call"
    fields_desc = [
        StrField("Header",
                "POST /cmd/ HTTP/1.1\r\n"
                "Content-Type: application/octet-stream\r\n"
                ,fmt="H"),
        StrField("Length",None,fmt="H"),
        StrField("end","\r\n\r\n",fmt="H"),
    ]
    def post_build(self, p, pay):
        if self.Length is None and pay:
            l = len(pay)
            p = p[:-4] + "Content-Length: " + str(l) + "\r\n\r\n"
        return p+pay


#                "Cache-Control: no-cache\r\n"
#                "Pragma: no-cache\r\n"
#                "User-Agent: Mozilla/4.0 (Windows 10 10.0) Java/1.8.0_152\r\n"
#                "Host: 192.168.9.92\r\n"
#                "Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2\r\n"
#                "Connection: keep-alive\r\n"


class DaikinHeader(Packet):
    name = "Daikin Base Packet"
    fields_desc = [
        LenField("length",32,fmt="<I"),
        LEIntField("command",0),
        LEIntField("id",0),
        LEUTCTimeField("time"),
        LEIntField("arg1",0),
        LEIntField("arg2",0),
        LEIntField("arg3",0),
        LEIntField("arg4",0),
    ]
    def post_build(self, p, pay):
        if pay:
            l = len(pay)
            p = struct.pack('<I',l+32) + p[4:]        
            return p+pay
        else:
            return p

class DaikinReqSetLogin(Packet):
    name = "Daikin Send Login info (60002) - set ID to IP address"
    fields_desc = [
        StrFixedLenField("username","admin",16),
        StrFixedLenField("password","daikin",16),
    ]

class DaikinRespSetLogin(Packet):
    name = "Daikin Send Login info (60003)"
    fields_desc = [
        FieldListField("zoneArray", None, LEIntField("zoneId",0), count_from=lambda pkt: pkt.underlayer.arg3),
    ]

class DaikinReqSetLogout(Packet):
    name = "Daikin Send Logout info (60004) - set ID to user ID"

class DaikinRespSetLogout(Packet):
    name = "Daikin Get Logout response (60005)"

class DaikinStructZoneProp(Packet):
    name = "Daikin struct for zone properties response (used in 60101)"
    fields_desc = [
        LEIntField("zoneId",0),
        LEIntField("iconId",0),
        LEUTF16FixedLenField("shortName","",16),
        LEUTF16FixedLenField("longName","",64),
    ]
    def extract_padding(self, p):
        return "", p

class DaikinReqGetZoneProp(Packet):
    name = "Daikin send GetZoneProp command (60100)"

class DaikinRespGetZoneProp(Packet):
    name = "Daiking getZoneProperties command response (60101)"
    fields_desc = [
        PacketListField("zoneArray", None, DaikinStructZoneProp, count_from=lambda pkt: pkt.underlayer.arg2),
    ]


class DaikinReqGetSysVersion(Packet):
    name = "Daikin send GetZoneProp command (60008)"
    fields_dsc = []


class DaikinRespGetSysVersion(Packet):
    name = "Daiking getZoneProperties command response (60009)"
    fields_desc = [
        StrFixedLenField("longVersion","",32),
    ]



class DaikinStructPntProp(Packet):
    name = "Daikin struct for zone properties response (used in 60103)"
    fields_desc = [
        LEIntField("id",0),
        LEIntField("portNumber",0),
        LEIntField("address",0),
        LEShortEnumField("pntType",0,
            {'100':'ZONE',
            '0':'UNKNOWN',
            '3':'CORE_DO',
            '4':'CORE_DI',
            '5':'CORE_PI',
            '1':'CORE_AI',
            '11':'CORE_AO',
            '6':'D3_DI',
            '7':'D3_DIO',
            '2':'D3_PI',
            '15':'D3_AI',
            '17':'D3_AO',
            '9':'D3_INNER',
            '8':'D3_OUTER',
            '10':'NLIGHT',
            '12':'RS485',
            '16':'PSEUDO_AI'}),
        LEShortEnumField("innerType",0,
            {'100': 'UNKNOWN',
            '0': 'NORMAL',
            '1': 'AIRHAN',
            '2': 'FFU',
            '3': 'VENT',
            '4': 'CHILLER'}),
        LEIntField("iconId",0),
        LEUTF16FixedLenField("shortName","",16),
        LEUTF16FixedLenField("longName","",64),
    ]
    def extract_padding(self, p):
        return "", p

class DaikinReqGetPntProp(Packet):
    name = "Daikin send ComGetPntProp command (60102)"
    fields_desc=[StrFixedLenField("filler","",64)]

class DaikinRespGetPntProp(Packet):
    name = "Daiking ComGetPntProp command response (60103)"
    fields_desc = [
        PacketListField("pntArray", None, DaikinStructPntProp, count_from=lambda pkt: pkt.underlayer.arg2),
    ]


class DaikinReqGetZonePnt(Packet):
    name = "Daikin send ComGetZonePnt command (60108)"
    # set zone ID to request in ID field of parent

class DaikinRespGetZonePnt(Packet):
    name = "Daiking ComGetZonePnt command response (60109)"
    fields_desc = [
        FieldListField("pntIdArray", None, LEIntField("pntId",0), count_from=lambda pkt: pkt.underlayer.arg2),
    ]


class LEIEEEFloatField(Field):
    def __init__(self, name, default):
        Field.__init__(self, name, default, "<f")

class DaikinStructPntState(Packet):
    name = "Daikin struct for pnt stateresponse (used in 60105)"
    fields_desc = [
        LEIntField("id",0),
        ByteField("type",0),
        ByteField("unk1",1),
        ByteField("enumComStat",0),
        ByteField("boolError",0),
        StrFixedLenField("errorString","",2),
        ByteField("unitNumber",0),
        ByteField("pntState",0),
        ByteField("complexStatus",0),
        ByteField("unk2",0),
        LEShortEnumField("enumDriveMode",0,{'1':'Fan','2':'Heat','4':'Cool','16':'Submit','32':'Vent','64':'Dry','512':'Autocool'}),
        LEShortEnumField("enumVentMode",0,{'1':'Auto','2':'Ventilation','4':'Normal'}),
        ByteField("boolFlags1",0),
        ByteField("boolFlags2",0),
        LEIEEEFloatField("tempSetPoint",0),
        LEIEEEFloatField("tempAmbient",0),
        ByteField("unk3",0),
        ByteField("unk4",0),
        LEShortEnumField("enumVentVol",0,{'1':'Auto','2':'Low','4':'High','8':'Auto (Fresh)','16':'Low (Fresh)','32':'High (Fresh)'}),
        LEShortField("unk5",0),
        LEShortField("unk6",0),
        LEShortField("unk7",0),
        ByteField("temp1Int",0),
        ByteField("temp1Dec",0),
        ByteField("temp2Int",0),
        ByteField("temp2Dec",0),
        ByteField("temp3Int",0),
        ByteField("temp3Dec",0),
        ByteField("temp4Int",0),
        ByteField("temp4Dec",0),
        ByteField("boolUnk",0),
        ByteField("unk8",0),
    ]
    def extract_padding(self, s):
        return '', s

class DaikinStructReqPntState(Packet):
    name = "Daikin struct for pnt stat request (used in 60104)"
    fields_desc = [
        LEIntEnumField("type",0,{'1':'zone','0':'pnt'}),
        LEIntField("id",0),
    ]
    def extract_padding(self, s):
        return '', s

class DaikinReqGetPntState(Packet):
    name = "Daikin send GetPntState command (60104)"
    # set zone ID to request in ID field of parent
    fields_desc = [
        FieldLenField("reqLength", None, count_of="reqIds", fmt="<I"),
        PacketListField("reqIds", None, DaikinStructReqPntState, count_from=lambda pkt: pkt.reqLength),
    ]

class DaikinRespGetPntState(Packet):
    name = "Daiking GetPntState command response (60105)"
    fields_desc = [
        PacketListField("pntStateArray", None, DaikinStructPntState, count_from=lambda pkt: pkt.underlayer.arg2),
    ]



def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

def sendP(host,packet):
    MAX_PACKET=32768
    s=socket.socket()
    s.settimeout(1)
    s.connect((host,80))
    s.send(bytes(packet))
    rdata = ''
    while True:
        try:
            data = s.recv(MAX_PACKET)
            if data:
                rdata +=data
            else:
                break
        except Exception, e:
            print e
            break
    s.close()
    return rdata[(rdata.find("\r\n\r\n")+4):]


bind_layers(DaikinHeader, DaikinReqSetLogin, command=60002)
bind_layers(DaikinHeader, DaikinRespSetLogin, command=60003)
bind_layers(DaikinHeader, DaikinReqSetLogout, command=60004)
bind_layers(DaikinHeader, DaikinRespSetLogout, command=60005)
bind_layers(DaikinHeader, DaikinReqGetZoneProp, command=60100)
bind_layers(DaikinHeader, DaikinRespGetZoneProp, command=60101)
bind_layers(DaikinHeader, DaikinReqGetPntProp, command=60102)
bind_layers(DaikinHeader, DaikinRespGetPntProp, command=60103)
bind_layers(DaikinHeader, DaikinReqGetZonePnt, command=60108)
bind_layers(DaikinHeader, DaikinRespGetZonePnt, command=60109)
bind_layers(DaikinHeader, DaikinReqGetPntState, command=60104)
bind_layers(DaikinHeader, DaikinRespGetPntState, command=60105)
bind_layers(DaikinHeader, DaikinReqGetSysVersion, command=60008)
bind_layers(DaikinHeader, DaikinRespGetSysVersion, command=60009)

bind_layers(DaikinApi, DaikinHeader)


