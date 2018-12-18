'''
Created on 15 Sep 2017

@author: cheney
'''

#from oxpe2elib.channel.channel import ProtocolType

from oxpe2elib.channel.protocolType import ProtocolType
from oxpe2elib.channel.qosType import QosType
from oxpe2elib.channel.secType import SecurityType
from oxpe2elib.channel.gdprType import GdprType


from oxpe2elib.channel.msg.message import Message

from oxpe2elib.channel.msg.protocol.mqtt.mqttClient import MqttClient
from oxpe2elib.channel.msg.protocol.mqtt.mqttSmartAgent import MqttSmartAgent
from oxpe2elib.channel.msg.protocol.mqtt.mqttBrokerServices import MqttBrokerServices

from oxpe2elib.channel.msg.protocol.lorawan.loraClient import LoraClient
from oxpe2elib.channel.msg.protocol.http.httpClient import HttpClient
from oxpe2elib.channel.msg.protocol.ble.bleClient import BleClient
from oxpe2elib.channel.msg.protocol.sigfox.sigfoxClient import SigfoxClient

import uuid
import sys
import logging
import json

# logging defined in the Channel class

class Protocol:

    '''
    classdocs
    '''


    def __init__(self, dictParams, transport, friendlyName):
        '''
        Constructor
        '''
        # TODO dont think this is required because all it does is run setup for the client but that is explicitly done in Channel
#        objProto = self.prepTransport( dictParams, transport)
        
        return None
        
        
    def prepTransport(self, dictParams, transport):
        
        functions = {
            ProtocolType.PROTO_MQTT: MqttSmartAgent.setup, 
            ProtocolType.PROTO_LORA: LoraClient.setup,
            ProtocolType.PROTO_HTTP: HttpClient.setup,
            ProtocolType.PROTO_SIGFOX: SigfoxClient.setup,
            ProtocolType.PROTO_BLE: BleClient.setup
            }

        if transport in functions:
            try:
                functions[transport]( dictParams[transport] )
            except TypeError as e:
                logging.error("ERROR - could not call setup for the protocol - typeerror %s", e)
                return False
            except ValueError as e:
                logging.error("ERROR - could not call setup for the protocol - valueerror %s", e)
                return False
            except AttributeError as e:
                logging.error("ERROR - could not call setup for the protocol - attributeerror %s", e)
                return False
            except:
                logging.error("ERROR - could not call setup for the protocol- %s", sys.exc_info()[0])
                return False
        else:
            logging.error("ERROR - attempt to call unknown protocol on setup")
            return False

        return True
    
    
        
    def protocolSend(self, destination, objClient, jsonPayload, dictFlags, transport, friendlyName):
        
        # this is for non-blocking Sends only
        # a later version of this prog will handle the blocking sends

        # extract security and qos flags for use by mqtt client, not the security infrastructure
        # the payload contains the security infrastructure which is a wrapper around the original data 
        try:
            toNode = destination
#            dictMeta = json.loads(jsonMetadata)
#            tempMeta = dictMeta[unicode("meta")]
#            tempMeta2 = tempMeta[unicode("flags")]
#            unicodeQos = tempMeta2[unicode("qos")]
#            unicodeSecurity = tempMeta2[unicode("sec")]
            unicodeQos = dictFlags[unicode("qos")]
            qos = int(unicodeQos.decode('utf-8'))     
            unicodeSecurity = dictFlags[unicode("sec")]
            security = int(unicodeSecurity.decode('utf-8'))     
        except:
            logging.error("ERROR - problem extracting flags before send to protocol client- %s", sys.exc_info()[0])
            return False        
        
        # NB for mqtt we are sending this to the client not the wrapper for the client
        functions = {
            ProtocolType.PROTO_MQTT: objClient.send, 
            ProtocolType.PROTO_LORA: objClient.send,
            ProtocolType.PROTO_HTTP: objClient.send,
            ProtocolType.PROTO_SIGFOX: objClient.send,
            ProtocolType.PROTO_BLE: objClient.send
            }
        clientRecipients = []
        clientRecipients.append(toNode) 
#        security = SecurityType.reverseLookup(int(unicodeSecurity.decode('utf-8')))     

        if transport in functions:
            try:
                functions[transport]( clientRecipients, jsonPayload, security, qos )
            except:
                logging.error("ERROR - could not send to the protocol client- %s", sys.exc_info()[0])
                return False
        else:
            logging.error("ERROR - attempt to call unknown protocol on send to protocol client")
            return False
            
        
        return True
    
    def protocolListen(self):
        return True
    
    def protocolReceive(self):
        return True
