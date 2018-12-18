#coding=utf-8
# NB we need to declare the code format so we can use multinational characters

import logging
import time
import json

import socket

import sys
from zlib import adler32
import base64

#from oxpe2elib.channel import channel
from oxpe2elib.channel.channel import Channel
#from oxpe2elib.channel.identity import Identity
from oxpe2elib.listener.listener import Listener
#from oxpe2elib.channel.pingService import PingService
from oxpe2elib.received.receivedMessage import ReceivedMessage
#from oxpe2elib.channel.msg.message import Message



from oxpe2elib.config import Config

from oxpe2elib.channel.qosType import QosType
from oxpe2elib.channel.gdprType import GdprType
from oxpe2elib.channel.protocolType import ProtocolType
from oxpe2elib.channel.secType import SecurityType

from oxpe2elib.channel.msg.protocol.mqtt.mqttClient import MqttClient
from oxpe2elib.channel.msg.protocol.mqtt.mqttSmartAgent import MqttSmartAgent
from oxpe2elib.channel.msg.protocol.mqtt.mqttBrokerServices import MqttBrokerServices

from oxpe2elib.channel.msg.protocol.lorawan.loraClient import LoraClient
from oxpe2elib.channel.msg.protocol.http.httpClient import HttpClient
from oxpe2elib.channel.msg.protocol.ble.bleClient import BleClient
from oxpe2elib.channel.msg.protocol.sigfox.sigfoxClient import SigfoxClient


logging.basicConfig(level=logging.DEBUG)

logging.debug("starting mf2cDemoBobFromAlice")

STATUS_CONNECTED = "C"
STATUS_DISCONNECTED_GRACE = "DG"
STATUS_DISCONNECTED_UNGRACE = "DU"
HUB = 'broker_services'


if __name__ == "__main__":
    
    # get the hostname in fqdn format in all situations even if hosts file is not fqdn.
    # nb windows behaves differently to linux
    # ubuntu behaves differently to redhat
    if socket.getfqdn().find('.')>=0:
        myHostname=socket.getfqdn()
    else:
        myHostname=socket.gethostbyaddr(socket.gethostname())[0]

    logging.info('hostname is ' + str(myHostname))

    

    
    
