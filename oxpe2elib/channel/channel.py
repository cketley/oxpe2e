'''
Created on 15 Sep 2017

@author: cheney
'''


from enum import Enum     # for enum34, or the stdlib version

import logging

from oxpe2elib.channel.protocolType import ProtocolType
from oxpe2elib.channel.qosType import QosType
from oxpe2elib.channel.secType import SecurityType
from oxpe2elib.channel.gdprType import GdprType
from oxpe2elib.channel.msg.message import Message
#from oxpe2elib.channel.identity import Identity
#from oxpe2elib.listener.listener import Listener
#from oxpe2elib.channel.pingService import PingService
#from oxpe2elib.received.receivedMessage import ReceivedMessage

from oxpe2elib.channel.msg.protocol.mqtt.mqttClient import MqttClient
from oxpe2elib.channel.msg.protocol.mqtt.mqttSmartAgent import MqttSmartAgent
from oxpe2elib.channel.msg.protocol.mqtt.mqttBrokerServices import MqttBrokerServices

from oxpe2elib.channel.msg.protocol.lorawan.loraClient import LoraClient
from oxpe2elib.channel.msg.protocol.http.httpClient import HttpClient
from oxpe2elib.channel.msg.protocol.ble.bleClient import BleClient
from oxpe2elib.channel.msg.protocol.sigfox.sigfoxClient import SigfoxClient

from oxpe2elib.channel.msg.protocol.protocol import Protocol

from oxpe2elib.config import Config
from oxpe2elib.channel.identity import Identity
from oxpe2elib.received.receivedMessage import ReceivedMessage



import time
import socket
import sys
#from oxpe2elibDemoAlice2Bob.oxpe2elibDemoAlice2Bob import friendlyName

NONE = 0
CHANNEL = 1
MESSAGES = 2
IDENTITY = 3
LISTENER = 4
PINGER = 5
RECEIVER = 6
PROTOCOL = 7
ATTRIBUTES = 8
   
class Channel:
    
    '''
    
    '''
     
    def __init__(self, toNode, transport, friendlyName):
        '''
        Constructor
        '''

        logging.debug('Instance created for the channel')
        
        self.__initRoot(toNode, transport, friendlyName)
        transport = self.transport
        # this is the root that holds everything in a dictionary of dictionaries plus list
        fromNode = ""
        self.__prepChannel(toNode, fromNode, transport, friendlyName)        
        self.__prepProtocol(toNode, fromNode, transport, friendlyName)        

        self.sendRoot[friendlyName] = self.dictChannel
                
        return None
    
    
    
        
    def __initRoot(self, toNode, transport, friendlyName):
        
        # create the empty structures that the following methods will populate.
        # The receiveRoot lives in the receivedMessage object.
        self.sendRoot = {}
        # this is a dictionary of the channels in use
        self.dictChannel = {}
        # this holds a list of channels
        self.listChannel = []
        self.dictChanAttributes = {}
        self.dictMessages = {}
        self.dictProtocols = {}
        
        # init the instance variable to NOT match the Type of the flag 
        self.transport = ProtocolType.PROTO_NONE.value
        try:
            self.transport = transport
        except TypeError as e:
            logging.debug("ERROR - typeerror on flag handling - %s", e)
        except ValueError as e:
            logging.debug("ERROR - valueerror on flag handling - %s", e)
        except:
            logging.debug("ERROR - some problem on flag handling - %s", sys.exc_info()[0])
            return False
        else:
            logging.debug("INFO - all OK - no problem on flag handling - %s", sys.exc_info()[0])
            
        # TODO this isn't right
        # put the dictionaries for messages and protocols into the channel list
        # only one protocol per message at the moment
        self.dictMessages[friendlyName] = self.dictProtocols
        
        # this is just for convenience when querying for all known channels
        self.listChannel.append(friendlyName)
        # insert the attributes dictionary into the channels list
        self.dictChannel[ATTRIBUTES] = self.dictChanAttributes

        return True
    
    
    
        
    def flushChannel(self):
        return True
        
        

    def destructorChannel(self, transport, friendlyName):
        ''' 
        use this from the app to terminate the channel gracefully
        '''
        # destroy the transactions
        
        
        # destroy the protocol specific stuff
        functions = {
            ProtocolType.PROTO_MQTT: self.objClient.clean_up, 
            ProtocolType.PROTO_LORA: self.objClient.clean_up,
            ProtocolType.PROTO_HTTP: self.objClient.clean_up,
            ProtocolType.PROTO_SIGFOX: self.objClient.clean_up,
            ProtocolType.PROTO_BLE: self.objClient.clean_up
            }

        if transport in functions:
            try:
                functions[transport]()
            except:
                logging.error("ERROR - could not terminate the protocol - %s", sys.exc_info()[0])
        else:
            logging.error("ERROR - attempt to call unknown protocol on destructor")
            return False

        # destroy this one channel and its attributes
        self.dictChannel[friendlyName] = None
        
        logging.debug('DEBUG - dictionary dictChannel for the channel has been destroyed')

        return True
        
        



    def __prepChannel(self, toNode, fromNode, transport, friendlyName ):
        '''
        private method to build a channel
        called on first send
        '''

        # build a dictionary of attributes
        self.dictChanAttributes={}
        self.dictChanAttributes['channelName'] = friendlyName
        self.dictChanAttributes['channelTo'] = toNode
        self.dictChanAttributes['channelFrom'] = fromNode
        self.dictChanAttributes['channelPreferred'] = transport
        
        # insert the dictionary containing attributes into the list for the channel
        self.dictChannel[ATTRIBUTES] = self.dictChanAttributes
        
        # instantiate the Identity object
        self.objMessage = Message(friendlyName)
        try:
            # the interpreter throws an error here but i think it is ok really
            self.objIdentity = Identity.Instance()
        except TypeError as e:
            logging.error("ERROR - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - unknown error- %s", sys.exc_info()[0])
            return False
        else:
            logging.info("INFO - all OK no error")
            
