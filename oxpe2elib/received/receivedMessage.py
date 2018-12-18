'''
Created on 15 Sep 2017

@author: cheney
'''


import uuid
import json
import logging
import sys

#from oxpe2elib.channel.channel import Channel
#from oxpe2elib.channel.msg.message import Message
from oxpe2elib.channel.protocolType import ProtocolType
from oxpe2elib.channel.qosType import QosType
from oxpe2elib.channel.secType import SecurityType
from oxpe2elib.channel.gdprType import GdprType
from oxpe2elib.config import Config 

#from oxpe2elib.channel.channel import Channel
from oxpe2elib.channel.msg.message import Message

NONE = 0
CHANNEL = 1
MESSAGES = 2
IDENTITY = 3
LISTENER = 4
PINGER = 5
RECEIVER = 6
PROTOCOL = 7
ATTRIBUTES = 8


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
    
    
@Singleton
class ReceivedMessage():
    '''
    Decorated class to implement a Singleton design pattern.
    
    The class can have only one instance.
     
    f = Foo() # Error, this isn't how you get the instance of a singleton

    f = Foo.Instance() # Good. Being explicit is in line with the Python Zen
    g = Foo.Instance() # Returns already created instance

    print f is g # True

    From wikipedia:- 
    In software engineering, the singleton pattern is a software design pattern that restricts the instantiation of a class to 
    one object. This is useful when exactly one object is needed to coordinate actions across the system. The concept is 
    sometimes generalized to systems that operate more efficiently when only one object exists, or that restrict the 
    instantiation to a certain number of objects. The term comes from the mathematical concept of a singleton.
    
    There are some who are critical of the singleton pattern and consider it to be an anti-pattern in that it is 
    frequently used in scenarios where it is not beneficial, introduces unnecessary restrictions in situations where a 
    sole instance of a class is not actually required, and introduces global state into an application.


    this works with Listener to capture a message pushed from the broker down to here.
    This is called by the protocol's callbacks and the received data is passed into here. From here
    it gets put into an appropriate structure of channel/message/protocol, where message is header plus body.
    '''


    def __init__(self):
        '''
        Constructor to receive messages from the listener
        '''
        # at constructor set variables that will have global scope across modules
        objConfig = Config.Instance()
        self.incomingMessageBuffer = []
        # this controls the handling of the callbacks
        self.loopCallbackReceivedFlag = False


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
    
    
    
    def pollBuffer(self, objClient, friendlyName):
        '''
        This is for the version that requires an application to ask for data that might or might not be present.
        It says whether or not there is any data waiting.
        '''
        if len(self.incomingMessageBuffer) == 0:
            dataAvailableFlag = False
        else:
            dataAvailableFlag = True
        
        return dataAvailableFlag
    
    
    def popBuffer(self, objClient, friendlyName):
        '''
        This is for the version that requires an application to ask for 
        data that might or might not be present.
        Return data to the application when it asks for it.
        '''
        eofFlag = False
        while not eofFlag:
            try:
                # read thru the list of records in the self.incomingMessageBuffer until empty
                if len(self.incomingMessageBuffer) == 0:
                    eofFlag = True
                    raise BufferError ("buffer is empty - this is a valid situation")
                # TODO proper iteration thru the buffer is required here
                #for message in incoming_messages:
                # pop(0) is effectively a dequeue rather than a pop
                dictFlags, dictMetaHdr, dictPayload, dictMetaPayload = self.__understandMessage(self.incomingMessageBuffer.pop(0))    
            except ValueError as e:
                logging.error("ERROR - unable to understand received data - valueerror %s", e)
                dictFlags = {} 
                dictMetaHdr = {}
                dictPayload = {}
                dictMetaPayload = {}
                pass
            except BufferError as e:
                logging.debug("DEBUG - end of buffer - want more data")
                eofFlag = True
                dictFlags = {} 
                dictMetaHdr = {}
                dictPayload = {}
                dictMetaPayload = {}
                pass
            except:
                logging.error("ERROR - error returning received data - error is - %s", sys.exc_info()[0])
                return False
        
        # some of this data consists of empty dictionaries depending on whether it is header or body
        return dictFlags, dictMetaHdr, dictPayload, dictMetaPayload
    
    def setDataFromCallback(self, message):
        '''
        For both versions, receive a callback from the protocol client.
        Currently only for the mqtt client.
        '''
        self.incomingMessageBuffer.append(message)
        
        return True
    
    
    def getDataFromCallback(self):
        # return all of the data
        return self.incomingMessageBuffer
    
    
    def emptyDataFromCallback(self):
        self.incomingMessageBuffer = []
        return True
    

    def setLoopCallbackReceivedFlag(self, value):
        '''
        For both versions, receive a callback from the protocol client.
        Currently only for the mqtt client.
        '''
        self.loopCallbackReceivedFlag = value
        
        return True
        
    
    
    def __unpackMsg(self, friendlyName):
        '''
        '''

        return True
