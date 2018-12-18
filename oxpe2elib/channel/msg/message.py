'''
Created on 28 Sep 2017

@author: cheney
'''

import logging
from valideer.validators import String, Integer

import json
import base64
import valideer as V
import re
import sys
import unicodedata

from oxpe2elib.channel.protocolType import ProtocolType
from oxpe2elib.channel.qosType import QosType
from oxpe2elib.channel.secType import SecurityType
from oxpe2elib.channel.gdprType import GdprType



class Message():
    '''
    classdocs
    '''


    def __init__(self, friendlyName):
        '''
        Constructor
        '''
        self.__beginMsg(friendlyName)
        
        
    def __beginMsg(self, friendlyName):
        self.__prepStats(friendlyName)
        return True


    def sendMsg(self, destination, objProtocol, objClient, dictPayload, dictFlags, transport, friendlyName):
        
        # the payload input has some metadata in front of the data
        # input is python dictionary
        # output is json
        # TODO this doesnt work 
#        try:
#            self.__sanitiseSent(dictPayload, friendlyName)
#        except:
#            logging.warning("WARNING - unsanitary input detected on send of message")
#            return False
        
        # data is already in base64 format
        # the payload data is encrypted but the payload metadata is not, it's clear-signed
        try:
            compressedPayload = self.__compressMsg(self.__makePayload(dictPayload))
            compressedPayloadSize = len(compressedPayload)
        except:
            logging.error("ERROR - failure of compression when sending payload")
            return False
        
        try:
            encryptedPayload = self.__encryptPayload(compressedPayload)
            encryptedPayloadSize = len(encryptedPayload)
            jsonEncryptedPayload = json.dumps(encryptedPayload)
        except:
            logging.error("ERROR - failure of encryption when sending payload")
            return False
        
        jsonDictMetaPayload = json.dumps(self.__makePayloadMeta(dictPayload, compressedPayloadSize, encryptedPayloadSize))
        try: 
            # this clearsigns a json structure containing the metadata
            jsonSignedPayloadMeta = json.dumps(self.__clearsignMetadata(jsonDictMetaPayload))
        except:
            logging.error("ERROR - failure of clear-sign on sending payload")
            return False
        
        # this glues together two chunks that are already json
        jsonPayload = self.__encodeJson(jsonSignedPayloadMeta, jsonEncryptedPayload)
        logging.debug("json data for payload is " + jsonPayload)
        try:
            self.__callProtoSend( destination, objProtocol, objClient, jsonPayload, dictFlags, transport, friendlyName )
        except:
            logging.error("ERROR - unable to call the send of the message")
            return False
        
        return True
    
    
    def sendMsgHdr(self, destination, objProtocol, objClient, dictMetaHdr, dictFlags, transport, friendlyName):
        
        # send the metadata as the first item in the stream
        # input is python dictionary
        # output is json
        # TODO this doesnt work 
#        try:
#            self.__sanitiseSentHdr(dictMetaHdr, dictFlags, friendlyName)
#        except:
#            logging.warning("WARNING - unsanitary input detected on send of message")
#            return False
        
        try: 
            signedMetaHdr = self.__clearsignMetadata(self.__makeMetadataHdr(dictMetaHdr, dictFlags, friendlyName))
        except:
            logging.error("ERROR - failure of clear-sign on sending of header metadata")
            return False
        try:
            jsonPayload = self.__encodeJsonHdr(signedMetaHdr)
        except:
            logging.error("ERROR - failure of json encode of header metadata")
            return False
        try:
            self.__callProtoSend( destination, objProtocol, objClient, jsonPayload, dictFlags, transport, friendlyName )
        except:
            logging.error("ERROR - unable to call the send of the message header")
            return False
        
        return True



    


    
    def receiveMsg(self, dictPayload, dictMetadata, friendlyName):
        return True
    
    
    
        
    def __prepStats(self,friendlyName):
        bytes_sent = 0
        bytes_received = 0
        warnings_detected = 0
        errors_detected = 0
        messages_sent = 0
        messages_received = 0
        
        return True

    def __headerReceiveMsg(self, dummy, dictMetadata, friendlyName):
        return True

        
    def __sanitiseSent(self, dictPayload, friendlyName):
        
        try:
            self.__checkSanitarinessOfPayloadMeta(dictPayload)
        except:
            logging.error("ERROR - unsanitary data detected in meta dictionary of BODY record")
            return False
        
        
        try:
            self.__checkSanitarinessOfPayloadData(dictPayload)
        except:
            logging.error("ERROR - unsanitary data detected in data dictionary of BODY record")
            return False
                
        return True
        
        
    def __checkSanitarinessOfPayloadMeta(self, dictPayload):
             
        # check that bad guys haven't put dangerous content into the input
        # we can't trap malicious output here because it's trivial to change this program to not do the check

        try:
        # dictPayload is a python dictionary
        # check the content is the right format for the schema