#        self.objListener = Listener(friendlyName)
#        self.objPinger = PingService(friendlyName)
        self.objReceivedMessage = ReceivedMessage.Instance()
        
        # Instantiate a Singleton that stores cross-application variables
        # They are used mostly in the callbacks.
        self.objConfig = Config.Instance()

        return True


    def __prepProtocol(self, toNode, fromNode, transport, friendlyName ):
        '''
        private method to build a channel
        called on first send
        '''
        
        # instantiate for some of the protocols
        if socket.getfqdn().find('.')>=0:
            myHostname=socket.getfqdn()
        else:
            myHostname=socket.gethostbyaddr(socket.gethostname())[0]
            
        # these are params to the individual client setups
        dictParams = {}
        dictProtoMqtt = {}
        dictProtoMqtt = {
            "sess" : myHostname,
            "dest" : toNode,
            "broker" : "v95.example.com",
            "port" : 1883,
            "protoVer" : "3.1",
            "oldtimestamp" : str(int(time.time())),
            "timeout" : 20,
            "anotherParam" : "0001",
            "RcvdMsg" : self.objReceivedMessage
            }
        dictProtoHttp = {
            "sess" : myHostname,
            "dest" : toNode,
            }
        dictProtoBLE = {
            "sess" : myHostname,
            "dest" : toNode,
            }
        dictProtoLoRa = {
            "sess" : myHostname,
            "dest" : toNode,
            }
        dictProtoSigfox = {
            "sess" : myHostname,
            "dest" : toNode,
            }
        try:
            dictParams[ProtocolType.PROTO_MQTT] = dictProtoMqtt
            dictParams[ProtocolType.PROTO_HTTP] = dictProtoHttp
            dictParams[ProtocolType.PROTO_BLE] = dictProtoBLE
            dictParams[ProtocolType.PROTO_LORA] = dictProtoLoRa
            dictParams[ProtocolType.PROTO_SIGFOX] = dictProtoSigfox
        except:
            logging.error("ERROR - could not store dictionary to the protocol- %s", sys.exc_info()[0])
            return False
            

        # instantiating the Protocol also instantiates the Client
        self.objProtocol = Protocol(dictParams, transport, friendlyName)

                        
        functions = {
            ProtocolType.PROTO_MQTT: MqttSmartAgent, 
            ProtocolType.PROTO_LORA: LoraClient,
            ProtocolType.PROTO_HTTP: HttpClient,
            ProtocolType.PROTO_SIGFOX: SigfoxClient,
            ProtocolType.PROTO_BLE: BleClient
            }
        if transport in functions:
            try:
                self.objClient = functions[transport]( dictParams[transport] )
            except TypeError as e:
                logging.error("ERROR - could not initialise the protocol - typeerror %s", e)
                return False
            except ValueError as e:
                logging.error("ERROR - could not initialise the protocol - valueerror %s", e)
                return False
            except AttributeError as e:
                logging.error("ERROR - could not initialise the protocol - attributeerror %s", e)
                return False
            except:
                logging.error("ERROR - could not initialise the protocol- %s", sys.exc_info()[0])
                return False
        else:
            logging.error("ERROR - attempt to call unknown protocol")
            return False

        # we are storing the instance that handles the messages here, not the messages themselves
        self.dictChannel[MESSAGES] = self.objMessage
        self.dictChannel[PROTOCOL] = self.objProtocol
        # currently we don't do anything with these