#######################################################################################        

    # sync callback
    # poll for data without blocking
    
    # the name of the stream is supplied by the sender
    # We use the time as an ID to initially bind things together until the real name
    # becomes known 
    # We use the time instead of a random id because it is a little quicker to do
    friendlyName = unicode(time.ctime())

    # at program startup instantiate the Listener object and constructor
    objListener = Listener()
    
    # ReceivedMessage is a Singleton. This is so that we can find it. 
    # The data received has no sense of what it belongs to therefore ReceivedMessage object doesnt either.
    # It stores a list of messages and updates the dictionary of dictionaries that 
    # describes the structure of the transactions.
    objReceivedMessage = ReceivedMessage.Instance()
    
    
    # Instantiate a Singleton that stores cross-application variables
    # They are used mostly in the callbacks.
    objConfig = Config.Instance()
     
    
    #  .
    #  .
    #  .
    #  .
    #  .
    #  .
        
    # set the type of protocol and assign it to a variable that is passed into the module as a python Type
    # use ProtocolType.reverseLookup(yourVariable) to translate backwards from an integer value 
    # that you've received inwards from the module to get back to a an enum by assigning it 
    # using reverseLookup to a variable that then takes on the python Type for this particular Enum Type
    # for example
    #   # tempry = 3
    #   # newProtocol = ProtocolType.reverseLookup(tempry)
    #   # logging.debug("DEBUG - newProtocol is %s", newProtocol)
    #   # > DEBUG - newProtocol is ProtocolType.PROTO_BLE
    transport = ProtocolType.PROTO_MQTT
    
    # this creates the client name used by mqtt
    # It has to be different for each stream and between end/start of streams otherwise mqtt will
    # get stuck doing disconnnect/reconnect cycles
    clientId = "unknown" + "001"
    # these are params to the individual client setups
    dictParams = {}
    dictProtoMqtt = {}
    # TODO edit the broker name - was 95
    dictProtoMqtt = {
        "source" : clientId,
        "dest" : myHostname,
        "broker" : "changeMe",
        "port" : 1883,
        "protoVer" : "3.1",
        "oldtimestamp" : str(int(time.time())),
        "timeout" : 300,
        "anotherParam" : "0001",
        "RcvdMsg" : objReceivedMessage
        }
    dictProtoHttp = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictProtoBLE = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictProtoLoRa = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictProtoSigfox = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictParams[ProtocolType.PROTO_MQTT] = dictProtoMqtt
    dictParams[ProtocolType.PROTO_HTTP] = dictProtoHttp
    dictParams[ProtocolType.PROTO_BLE] = dictProtoBLE
    dictParams[ProtocolType.PROTO_LORA] = dictProtoLoRa
    dictParams[ProtocolType.PROTO_SIGFOX] = dictProtoSigfox

    # this will call the constructor that preps the topics but does not subscribe to them yet
    functions = {
        ProtocolType.PROTO_MQTT: MqttSmartAgent, 
        ProtocolType.PROTO_LORA: LoraClient,
        ProtocolType.PROTO_HTTP: HttpClient,
        ProtocolType.PROTO_SIGFOX: SigfoxClient,
        ProtocolType.PROTO_BLE: BleClient
        }
    if transport in functions:
        try:
            objClient = functions[transport]( dictParams[transport] )
        except TypeError as e:
            logging.error("ERROR - could not initialise the protocol - typeerror %s", e)
            exit(0)
        except ValueError as e:
            logging.error("ERROR - could not initialise the protocol - valueerror %s", e)
            exit(0)
        except AttributeError as e:
            logging.error("ERROR - could not initialise the protocol - attributeerror %s", e)
            exit(0)
        except:
            logging.error("ERROR - could not initialise the protocol")
            exit(0)
    else:
        logging.error("ERROR - attempt to call unknown protocol")
        exit(0)

    # do some initial setup of the protocol
    # most protocols don't do anything in the initial setup   
    # the way i am doing this is not very Dry but i want to keep the code similar throughout     
    functions = {
        ProtocolType.PROTO_MQTT: objClient.setup, 
        ProtocolType.PROTO_LORA: objClient.setup,
        ProtocolType.PROTO_HTTP: objClient.setup,
        ProtocolType.PROTO_SIGFOX: objClient.setup,
        ProtocolType.PROTO_BLE: objClient.setup
        }
    if transport in functions:
        try:
            functions[transport]( dictParams[transport] )
        except TypeError as e:
            logging.error("ERROR - could not do setup for the protocol - typeerror %s", e)
            exit(0)
        except ValueError as e:
            logging.error("ERROR - could not do setup for the protocol - valueerror %s", e)
            exit(0)
        except AttributeError as e:
            logging.error("ERROR - could not do setup for the protocol - attributeerror %s", e)
            exit(0)
        except:
            logging.error("ERROR - could not do setup for the protocol")
            exit(0)
    else:
        logging.error("ERROR - attempt to call unknown protocol")
        exit(0)

    #  .
    #  .
    #  .
    #  .
    # in the program body do other app logic...
    #  .
    #  .
    #  .
    #  .
    # in the program body poll for data received
    #
    try:
        # we do not know what type of message might be waiting so no need for passing anything
        objListener.poll(objReceivedMessage, objClient, friendlyName)
    except ValueError as e:
        logging.debug("DEBUG - listener says nothing is available")
        pass
    except:
        logging.error("ERROR - listener reported an error on check for data available - %s", sys.exc_info()[0])
        exit(0)
    else:
        # data is available so retrieve it
        # This is not the standard way to handle mqtt but is used for compatibility with other
        # protocols
        try:
            # we do not know what type of message might be waiting so no need for passing anything
            # Don't get confused by the name - it's a dequeue not a pop
            dictFlags, dictMetaHdr, dictPayload, dictMetaPayload = objListener.pop(objReceivedMessage, objClient, friendlyName)
        except ValueError as e:
            logging.error("ERROR - listener says nothing is available but earlier said there was - valueerror %s", sys.exc_info()[0])
            exit(0)
        except:
            logging.error("ERROR - listener reported an error on dequeue of data - %s", sys.exc_info()[0])
            exit(0)
        else:
            # do whatever you want with the data
            logging.debug("DEBUG - data received is %s", dictPayload)
            pass
            
    
    
    