#        adapt_sent = V.parse({"+snt" : [V.AdaptTo(String)]})
            payload_schema = {
                "+snt" : [V.AdaptTo(String)],
                "+sz" : [V.AdaptTo(Integer)],
                "+szu" : [V.AdaptTo(Integer)],
                "+szc" : [V.AdaptTo(Integer)],
                "+sze" : [V.AdaptTo(Integer)],
                "+cks" : [V.AdaptTo(String)],
                "+dat" : "string",    ### should be in uuencode format i.e. alphanumerics
                }

#        payload_schema = {
#            V.parse({"+snt" : [V.AdaptTo(String)]}),
#            V.parse({"+sz" : [V.AdaptTo(Integer)]}),
#            V.parse({"+szu" : [V.AdaptTo(Integer)]}),
#            V.parse({"+szc" : [V.AdaptTo(Integer)]}),
#            V.parse({"+sze" : [V.AdaptTo(Integer)]}),
#            V.parse({"+cks" : [V.AdaptTo(String)]}),
#            "+dat" : "string",    ### should be in uuencode format i.e. alphanumerics
#            }
            
#        payload_schema = {
#            "+snt": "datetime",
#            "+sz": V.Range("number", min_value=0),
#            "+szu": V.Range("number", min_value=0),
#            "+szc": V.Range("number", min_value=0),
#            "+sze": V.Range("number", min_value=0),
#            "+cks": "string",
#            "+dat" : "string",    ### should be in uuencode format i.e. alphanumerics
#            }
            validator = V.parse(payload_schema)
#        dictValidatePayload = {
#            "snt": int(unicodeQos.decode('utf-8')),
#            "sz": ,
#            "szu": ,
#            "szc": ,
#            "sze": ,
#            "cks": ,
#            "dat" : ,    ### should be in uuencode format i.e. alphanumerics
#            
#            }
#        (int(unicodeQos.decode('utf-8')))
            validator.validate(dictPayload)
        except V.ValidationError as e:
            logging.error("ERROR - invalid data format in dictionary to send - %s", e)
            return False
        except:
            logging.error("ERROR - invalid data format in dictionary to send - %s", sys.exc_info()[0])
            return False
        
        return True
    
    

    def __checkSanitarinessOfPayloadData(self, dictPayload):
                
        payloadFieldData = dictPayload['dat']  # data is not in unicode it is in uuencode
        if re.sub(r'[^a-fA-F0-9]','', payloadFieldData) is None:  # check payload data contains only hex chars
            pass
        else:
            logging.error("ERROR - data must be base64 encoded in payload for send")
            return False
        
        # it's input and it's important so we sanitise it
        # TODO cant get this to work right so leaving it out for now
#        if re.match('^[\w-]+$', friendlyName) is not None:   # check friendlyName is only alphanumerics and underscore and hyphen from start to end
#            pass
#        else:
#            logging.error("ERROR - friendlyName must be alphanumeric, hyphen or underscore in send")
#            return False
           
        return True

    def __sanitiseSentHdr(self, dictMetaHdr, dictFlags, friendlyName):
        # check that bad guys haven't put dangerous content into the input
        # we can't trap malicious output here because it's trivial to change this program to not do the check
        
        try:
            self.__checkSanitarinessOfID(dictMetaHdr)
        except:
            logging.error("ERROR - unsanitary data detected in ID dictionary of HDR")
            return False
        
        
        try:
            self.__checkSanitarinessOfFlags(dictFlags)
        except:
            logging.error("ERROR - unsanitary data detected in Flags dictionary of HDR")
            return False
        
        return True
    
    
        
    def __checkSanitarinessOfID(self, dictMetaHdr): 
        
        
        try:
        # dictMetaHdr is a python dictionary
        # check the content is the right format for the schema
            header_schema = {
                "+ver" : [V.AdaptTo(String)],
                "+sndr" : [V.AdaptTo(String)],
                "+name" : [V.AdaptTo(String)],
    #            "+ver": "string",
    #            "+sndr": "string",
    #            "+name": "string",
            }

