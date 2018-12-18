'''
Created on 29 Sep 2017

@author: cheney
'''

        
import paho.mqtt.client as mqtt
import time
import json
import logging

from oxpe2elib.channel.protocolType import ProtocolType
from oxpe2elib.channel.qosType import QosType
from oxpe2elib.channel.secType import SecurityType
from oxpe2elib.channel.gdprType import GdprType

__author__ = "Emma Tattershall & Callum Iddon"
__version__ = "1.3"
__email__ = "etat02@gmail.com, jens.jensen@stfc.ac.uk"
__status__ = "Pre-Alpha"


### these methods belong to the class not the instance
def timestamp():
    # Returns a string UNIX time
    return str(int(time.time()))
    



class MqttClient():
    """
    Client is the base class for the Smart Agent and Broker Agent classes. It 
    sets class level variables and creates a RSA key pair when it is initialised.
    
    It also contains the methods used in sending a message, and sending and 
    receiving pings since these are the same for any kind of agent.
    """
    def __init__(self, dictParams):
        # Check input
        '''
        Constructor
        '''
        
        logging.debug("dictParams is %s", dictParams)
        myName = dictParams["sess"]
        hostname = dictParams["dest"]
        port = dictParams["port"]
        protocol = dictParams["protoVer"]
        broker = dictParams["broker"]
        # this is a Singleton
        # not referenced here
        self.receiver = dictParams["RcvdMsg"]

        ### i got rid of this check because it was doing some strange things with unicode
#         try:
#             assert type(hostname) is str
#             assert type(myName) is str
#             assert type(port) is int
#             assert protocol in ['3.1', '3.1.1']
#         except:
#             logging.error("ERROR - invalid input to init for mqttClient")

        # Set class level variables
        self.hostname = hostname
        self.myName = myName
        self.port = port
        # Set protocol. When using older machines in any part of your system,
        # there may only be support for version 3.1
        if protocol == '3.1':
            self.protocol = mqtt.MQTTv31
        elif protocol == '3.1.1':
            self.protocol = mqtt.MQTTv311

        # Set the topics that will be subscribed to
        try:
            self.STATUS = self.topic_status()
        except TypeError as e:
            logging.error("ERROR - on topic_status - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - on topic_status - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - on topic_status - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - on topic_status - unknown error")
            return False

        
        # Set a new random generator and create a RSA key pair
        ### disabled for now
#        random_generator = Random.new().read
#        self.key = RSA.generate(1024, random_generator)
#        self.public_key = self.key.publickey()
        return None
    
    
    def package(self, payload_dict, security=SecurityType.FLAG_SEC_PUBLIC):
        """
        Method adds supplementary information to the supplied payload. At 
        present the added items are:
            - timestamp (UNIX time, str)
            - sess (ID of this agent, str)
        """
        payload_dict['timestamp'] = timestamp()
        if 'sess' not in payload_dict.keys():
            payload_dict['sess'] = self.myName

        ### disabled for now
#        if security != 0:
#            payload_dict['signature'] = generate_signature(self.myName, self.public_key)
            
        if SecurityType.reverseLookup(security) in [SecurityType.FLAG_SEC_PUBLIC,SecurityType.FLAG_SEC_PROTECTED]:
            return json.dumps(payload_dict)
        #else:
            # Encrypt the payload of the message
            #payload_dict['payload'] = encrpyt(payload, broker_public_key)


    def send(self, recipients, jsonPayload, security=SecurityType.FLAG_SEC_PUBLIC.value, qos=QosType.FLAG_QOS_ATLEASTONCE.value):
        """
        Method sends a specified jsonic payload to a list of recipients.
        """
        # Check input
        try:
            assert type(recipients) == list
            assert len(recipients) > 0
            assert SecurityType.reverseLookup(security) in [SecurityType.FLAG_SEC_PUBLIC, SecurityType.FLAG_SEC_PROTECTED, SecurityType.FLAG_SEC_PRIVATE]