#        return msgFlags, msgSenderId, msgFriendlyName, msgMessage, msgTimeSent, msgTimeReceived


    def __understandMessage(self, mqttTypeMessage):

        # extract the payload from the mqtt message which has a rather complicated structure to it.
        jsonReceivedProtocolData = mqttTypeMessage.payload.decode()
        
        # we check only part of the received data to start with so that we can decide which protocol is in use,  
        # which stream is being received and whether this is a stream header or body
        # Later in this method the entire received data is sent to be completely unpacked which means that
        # some data will be unpacked twice
        try:
            # TODO the returned stuff is either boolean or dictionary - this check is not correct but should work ok
            intermediate = self.__decodeJson(jsonReceivedProtocolData)
            if intermediate == False:
                candidateMeta = {}
            else:
                candidateMeta = self.__uncompressReceived(intermediate)
        except:
            logging.error("ERROR - failure to interpret received data on initial check - error is - %s", sys.exc_info()[0])
            raise ValueError ("ERROR - failure to interpret received data on initial check ")

        try:
            transport, candidateSender, candidateFriendlyName = self.__preliminaryUnpackCandidateMeta(candidateMeta)
        except:
            logging.error("ERROR - failure to unpack received data on initial check - error is - %s", sys.exc_info()[0])
            raise ValueError ("ERROR - failure to unpack received data on initial check")
        
        # if we can't see a name then it is assumed to be not a header record i.e. it is a body
        if candidateFriendlyName is not None:
            # process as a HDR record
            #TODO bodge to skip bugs
            return {}, {}, {}, []
            logging.debug("DEBUG - found HDR record in stream")
            channelSeen = False
            # TODO this needs to be the hostname
            toNode = ""
            try:
                # this will check whether or not the stream has been seen before and
                # will create new dictionary for it if not seen. It also stores some info about it
                # Usually we would not expect to see the same header record twice
                channelSeen = self.queryChannel(candidateFriendlyName)
            except:
                logging.debug("DEBUG - channel not seen previously")
                channelSeen = False
                pass
            
            if not channelSeen:
                try:
                    # TODO this overwrites all of the dictionaries to blank - not correct...
                    channelNew = Channel(toNode, transport, candidateFriendlyName)
#                    channelNew = self.initRoot(toNode, transport, candidateFriendlyName)                   
                    channelNew.receiveChannel(self, toNode, candidateSender, transport, candidateFriendlyName)
                    newMessage = Message(candidateFriendlyName)
                except:
                    logging.error("ERROR - could not store the channel details")
                    raise ValueError ("ERROR - could not store the channel details")
                
            try:
                dictFlags, dictMetaHdr = newMessage.receivedProcessHeader(jsonReceivedProtocolData)
            except:
                logging.error("ERROR - cannot process HDR record")
                raise ValueError ("ERROR - cannot process HDR record")
            else:
                # all ok so pass back data with appropriate nulls so that calling procedure
                # knows what is what
                return dictFlags, dictMetaHdr, {}, {}
        else:
            # process as a BODY record
            logging.debug("DEBUG - found BODY record in stream")
            #TODO bodge to skip bugs
            return {}, {}, {}, []
            try:
                dictPayload, dictMetaPayload = newMessage.receivedProcessBody(jsonReceivedProtocolData)
            except:
                logging.error("ERROR - cannot process BODY record")
                raise ValueError ("ERROR - cannot process BODY record")
            else:
                # all ok so pass back data with appropriate nulls so that calling procedure
                # knows what is what
                return {}, {}, dictPayload, dictMetaPayload
            
    
        # should never reach here so fail it        
        raise ValueError ("ERROR - program logic error in __understandMessage")
    
            
            
        
        

    def __decodeJson(self, jsonReceivedProtocolData):
        try:
            jsonHdrMeta = json.loads(jsonReceivedProtocolData)
            #logging.debug("json header metadata is " + jsonHdrMeta)
        except:
            logging.error("ERROR - failure of json.dumps on received data initial check - error is - %s", sys.exc_info()[0])
            return False
            
#        logging.debug("json data for header payload is " + jsonHdrMeta)
        return jsonHdrMeta

    
    
    def __uncompressReceived(self, jsonCompressedProtocolData):
        '''
        not currently in use 
        '''
        # TODO put in decompression here
        return jsonCompressedProtocolData
    
    
        
    def __preliminaryUnpackCandidateMeta(self, candidateMeta):
        # set to bad value to force a lookup failure when dropping thru
        candidateProtocolType = 99
        try:
            # attempt to extract protocolType information
            candidateHdr = candidateMeta[unicode("meta")]
            candidateFlags = candidateHdr[unicode("flags")]
            candidateProtocolType = candidateFlags[unicode("prt")]
        except:
            # it might or might not be a BODY record if not found
            logging.debug("DEBUG - protocol not found in HDR template for mqtt")
            pass
        
        # set to a default value to instantiate the receiving variable as that enum Type
        transport = ProtocolType.PROTO_NONE
        try:
            transport = ProtocolType.reverseLookup(candidateProtocolType)
        except:
            logging.debug("DEBUG - protocol not translated for HDR template for mqtt")
            # assume this is a BODY record rather than a HDR record
            pass
        
        # TODO we cannot assume messages arrive in the correct sequence
        # but i do not have the time to write complicated stream error handling 
        # so assume everything is how we would like it to be
        
        try:
            # attempt to extract sender and friendlyName information
            candidateHdr = candidateMeta[unicode("meta")]
            candidateID = candidateHdr[unicode("id")]
            # nested dictionary here
            candidateSender = candidateID[unicode("sndr")]
            candidateFriendlyName = candidateID[unicode("name")]
            logging.debug("DEBUG - extracted sender and friendlyName OK for HDR template for mqtt - assuming a HDR record")
        except:
            logging.debug("DEBUG - could not extract sender and friendlyName for HDR template for mqtt - assuming a BODY record")
            candidateSender = None
            candidateFriendlyName = None
        
        return transport, candidateSender, candidateFriendlyName
    

    def __queryChannel(self, candidateFriendlyName):
        if candidateFriendlyName in self.listChannel:
            return True
        else:
            return False


    def __responseBrokerReachable(self, friendlyName):
        '''
        Before sending data we have to check whether or not the broker is reachable.
        This is the response leg.
        '''
        
#        networkDown = False
#        if
#        return True
        return True 

    
   