#                header_schema = {
#            V.parse({"+ver" : [V.AdaptTo(String)]}),
#            V.parse({"+sndr" : [V.AdaptTo(String)]}),
#            V.parse({"+name" : [V.AdaptTo(String)]}),
##            "+ver": "string",
##            "+sndr": "string",
##            "+name": "string",
#        }
            validator = V.parse(header_schema)
            if validator.is_valid(dictMetaHdr):
                pass
            else:
                logging.error("ERROR - schema layout incorrect in send header")
                return False
        except V.ValidationError as e:
            logging.error("ERROR - schema layout incorrect in send header - %s", e)
            return False
        except TypeError as e:
            logging.error("ERROR - schema layout incorrect in send header - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - schema layout incorrect in send header - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - schema layout incorrect in send header - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - schema layout incorrect in send header - error is - %s", sys.exc_info()[0])
            return False
        
        # cant get this to work right so leaving it out for now
#        try:
#            try:
#                tempMatch = unicodedata.normalize('NFC',friendlyName)
#            except:
#                pass
#            
#            if re.match(r'^[^\w-]+$', str(tempMatch)) is not None:   # check it is only alphanumerics and underscore and hyphen from start to end
#                pass
#            else:
#                logging.error("ERROR - friendlyName must be alphanumeric, hyphen or underscore in send")
#                return False
#        except TypeError as e:
#            logging.error("ERROR - friendlyName must be alphanumeric, hyphen or underscore in send - typeerror %s", e)
#            return False
#        except ValueError as e:
#            logging.error("ERROR - friendlyName must be alphanumeric, hyphen or underscore in send - valueerror %s", e)
#            return False
#        except AttributeError as e:
#            logging.error("ERROR - friendlyName must be alphanumeric, hyphen or underscore in send - attributeerror %s", e)
#            return False
#        except ValueError as e:
#            logging.error("ERROR - friendlyName must be alphanumeric, hyphen or underscore in send - valueerror %s", e)
#            return False
#        except:
#            logging.error("ERROR - friendlyName must be alphanumeric, hyphen or underscore in send - error is - %s", sys.exc_info()[0])
#            return False

        return True

        
    def __checkSanitarinessOfFlags(self, dictFlags):
        

        # TODO cant get this to work so leave it out for now
#        try:
#            flags_schema = {
#                "+sec" : V.Range("integer", min_value=1, max_value=3),
#                "+gdpr" : V.Range("integer", min_value=1, max_value=4),
#                "+qos" : V.Range("integer", min_value=1, max_value=3),
#                "+proto" : V.Range("integer", min_value=1, max_value=40),
#                }
#            validator = V.parse(flags_schema)
#            if validator.is_valid(dictFlags):
#                pass
#            else:
#                logging.error("ERROR - flags are out of range in send")
#                return False
#        except TypeError as e:
#            logging.error("ERROR - flags are out of range in send - typeerror %s", e)
#            return False
#        except ValueError as e:
#            logging.error("ERROR - flags are out of range in send- valueerror %s", e)
#            return False
#        except AttributeError as e:
#            logging.error("ERROR - flags are out of range in send- attributeerror %s", e)
#            return False
#        except:
#            logging.error("ERROR - flags are out of range in send - error is - %s", sys.exc_info()[0])
#            return False
            
        return True
    

    def __makeMetadata(self, dictMetadata):
        dictCompositePayload = {
            unicode("desc") : dictMetadata,
            unicode("dat") : None
            }
        return dictCompositePayload
    
    

    def __makeMetadataHdr(self, dictMetadataHdr, dictFlags, friendlyName):

        dictCompositeMetaHdr = {
            unicode("id") : dictMetadataHdr,
            unicode("flags") : dictFlags
            }
        return dictCompositeMetaHdr
    
    
    def __encodeJsonHdr(self, signedMetaHdr):
        try:
            jsonHdrMeta = json.dumps(signedMetaHdr)
            logging.debug("json header metadata is " + jsonHdrMeta)
        except:
            logging.error("ERROR - failure of json.dumps - error is - %s", sys.exc_info()[0])
            return False
            