#        self.dictChannel[IDENTITY] = self.objIdentity
#        self.dictChannel[LISTENER] = self.objListener
#        self.dictChannel[PINGER] = self.objPinger
#        self.dictChannel[RECEIVER] = self.objReceiver

        # do some initial setup of the protocol
        # most protocols don't do anything in the initial setup   
        # the way i am doing this is not very Dry but i want to keep the code similar throughout     
#        functions = self.objClient.setup
        functions = {
            ProtocolType.PROTO_MQTT: self.objClient.setup, 
            ProtocolType.PROTO_LORA: self.objClient.setup,
            ProtocolType.PROTO_HTTP: self.objClient.setup,
            ProtocolType.PROTO_SIGFOX: self.objClient.setup,
            ProtocolType.PROTO_BLE: self.objClient.setup
            }
        if transport in functions:
            try:
                functions[transport]( dictParams[transport] )
            except TypeError as e:
                logging.error("ERROR - could not do setup for the protocol - typeerror %s", e)
                return False
            except ValueError as e:
                logging.error("ERROR - could not do setup for the protocol - valueerror %s", e)
                return False
            except AttributeError as e:
                logging.error("ERROR - could not do setup for the protocol - attributeerror %s", e)
                return False
            except:
                logging.error("ERROR - could not do setup for the protocol- %s", sys.exc_info()[0])
                return False
        else:
            logging.error("ERROR - attempt to call unknown protocol")
            return False
        
