#coding=utf-8
# NB we need to declare the code format so we can use multinational characters

import logging
import time
import json

import socket

import sys
from zlib import adler32
import base64

from oxpe2elib.channel import channel
from oxpe2elib.channel.channel import Channel
from oxpe2elib.channel.channel import QosType
from oxpe2elib.channel.channel import GdprType
from oxpe2elib.channel.channel import ProtocolType
from oxpe2elib.channel.channel import SecurityType

logging.basicConfig(level=logging.DEBUG)

logging.debug("starting oxpe2eDemoAlice2Bob")



__version__ = "0.1"
__status__ = "Pre-Alpha"


if __name__ == "__main__":
    
    # get the hostname in fqdn format in all situations even if hosts file is not fqdn.
    # nb windows behaves differently to linux
    # ubuntu behaves differently to redhat
    if socket.getfqdn().find('.')>=0:
        myHostname=socket.getfqdn()
    else:
        myHostname=socket.gethostbyaddr(socket.gethostname())[0]

    logging.info('hostname is ' + str(myHostname))

    port = 1883
    




#######################################################################################        

    # NB i have put a diacritical o character in the name (Galician for stream) because this software must be multinational
    # But note that you have to put it into unicode format because otherwise you get this error thrown
    # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 4: ordinal not in range(128)
    friendlyName = u'bobCórrego01'
    
    # set the type of protocol and assign it to a variable that is passed into the module as a python Type
    # Use ProtocolType.reverseLookup(yourVariable) to translate backwards from an integer value 
    # that you've received inwards from the module to get back to a an enum by assigning it 
    # using reverseLookup to a variable that then takes on the python Type for this particular Enum Type
    # For example
    #   tempry = 3
    #   newProtocol = ProtocolType.reverseLookup(tempry)
    #   logging.debug("DEBUG - newProtocol is %s", newProtocol)
    #   > DEBUG - newProtocol is ProtocolType.PROTO_BLE
    transport = ProtocolType.PROTO_MQTT
    # force values for flags for the example program
    # NB we are storing the value of the enum here not the Type    
    protoEnum = ProtocolType.PROTO_MQTT
    secEnum = SecurityType.FLAG_SEC_PROTECTED
    qosEnum = QosType.FLAG_QOS_ATLEASTONCE
    gdprEnum = GdprType.FLAG_PRIV_NOTPII

    # we assume that all fqdns are not unicode
    destination = "v92.example.com"

    logging.debug("before create Channel")
    
    # create the channel
    try:
        bobChannel01 = Channel(destination, transport, friendlyName)
    except TypeError as e:
        logging.error("ERROR - unable to open a channel - typeerror %s", e)
        exit(0)
    except AttributeError as e:
        logging.error("ERROR - unable to open a channel - attributeerror %s", e)
        exit(0)
    except:
        logging.error("ERROR - unable to open a channel - unknownerror %s", sys.exc_info()[0])
        exit(0)

    
    # convert enums into a format that can interface between java, go, c and python etc
    secValue = secEnum.value
    qosValue = qosEnum.value
    protoValue = protoEnum.value
    gdprValue = gdprEnum.value
    
    # build the flags
    # NB we put keys for the dictionary into unicode as well because json will mangle everything out into unicode Type not str Type
    # and that becomes a problem because we pass across dictionaries as params
    dictFlags = {
        "prt" : protoValue, 
        "qos" : qosValue,
        "sec" : secValue,
        "prv" : gdprValue
        }
    
    # build the stream header
    # schema version for this layout is version 0.1.0
    # "ver" : version number of the schema as x.y.z format
    # "sndr" : sender as fqdn
    # "name" : the friendly name assigned to the channel
    dictMetaHdr = {
        "ver" : "0.1.0",
        "sndr" : "v60.example.com",
        "name" : friendlyName
        }
        
    # send the stream header
    try:
        status = bobChannel01.sendChannelHdr(destination, dictMetaHdr, dictFlags, friendlyName)
        if not status:
            logging.error("ERROR - unable to send header for the channel - userwarning")
            raise UserWarning
    except:
        logging.error("ERROR - unable to send header for the channel")
        exit(0)
    
    
    
    
    # send a message to the channel
    temporaryData = "Hello to Bob from Alice's Computer"
    # we uuencode the data because it might have characters that confuse python dictionary format
    # we can't trap malicious output here because it's trivial to change this program to not do the check
    b64payload = base64.b64encode(temporaryData)
    # schema version for this layout is version 0.1.0
    # 'snt' : datetime this message was sent in ccyymmddThhmmssZ format
    # 'sz' : size of data before uuencode or zipping
    # 'szu' : size after uuencode base64
    # 'szc' : size after compress
    # 'sze' : size after encryption
    # 'cks' : checksum in adler32 format
    # 'dat': data in any format NB user app is responsible for knowing its format and tracking schema version numbers 

    dictPayload = {
        'snt' : str(int(time.time())),
        'sz' : len(temporaryData),       # length of data before uuencode or zipping
        'szu' : len(b64payload),
        'cks' : adler32(temporaryData),
        'dat': b64payload  # dont unicode this because it could be very large and anyway its in uuencode format
        }
    try:
        status = bobChannel01.sendChannel(destination, dictPayload, dictFlags, friendlyName)
        if not status:
            logging.error("ERROR - unable to send the message - userwarning")
            raise UserWarning
    except:
        logging.error("ERROR - unable to send the message")
        exit(0)
    
    
    


    
    # send another message to the channel    
    temporaryData = "temperature readings follow:-"
    # we uuencode the data because it might have characters that confuse python dictionary format
    # we can't trap malicious output here because it's trivial to change this program to not do the check
    b64payload = base64.b64encode(temporaryData)
    # schema version for this layout is version 0.1.0
    # 'snt' : datetime this message was sent in ccyymmddThhmmssZ format
    # 'sz' : size of data before uuencode or zipping
    # 'szu' : size after uuencode base64
    # 'szc' : size after compress
    # 'sze' : size after encryption
    # 'cks' : checksum in adler32 format
    # 'dat': data in any format NB user app is responsible for knowing its format and tracking schema version numbers 

    dictPayload = {
        'snt' : str(int(time.time())),
        'sz' : len(temporaryData),       # length of data before uuencode or zipping
        'szu' : len(b64payload),
        'cks' : adler32(temporaryData),
        'dat': b64payload  # dont unicode this because it could be very large and anyway its in uuencode format
        }
    try:
        status = bobChannel01.sendChannel(destination, dictPayload, dictFlags, friendlyName)
        if not status:
            logging.error("ERROR - unable to send the message - userwarning")
            raise UserWarning
    except:
        logging.error("ERROR - unable to send the message")
        exit(0)





    # send another message to the channel    
    temporaryData = str(36.9)
    # we uuencode the data because it might have characters that confuse python dictionary format
    # we can't trap malicious output here because it's trivial to change this program to not do the check
    b64payload = base64.b64encode(temporaryData)
    # schema version for this layout is version 0.1.0
    # 'snt' : datetime this message was sent in ccyymmddThhmmssZ format
    # 'sz' : size of data before uuencode or zipping
    # 'szu' : size after uuencode base64
    # 'szc' : size after compress
    # 'sze' : size after encryption
    # 'cks' : checksum in adler32 format
    # 'dat': data in any format NB user app is responsible for knowing its format and tracking schema version numbers 

    dictPayload = {
        'snt' : str(int(time.time())),
        'sz' : len(temporaryData),       # length of data before uuencode or zipping
        'szu' : len(b64payload),
        'cks' : adler32(temporaryData),
        'dat': b64payload  # dont unicode this because it could be very large and anyway its in uuencode format
        }
    try:
        status = bobChannel01.sendChannel(destination, dictPayload, dictFlags, friendlyName)
        if not status:
            logging.error("ERROR - unable to send the message - userwarning")
            raise UserWarning
    except:
        logging.error("ERROR - unable to send the message")
        exit(0)





    # send another message to the channel    
    temporaryData = str(37.0)
    # we uuencode the data because it might have characters that confuse python dictionary format
    # we can't trap malicious output here because it's trivial to change this program to not do the check
    b64payload = base64.b64encode(temporaryData)
    # schema version for this layout is version 0.1.0
    # 'snt' : datetime this message was sent in ccyymmddThhmmssZ format
    # 'sz' : size of data before uuencode or zipping
    # 'szu' : size after uuencode base64
    # 'szc' : size after compress
    # 'sze' : size after encryption
    # 'cks' : checksum in adler32 format
    # 'dat': data in any format NB user app is responsible for knowing its format and tracking schema version numbers 

    dictPayload = {
        'snt' : str(int(time.time())),
        'sz' : len(temporaryData),       # length of data before uuencode or zipping
        'szu' : len(b64payload),
        'cks' : adler32(temporaryData),
        'dat': b64payload  # dont unicode this because it could be very large and anyway its in uuencode format
        }
    try:
        status = bobChannel01.sendChannel(destination, dictPayload, dictFlags, friendlyName)
        if not status:
            logging.error("ERROR - unable to send the message - userwarning")
            raise UserWarning
    except:
        logging.error("ERROR - unable to send the message")
        exit(0)





    # send another message to the channel    
    temporaryData = str(0b0100010101110110011001010111001000100000011101110110000101101110011101000010000001110100011011110010000001110011011001010110111001100100001000000110000101101110001000000110010101101110011000110110111101100100011001010110010000100000011011010110010101110011011100110111001101100001011001110110010100100000011101000110100001100001011101000010000001101111011011100110110001111001001000000110000100100000011010000110000101101110011001000110011001110101011011000010000001101111011001100010000001110000011001010110111101110000011011000110010100100000011000110110000101101110001000000110000101100011011101000111010101100001011011000110110001111001001000000110001101110010011000010110001101101011001000000111010001101000011001010010000001100011011011110110010001100101001111110010000001010111011001010110110001101100001011000010000001101100011011110110111101101011001000000110111001101111001000000110011001110101011100100111010001101000011001010111001000111011001000000110110101111001001000000110001001110010011000010110100101101110001000000110100001110101011100100111010000100000011101110110100001100101011011100010000001001001001000000110110101100001011001000110010100100000011010010111010000100000011000010110111001100100001000000100100100100000011100110111010001101001011011000110110000100000011010000110000101110110011001010010000001100001001000000111001101101100011010010110011101101000011101000010000001101000011000010110111001100111011011110111011001100101011100100010111000101110001011100010000001110011011011110010110000100000011001010110111001101010011011110111100100100001)
    # we uuencode the data because it might have characters that confuse python dictionary format
    # we can't trap malicious output here because it's trivial to change this program to not do the check
    b64payload = base64.b64encode(temporaryData)
    # schema version for this layout is version 0.1.0
    # 'snt' : datetime this message was sent in ccyymmddThhmmssZ format
    # 'sz' : size of data before uuencode or zipping
    # 'szu' : size after uuencode base64
    # 'szc' : size after compress
    # 'sze' : size after encryption
    # 'cks' : checksum in adler32 format
    # 'dat': data in any format NB user app is responsible for knowing its format and tracking schema version numbers 

    dictPayload = {
        'snt' : str(int(time.time())),
        'sz' : len(temporaryData),       # length of data before uuencode or zipping
        'szu' : len(b64payload),
        'cks' : adler32(temporaryData),
        'dat': b64payload  # dont unicode this because it could be very large and anyway its in uuencode format
        }
    try:
        status = bobChannel01.sendChannel(destination, dictPayload, dictFlags, friendlyName)
        if not status:
            logging.error("ERROR - unable to send the message - userwarning")
            raise UserWarning
    except:
        logging.error("ERROR - unable to send the message")
        exit(0)






    # close the channel
    try:
        status = bobChannel01.destructorChannel(transport, friendlyName)
        if not status:
            logging.error("ERROR - unable to close the channel - userwarning")
            raise UserWarning
    except:
        logging.error("ERROR - unable to close the channel")
        exit(0)
    else:
        logging.debug("DEBUG - normal completion of program")
        exit(1)
    
    
##############################





 