#        logging.debug("json data for header payload is " + jsonHdrMeta)
        return jsonHdrMeta


    def __clearsignMetadata(self, dictMetaHdr):
        # not enabled at the moment
        dictCompositeMetaHdr = {
            unicode("sig") : "",
            unicode("meta") : dictMetaHdr}
        return dictCompositeMetaHdr


    def __makePayload(self, dictPayload):
        # lift out the data
        dataContent = dictPayload[unicode("dat")]  # data is not stored as unicode because it is already uuencode

        return dataContent


    def __makePayloadMeta(self, dictPayload, compressedPayloadSize, encryptedPayloadSize):
        # blank out the data from the payload to leave only the metadata
        dictPayload[unicode("sze")] = encryptedPayloadSize
        dictPayload[unicode("szc")] = compressedPayloadSize
        # the data is handled separately so remove it from here
        del dictPayload["dat"]
        return dictPayload


    def __encryptPayload(self, dictPayload):
        # not enabled at the moment
        return dictPayload


    def __encodeJson(self, dictMetadata, dictPayload):
        
        try:
            dictCompositePayload = {
                unicode("meta") : dictMetadata,
                unicode("dat") : dictPayload}
            jsonComposite = json.dumps(dictCompositePayload)
            logging.debug("json data for payload metadata and data is " + jsonComposite)
        except TypeError as e:
            logging.error("ERROR - unable to encode metadata as json - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - unable to encode metadata as json - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - unable to encode metadata as json - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - unable to encode metadata as json - error is - %s", sys.exc_info()[0])
            return False
        
        return jsonComposite




    def __packDataB64(self, rawData):
        b64JsonData = base64.b64encode(rawData)
        return b64JsonData


    def __compressMsg(self, rawData):
        # not enabled at the moment
        return rawData


    def __callProtoSend(self, destination, objProtocol, objClient, jsonPayload, dictFlags, transport, friendlyName):
        
        try:
            objProtocol.protocolSend(destination, objClient, jsonPayload, dictFlags, transport, friendlyName)
        except TypeError as e:
            logging.error("ERROR - unable to send to protocol - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - unable to send to protocol - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - unable to send to protocol - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - unable to send to protocol - error is - %s", sys.exc_info()[0])
            return False
        
        return True

    def __callProtoReceive(self,dictPayload, dictMetadata, friendlyName):
#        try:
#            protocolReceive(dictPayload, dictMetadata, friendlyName)
#        except:
#            logging.error("ERROR - unable to receive from protocol")
#            return False
        
        return True
    
    
    def receivedProcessHeader(self, jsonReceivedProtocolData):
        '''
        public method to unpack, sanitise, validate and return a HDR record
        '''

        try:
            candidateMeta = self.__uncompressReceived(self.__decodeJson(jsonReceivedProtocolData))
        except:
            logging.error("ERROR - failure to interpret received data on initial check - error is - %s", sys.exc_info()[0])
            return False
        try:
            dictFlags, dictMetaHdr, clearsignSig = self.__upackCandidateMetaHdr(candidateMeta)
        except:
            logging.error("ERROR - failure to unpack received data on initial check - error is - %s", sys.exc_info()[0])
            return False
        try:
            self.__checkClearsign(clearsignSig)
        except:
            logging.error("ERROR - clearsign signature indicates corrupt HDR record")
            return False

        try:
            self.__sanitiseReceivedMetadataHdr(dictFlags, dictMetaHdr)
        except:
            logging.error("ERROR - unsanitary data received in HDR record")
            return False
        

        try:
            self.__validateMetadata(dictMetaHdr)
        except:
            logging.warning("WARNING - metadata invalid for receive message")
            return False

        try:
            self.__checkACLHdr(dictMetaHdr)
        except:
            logging.warning("WARNING - access denied for ACL for receive message")
            return False
        
        try:
            self.__giveHdrToApp(dictFlags, dictMetaHdr)
        except:
            logging.error("ERROR - unable to give data to use on receive of message")
            return False
        