#        try:
#            self.sendChannelHdr(payload, flags, friendlyName)
#        except:
#            logging.error("ERROR - could not send header for the channel")
#            return False
        
        return True
        
        
    def getChannel(self,friendlyName):
        '''
        use this to query the channel about its state
        '''
        dictTempChanAttributes = self.dictChannel[ATTRIBUTES]
        
        toNode = dictTempChanAttributes['channelTo'] 
        fromNode = dictTempChanAttributes['channelFrom']
        transport = dictTempChanAttributes['channelPreferred'] 
        
        return transport, toNode, fromNode

    
    def getChannelList(self):
        '''
        use this to query the channel about all known channel names
        '''

        return self.listChannel

    
    def setChannel(self, friendlyName):
        ''' 
        use this to force a channel into some state
        '''
        # TODO not currently implemented
        return None
 


    def sendChannel(self, destination, utf8DictPayload, utf8DictFlags, utf8FriendlyName):
        
        # translate user input into unicode to match json and also for code security (misinterpretation of canonical forms)

        # this is double-encoded into unicode in case the user forgets to do it.
        friendlyName = unicode(utf8FriendlyName)

        try:
            dictFlags = {
                unicode("prt") : unicode(utf8DictFlags["prt"]), 
                unicode("qos") : unicode(utf8DictFlags["qos"]),
                unicode("sec") : unicode(utf8DictFlags["sec"]),
                unicode("prv") : unicode(utf8DictFlags["prv"])
                }
    
            dictPayload = {
                unicode('snt') : unicode(utf8DictPayload["snt"]),
                unicode('sz') : unicode(utf8DictPayload["sz"]),         # length of data before uuencode or zipping
                unicode('szu') : unicode(utf8DictPayload["szu"]),       # length of data after base64 uuencode
                unicode('szc') : unicode(0),                            # not yet calculated so always zero - after zipping
                unicode('sze') : unicode(0),                            # not yet calculated so always zero - after encryption
                unicode('cks') : unicode("unknown"),                           # not yet calculated so always null - checksum
                unicode('dat'): utf8DictPayload["dat"]  # dont unicode this because it could be very large and anyway its in uuencode format
                }
        except:
            logging.error("ERROR - invalid user input")
            return False

        try:
            unicodeTransport = dictFlags[unicode("prt")]
            transport = ProtocolType.reverseLookup(int(unicodeTransport.decode('utf-8')))           
        except:
            logging.error("ERROR - could not reverse lookup transport protocol enum")
            return False

        try:
            self.objMessage.sendMsg(destination, self.objProtocol, self.objClient, dictPayload, dictFlags, transport, friendlyName)
        except:
            logging.error("ERROR - could not send a message")
            return False
        
        return True
    
    
    def sendChannelHdr(self, destination, utf8DictMetaHdr, utf8DictFlags, utf8FriendlyName):
        
        # translate user input into unicode to match json and also for code security (misinterpretation of canonical forms)
        
        # this is double-encoded into unicode in case the user forgets to do it.
        friendlyName = unicode(utf8FriendlyName)
        
        dictFlags = {
            unicode("prt") : unicode(utf8DictFlags["prt"]), 
            unicode("qos") : unicode(utf8DictFlags["qos"]),
            unicode("sec") : unicode(utf8DictFlags["sec"]),
            unicode("prv") : unicode(utf8DictFlags["prv"])
            }
        
        # build the stream header
        # schema version for this layout is version 0.1.0
        # "ver" : version number of the schema as x.y.z format
        # "sndr" : sender as fqdn
        # "name" : the friendly name assigned to the channel
        dictMetaHdr = {
            unicode("ver") : unicode(utf8DictMetaHdr["ver"]),
            unicode("sndr") : unicode(utf8DictMetaHdr["sndr"]),
            unicode("name") : unicode(utf8DictMetaHdr["name"])
            }

        try:
            unicodeTransport = dictFlags[unicode("prt")]
            transport = ProtocolType.reverseLookup(int(unicodeTransport.decode('utf-8')))           
        except:
            logging.error("ERROR - could not reverse lookup transport protocol enum")
            return False
        try:
            self.objMessage.sendMsgHdr(destination, self.objProtocol, self.objClient, dictMetaHdr, dictFlags, transport, friendlyName)
        except:
            logging.error("ERROR - could not send a message for stream header")
            return False
        
        return True
    
    
    def receiveChannel(self, toNode, fromNode, transport, candidateFriendlyName):
        '''
        this must be non-blocking because the application expects it to be
        '''
        # when we first receive a message we assign it a temporary dummy friendlyName
        # but here we assign it the name we have got from the message.
        # We should avoid saving the dummy friendlyName because we somehow 
        # would have to get rid of it later
        try:
            # lookup of the channel 
            # not found will cause the creation of a new channel
            dictTemporaryChannel = self.sendRoot[candidateFriendlyName]
            # TODO this is COMPLETELY WRONG            
            self.dictProtocols = self.dictMessages[candidateFriendlyName] 
            self.dictChanAttributes = self.dictChannel[ATTRIBUTES] 
        except:
            logging.debug("DEBUG - channel name not seen before - storing new channel")
            self.dictChannel[candidateFriendlyName] = self.listChannel.append(candidateFriendlyName)
            self.__prepChannel(toNode, fromNode, transport, candidateFriendlyName) 
        
        return True
    

#    def receiveChannelHdr(self, payload, dictFlags, friendlyName):
#        '''
#        this must be non-blocking because the application expects it to be
#        '''
# 
#         # lookup the stream header information and give it to the app
#        # We assume that data is not out of order with body arriving before header.
#        # Which is a dangerous assumption
#        # TODO handle out of order data
#        dictFlags, dictMetaHdr, 
#        # This returns the stream header with the stream payload so that app can decide what to do next

 
    
   
    def __receiveMsg(self, friendlyName):
        
        listBuiltMetadata = []
        listBuiltPayload = []
        
        
        return listBuiltMetadata, listBuiltPayload
    
    
    def __makePayload(self, payload, friendlyName):
        
        return True

    
    def __makeMetadata(self, flags, friendlyName):
        
        return True
    
    
    
    def __activateChannel(self, friendlyName):
        '''
        private method - use this if you know the network connection has come back up or is no longer faulty
        '''
        
        workChannelID = self.dictChannel[friendlyName]

        self.dictChannel[friendlyName] = workChannelID
        return True


    def __deactivateChannel(self, friendlyName):
        '''
        private method - use this if you know the network connection is going to be dropped or is faulty
        '''

        self.dictChannel[friendlyName] = None
        return True

    def __housekeepingChannel(self, friendlyName):
        ''' 
        private method - use this to clean up dead channels
        '''
        return True

#    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    logging.debug('class Channel')
#    
#    exit(1)