#            assert type(payload_dict) == dict
        except:
            logging.error("ERROR - invalid input to mqtt client")
            return False

        # Add metadata to the payload
        # Add a timestamp (integer unix time) and the sess ID to the payload
#        payload_dict['timestamp'] = timestamp()
#        if 'sess' not in payload_dict.keys():
#            payload_dict['sess'] = self.myName

        # For protected and private messages, a signature must be added
        ### disabled for now
#        if security in [1,2]:
#            payload_dict['signature'] = generate_signature(self.myName, self.public_key)
#            payload_dict['public_key'] = self.public_key.exportKey().decode()
            
        
        # Send the message
        # For public and protected messages, the payload does not need to be
        # encrypted and can be sent straight to each recipient
        if SecurityType.reverseLookup(security) in [SecurityType.FLAG_SEC_PUBLIC,SecurityType.FLAG_SEC_PROTECTED]:
            for recipient in recipients:
                topic = self.topic_public(recipient)
#                payload_str = json.dumps(payload_dict)
                try:
                    self.client.publish(topic, jsonPayload, qos)
                except:
                    logging.error("ERROR - unable to publish from client")
                    return False
         
        # For private messages, the recipients list must be encluded in the payload.
        # The entire payload must be encrypted
        # The message must be sent to the broker
        else:
            topic = self.topic_private('broker_services')
            
            return True
            

    
    def pingack(self, payload_dict):
        """
        Respond to a ping from another device with a ping acknowledgement.
        
        This method is called automatically when a 
        """
        # ping is always public
        try:
            recipient = payload_dict['sess']
        except:
            return
        topic = self.topic_pingack(recipient)
        payload_dict = {
                        'timestamp' : timestamp(),
                        'sess' : self.myName
                       }
        self.client.publish(topic, json.dumps(payload_dict), qos=2)
     
    def ping(self, recipients):
        """
        Send a ping request to one or more recipients
        """
        assert type(recipients) == list
        assert len(recipients) > 0
        for recipient in recipients:
            payload_dict = {
                        'timestamp' : timestamp(),
                        'sess' : self.myName
                       }
    
            self.client.publish(self.topic_pingreq(recipient), json.dumps(payload_dict), qos=2)

    
    """
    Define topic conventions
    """
    # static methods are referenced as <class>.<method>
    @staticmethod
    def topic_public(myName):
        logging.debug("DEBUG - topic is oxpe2elib/%s/public", str(myName))
        return 'oxpe2elib/' + str(myName) + '/public'
    
    # static methods are referenced as <class>.<method>
    @staticmethod
    def topic_protected(myName):
        logging.debug("DEBUG - topic is oxpe2elib/%s/protected", str(myName))
        return 'oxpe2elib/' + str(myName) + '/protected'
        
    # static methods are referenced as <class>.<method>
    @staticmethod
    def topic_private(myName):
        logging.debug("DEBUG - topic is oxpe2elib/%s/private", str(myName))
        return 'oxpe2elib/' + str(myName) + '/private'
        
    # static methods are referenced as <class>.<method>
    @staticmethod
    def topic_pingreq(myName):
        logging.debug("DEBUG - topic is oxpe2elib/%s/public/pingreq", str(myName))
        return 'oxpe2elib/' + str(myName) + '/public/pingreq'
    
    # static methods are referenced as <class>.<method>
    @staticmethod
    def topic_pingack(myName):
        logging.debug("DEBUG - topic is oxpe2elib/%s/public/pingack", str(myName))
        return 'oxpe2elib/' + str(myName) + '/public/pingack'
    
    # static methods are referenced as <class>.<method>
    @staticmethod
    def topic_status():
        logging.debug("DEBUG - topic is oxpe2elib/broker_services/status")
        return 'oxpe2elib/broker_services/status'
    
    # static methods are referenced as <class>.<method>
    @staticmethod
    def topic_handshake(myName):
        logging.debug("DEBUG - topic is oxpe2elib/%s/public/handshake", str(myName))
        return 'oxpe2elib/' + str(myName) + '/public/handshake'
                