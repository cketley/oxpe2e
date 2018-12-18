'''
Created on 5 Oct 2017

@author: cheney
'''
from enum import Enum, unique     # for enum34, or the stdlib version
@unique
class ProtocolType(Enum):
    # under no circumstances alter these values or names !!! 
    # the numbers must match the java enum which is positional not numbered.
    # altering the placeholder dummies so that they have new names with the same value is OK 
    # so long as the changes are rippled out to all progs using it.
    # deleting values or names is not allowed under any circumstances.
    # you have been warned !!!
    PROTO_MQTT = 1
    PROTO_HTTP = 2
    PROTO_BLE = 3
    PROTO_B = 4
    PROTO_LORA = 5
    PROTO_LORAWAN = 6
    PROTO_COAP = 7
    PROTO_ZIGBEE = 8
    PROTO_SIGFOX = 9
    PROTO_DDS = 10
    PROTO_6LOWPAN = 11
    PROTO_THREAD = 12
    PROTO_HALOW = 13
    PROTO_2G = 14
    PROTO_3G = 15
    PROTO_4G = 16
    PROTO_LTECAT0 = 17
    PROTO_LTECAT1 = 18
    PROTO_LTECAT3 = 19
    PROTO_ZWAVE = 20
    PROTO_LTEM1 = 21
    PROTO_NBIOT = 22
    PROTO_NFC = 23
    PROTO_RFID = 24
    PROTO_DIGIMESH = 25
    PROTO_INGENU = 26
    PROTO_WEIGHTLESSN = 27 
    PROTO_WEIGHTLESSP = 28
    PROTO_WEIGHTLESSW = 29
    PROTO_ANT = 30
    PROTO_ANTPLUS = 31
    PROTO_MIWI = 32
    PROTO_ENOCEAN = 33
    PROTO_DASH7 = 34
    PROTO_WIRELESSHART = 35
    PROTO_RPC = 36
    PROTO_KAFKA = 37
    PROTO_JMS = 38
    PROTO_AMQP = 39
    PROTO_RABBITMQ = 40
    PROTO_ACTIVEMQ = 41
    PROTO_ZEROMQ = 42
    PROTO_ICE = 43
    PROTO_CORBA = 44
    PROTO_THRIFT= 45
    PROTO_GOOGLE_PBUFF = 46
    PROTO_ZOOKEEPER = 47
    PROTO_GO = 48
    PROTO_PLACEHOLDER_08 = 49
    PROTO_PLACEHOLDER_09 = 50
    PROTO_PLACEHOLDER_10 = 51
    PROTO_PLACEHOLDER_11 = 52
    PROTO_PLACEHOLDER_12 = 53
    PROTO_PLACEHOLDER_13 = 54
    PROTO_PLACEHOLDER_14 = 55
    PROTO_PLACEHOLDER_15 = 56
    PROTO_PLACEHOLDER_16 = 57
    PROTO_PLACEHOLDER_17 = 58
    PROTO_PLACEHOLDER_18 = 59
    PROTO_PLACEHOLDER_19 = 60
    PROTO_PLACEHOLDER_20 = 61
    PROTO_PLACEHOLDER_21 = 62
    PROTO_PLACEHOLDER_22 = 63
    PROTO_PLACEHOLDER_23 = 64
    PROTO_PLACEHOLDER_24 = 65
    PROTO_PLACEHOLDER_25 = 66
    PROTO_PLACEHOLDER_26 = 67
    PROTO_PLACEHOLDER_27 = 68
    PROTO_PLACEHOLDER_28 = 69
    PROTO_PLACEHOLDER_29 = 70
    PROTO_PLACEHOLDER_30 = 71
    PROTO_BRIDGE = 997
    PROTO_IP_ONLY = 998
    PROTO_NONE = 999
    
    @classmethod
    def reverseLookup(cls, value):
        for _, member in cls.__members__.items():
            if member.value == value:
                return member
                raise LookupError
            
            