#######################################################################################        

    # async callback
    # set up a callback then go into a loop that will terminate only on a received callback
    
    # the name of the stream is supplied by the sender
    # We use the time as an ID to initially bind things together until the real name
    # becomes known 
    # We use the time instead of a random id because it is a little quicker to do
    friendlyName = unicode(time.ctime())

    # at program startup instantiate the Listener object and constructor
    objListener = Listener()

    # ReceivedMessage is a Singleton. This is so that we can find it. 
    # The data received has no sense of what it belongs to therefore ReceivedMessage object doesnt either.
    # It stores a list of messages and updates the dictionary of dictionaries that 
    # describes the structure of the transactions.
    objReceivedMessage = ReceivedMessage.Instance()
    
    # Instantiate a Singleton that stores cross-application variables
    # They are used mostly in the callbacks.
    objConfig = Config.Instance()

    #  .
    #  .
    #  .
    #  .
    #  .
    #  .
    # in the program body set up a callback
    
    # set the type of protocol and assign it to a variable that is passed into the module as a python Type
    # use ProtocolType.reverseLookup(yourVariable) to translate backwards from an integer value 
    # that you've received inwards from the module to get back to a an enum by assigning it 
    # using reverseLookup to a variable that then takes on the python Type for this particular Enum Type
    # for example
        # tempry = 3
        # newProtocol = ProtocolType.reverseLookup(tempry)
        # logging.debug("DEBUG - newProtocol is %s", newProtocol)
        # > DEBUG - newProtocol is ProtocolType.PROTO_BLE
    transport = ProtocolType.PROTO_MQTT
    # this creates the client name used by mqtt
    # It has to be different for each stream and between end/start of streams otherwise mqtt will
    # get stuck doing disconnnect/reconnect cycles
    clientId = "unknown" + "002"

    # these are params to the individual client setups
    dictParams = {}
    dictProtoMqtt = {}
    # TODO edit the broker name - was 95
    dictProtoMqtt = {
        "source" : clientId,
        "dest" : myHostname,
        "broker" : "changeMe",
        "port" : 1883,
        "protoVer" : "3.1",
        "oldtimestamp" : str(int(time.time())),
        "timeout" : 300,
        "anotherParam" : "0001",
        "RcvdMsg" : objReceivedMessage
        }
    dictProtoHttp = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictProtoBLE = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictProtoLoRa = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictProtoSigfox = {
        "source" : clientId,
        "dest" : myHostname,
        }
    dictParams[ProtocolType.PROTO_MQTT] = dictProtoMqtt
    dictParams[ProtocolType.PROTO_HTTP] = dictProtoHttp
    dictParams[ProtocolType.PROTO_BLE] = dictProtoBLE
    dictParams[ProtocolType.PROTO_LORA] = dictProtoLoRa
    dictParams[ProtocolType.PROTO_SIGFOX] = dictProtoSigfox

    # this will call the constructor that preps the topics but does not subscribe to them yet
    functions = {
        ProtocolType.PROTO_MQTT: MqttSmartAgent, 
        ProtocolType.PROTO_LORA: LoraClient,
        ProtocolType.PROTO_HTTP: HttpClient,
        ProtocolType.PROTO_SIGFOX: SigfoxClient,
        ProtocolType.PROTO_BLE: BleClient
        }
    if transport in functions:
        try:
            objClient = functions[transport]( dictParams[transport] )
        except TypeError as e:
            logging.error("ERROR - could not initialise the protocol - typeerror %s", e)
            exit(0)
        except ValueError as e:
            logging.error("ERROR - could not initialise the protocol - valueerror %s", e)
            exit(0)
        except AttributeError as e:
            logging.error("ERROR - could not initialise the protocol - attributeerror %s", e)
            exit(0)
        except:
            logging.error("ERROR - could not initialise the protocol")
            exit(0)
    else:
        logging.error("ERROR - attempt to call unknown protocol")
        exit(0)

    # do some initial setup of the protocol
    # most protocols don't do anything in the initial setup   
    # the way i am doing this is not very Dry but i want to keep the code similar throughout     
    functions = {
        ProtocolType.PROTO_MQTT: objClient.setup, 
        ProtocolType.PROTO_LORA: objClient.setup,
        ProtocolType.PROTO_HTTP: objClient.setup,
        ProtocolType.PROTO_SIGFOX: objClient.setup,
        ProtocolType.PROTO_BLE: objClient.setup
        }
    if transport in functions:
        try:
            functions[transport]( dictParams[transport] )
        except TypeError as e:
            logging.error("ERROR - could not do setup for the protocol - typeerror %s", e)
            exit(0)
        except ValueError as e:
            logging.error("ERROR - could not do setup for the protocol - valueerror %s", e)
            exit(0)
        except AttributeError as e:
            logging.error("ERROR - could not do setup for the protocol - attributeerror %s", e)
            exit(0)
        except:
            logging.error("ERROR - could not do setup for the protocol")
            exit(0)
    else:
        logging.error("ERROR - attempt to call unknown protocol")
        exit(0)

    #  .
    #  .
    #  .
    #  .
    # in the program body do other app logic...
    #  .
    #  .
    #  .
    #  .
    # somewhere in the program... drop into an infinite loop that terminates on a flag to receive
    # the callback

    # This controls how often you sleep before checking the loopCallbackReceivedFlag
    # Smaller values are faster and so use more processor resources
    processingSpeed = 0.1
    
    objReceivedMessage.loopCallbackReceivedFlag = False
        
    while not objReceivedMessage.loopCallbackReceivedFlag:
        # loop here as a way to wait for a callback from mqtt to occur
        # It is blocking and async
        time.sleep(processingSpeed)
        # nothing is done here except doing a blocking wait for a callback from mqtt
        
    # we have data waiting in a buffer so process it
    try:
        # we do not know what type of message might be waiting so no need for passing anything
        objListener.poll(objReceivedMessage, objClient, friendlyName)
    except ValueError as e:
        logging.debug("DEBUG - listener says nothing is available")
        pass
    except:
        logging.error("ERROR - listener reported an error on check for data available - %s", sys.exc_info()[0])
        exit(0)
    else:
        # data is available so retrieve it
        # This is not the standard way to handle mqtt but is used for compatibility with other
        # protocols
        try:
            # we do not know what type of message might be waiting so no need for passing anything
            # Don't get confused by the name - it's a dequeue not a pop
            dictFlags, dictMetaHdr, dictPayload, dictMetaPayload = objListener.pop(objReceivedMessage, objClient, friendlyName)
        except ValueError as e:
            logging.error("ERROR - listener says nothing is available but earlier said there was - valueerror %s", sys.exc_info()[0])
            exit(0)
        except:
            logging.error("ERROR - listener reported an error on dequeue of data - %s", sys.exc_info()[0])
            exit(0)
        else:
            # do whatever you want with the data
            logging.debug("DEBUG - data received is %s", dictPayload)
            pass
            
    #  .
    #  .
    #  .
    #  .
    #  .
    # destructors
    
    
        
    
#######################################################################################        

    
    
    # TODO bodge to get around bugs
    exit(1)
    # query the channel header record 
           
    try:
        chan = Channel()
        transport, toNode, fromNode = chan.getChannel(friendlyName)
        print("this channel is from %s to %s using protocol %s", fromNode, toNode, transport.value)
        listChans = chan.getChannelList()
        print("channels seen are %s", listChans)
    except ValueError as e:
        logging.debug("DEBUG - channel says nothing is available")
        pass
    except:
        logging.error("ERROR - channel reported an error on check for data available - %s", sys.exc_info()[0])
        exit(0)
    