#        self.__incrementStats(friendlyName)

        return dictFlags, dictMetaHdr
            
    
    
    
    def receivedProcessBody(self, jsonReceivedProtocolData):
        '''
        public method to unpack, sanitise, validate and return a BODY record
        '''
        try:
            candidatePayload = self.__uncompressReceived(self.__decodeJson(jsonReceivedProtocolData))
        except:
            logging.error("ERROR - failure to interpret received data on first check - error is - %s", sys.exc_info()[0])
            return False
        try:
            dictPayload, dictMetaPayload, clearsignSig = self.__upackCandidatePayload(candidatePayload)
        except:
            logging.error("ERROR - failure to unpack received data on first check - error is - %s", sys.exc_info()[0])
            return False
        try:
            self.__checkClearsign(clearsignSig)
        except:
            logging.error("ERROR - clearsign signature indicates corrupt BODY record")
            return False

        try:
            self.__sanitiseReceivedPayload(dictPayload, dictMetaPayload)
        except:
            logging.error("ERROR - unsanitary data received in BODY record")
            return False

        try:
            self.__decryptPayload(dictPayload)
        except:
            logging.error("ERROR - failure of decryption of payload on receive of message")
            return False
        try:
            self.__fullyUnpackDataB64(dictPayload)
        except:
            logging.error("ERROR - failure of base64 unpack of payload on receive of message")
            return False
        
        try:
            self.__validatePayload(dictMetaPayload)
        except:
            logging.warning("WARNING - metadata invalid for receive message")
            return False
        
        try:
            self.__checkACLData(dictMetaPayload)
        except:
            logging.warning("WARNING - access denied for ACL for receive message")
            return False

        try:
            self.__giveDataToApp(dictPayload, dictMetaPayload)
        except:
            logging.error("ERROR - unable to give payload data to user on receive of message")
            return False
        

#        self.__incrementStats(friendlyName)        
        return dictPayload, dictMetaPayload
    
        

    def __decodeJson(self, jsonReceivedProtocolData):
        try:
            jsonHdrMeta = json.loads(jsonReceivedProtocolData)
            logging.debug("json header metadata is " + jsonHdrMeta)
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
    
    
        
    def __upackCandidateMetaHdr(self, candidateMeta):
        # set to bad value to force a lookup failure when dropping thru
        candidateProtocolType = 99
        try:
            # attempt to extract protocolType information
            candidateFlags = candidateMeta[unicode("flags")]
        except:
            logging.debug("DEBUG - could not extract flags for FLAGS metadata in HDR template for mqtt")
            # TODO not sure if this is the right thing to do
            pass
            
        try:
            # attempt to extract protocolType information
            candidateProtocolType = candidateFlags[unicode("prt")]
        except:
            # it might or might not be a BODY record if not found
            logging.debug("DEBUG - protocol not found in HDR template for mqtt")
            pass
        
        # set to a default value to instantiate the receiving variable as that enum Type
        transport = ProtocolType.PROTO_NONE
        try:
            transport = transport.reverseLookup(candidateProtocolType)
        except:
            logging.debug("DEBUG - protocol not translated for HDR template for mqtt")
            # assume this is a BODY record rather than a HDR record
            pass
        
        # TODO we cannot assume messages arrive in the correct sequence
        # but i do not have the time to write complicated stream error handling 
        # so assume everything is how we would like it to be
        

        try:
            # attempt to extract protocolType information
            candidateQosType = candidateFlags[unicode("qos")]
        except:
            # set to bad value to force a failsafe
            candidateQosType = 99
            # it might or might not be a BODY record if not found
            logging.debug("DEBUG - qos flag not found in HDR template for mqtt")
            pass
        
        try:
            # attempt to extract protocolType information
            candidateSecurityType = candidateFlags[unicode("sec")]
        except:
            # set to bad value to force a failsafe
            candidateSecurityType = 99
            # it might or might not be a BODY record if not found
            logging.debug("DEBUG - security flag not found in HDR template for mqtt")
            pass
        
        try:
            # attempt to extract protocolType information
            candidateGdprType = candidateFlags[unicode("gdpr")]
        except:
            # set to bad value to force a failsafe
            candidateGdprType = 99
            # it might or might not be a BODY record if not found
            logging.debug("DEBUG - gdpr flag not found in HDR template for mqtt")
            pass
        

        
        # set to a default value to instantiate the receiving variable as that enum Type
        qosEnum = QosType.reverseLookup(candidateQosType)
        secEnum = SecurityType.reverseLookup(candidateSecurityType)
        gdprEnum = GdprType.reverseLookup(candidateGdprType)
        # unpack the flags into a dictionary
        # NB we put keys for the dictionary into unicode as well because json will mangle everything out into unicode Type not str Type
        # and that becomes a problem because we pass across dictionaries as params
        # Either everything becomes unicode or everything becomes utf-8 str or int
        dictFlags = {
            unicode("prt") : unicode(transport), 
            unicode("qos") : unicode(qosEnum),
            unicode("sec") : unicode(secEnum),
            unicode("prv") : unicode(gdprEnum)
            }
        

        try:
            # attempt to extract sender and friendlyName information
            candidateID = candidateMeta[unicode("id")]
        except:
            logging.debug("DEBUG - could not extract ID metadata for HDR template for mqtt - assuming a BODY record")
            # TODO not sure if this is the right thing to do
            pass
            
        try:
            candidateSender = candidateID[unicode("sndr")]
            candidateFriendlyName = candidateID[unicode("name")]
            candidateVer = candidateID[unicode("ver")]
            logging.debug("DEBUG - extracted sender and friendlyName OK for HDR template for mqtt - assuming a HDR record")
        except:
            logging.debug("DEBUG - could not extract sender and friendlyName for HDR template for mqtt - assuming a BODY record")
            candidateSender = None
            candidateFriendlyName = None
        
        # build the stream header
        # schema version for this layout is version 0.1.0
        # "ver" : version number of the schema as x.y.z format
        # "sndr" : sender as fqdn
        # "name" : the friendly name assigned to the channel
        dictMetaHdr = {
            unicode("ver") : unicode(candidateVer),
            unicode("sndr") : json.dumps(candidateSender),
            unicode("name") : json.dumps(candidateFriendlyName)
            }
                    
        try:
            # attempt to extract clearsign signature information
            clearsignSig = candidateMeta[unicode("sig")]
        except:
            logging.debug("DEBUG - could not extract ID metadata for HDR template for mqtt - assuming a BODY record")
            clearsignSig = "FAIL"
            # TODO not sure if this is the right thing to do
            pass

        
        return dictFlags, dictMetaHdr, clearsignSig
    




    def __sanitiseReceivedPayload(self, dictPayload, dictMetaPayload):

        try:
            self.__checkSanitarinessOfPayloadMeta(dictMetaPayload)
        except:
            logging.error("ERROR - unsanitary data detected in meta dictionary of BODY record")
            return False
        
        
        try:
            self.__checkSanitarinessOfPayloadData(dictPayload)
        except:
            logging.error("ERROR - unsanitary data detected in data dictionary of BODY record")
            return False
        
        return True



    def __sanitiseReceivedMetadata(self,friendlyName):
        return True


    def __sanitiseReceivedMetadataHdr(self, dictFlags, dictMetaHdr):

        try:
            self.__checkSanitarinessOfID(dictMetaHdr)
        except:
            logging.error("ERROR - unsanitary data detected in ID dictionary of HDR")
            return False
        
        
        try:
            self.__checkSanitarinessOfFlags(dictFlags)
        except:
            logging.error("ERROR - unsanitary data detected in Flags dictionary of HDR")
            return False
        
        return True


    def __fullyUnpackDataB64(self,dictPayload):
        try:
            b64payload = base64.standard_b64decode(dictPayload)
        except:
            logging.error("ERROR - unable to decode from base64 for Body payload")
            raise ValueError ("ERROR - unable to decode from base64 for Body payload")
            return False
        
        return b64payload


    def __validateMetadata(self,dictMetaHdr):
        # TODO not currently implemented
        return True
    
    
    def __validatePayload(self, dictMetaPayload):
        # TODO not currently implemented
        return True
    

    def __checkACLHdr(self,dictMetaHdr):
        # TODO not currently implemented
        return True


    def __checkACLData(self,dictMetaPayload):
        # TODO not currently implemented
        return True


    def __decryptPayload(self,friendlyName):
        # TODO not currently implemented
        return True


    def __incrementStats(self,friendlyName):
        # TODO not currently implemented
        return True
    
    
    def __giveHdrToApp(self, dictFlags, dictMetaHdr):
        # TODO remove unicode where necessary
        return dictFlags, dictMetaHdr
    
    def __giveDataToApp(self, dictPayload, dictMetaPayload):
        # TODO remove unicode where necessary
        return dictPayload, dictMetaPayload
    

    def __queryBrokerReachable(self, friendlyName):
        '''
        Before sending data we have to check whether or not the broker is reachable
        '''
        
#        networkDown = False
#        if
#        return True
        return True 



#    exit (1)
    