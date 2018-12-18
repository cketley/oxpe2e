'''
Created on 29 Sep 2017

@author: cheney
'''

        
        
import paho.mqtt.client as mqtt
from oxpe2elib.channel.msg.protocol.mqtt.mqttClient import MqttClient as Client
from oxpe2elib.channel.msg.protocol.mqtt.mqttTimeOutError import MqttTimeOutError

from oxpe2elib.channel.protocolType import ProtocolType
from oxpe2elib.channel.qosType import QosType
from oxpe2elib.channel.secType import SecurityType
from oxpe2elib.channel.gdprType import GdprType

import time
import json
import logging
import sys

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random


__author__ = "Emma Tattershall & Callum Iddon"
__version__ = "1.3"
__email__ = "etat02@gmail.com, jens.jensen@stfc.ac.uk"
__status__ = "Pre-Alpha"

STATUS_CONNECTED = "C"
STATUS_DISCONNECTED_GRACE = "DG"
STATUS_DISCONNECTED_UNGRACE = "DU"
HUB = 'broker_services'





    
        

class MqttSmartAgent(Client):
    """
    This class extends the standard Client class.
 
    """
    def __init__(self, dictParams):
        hostname = dictParams["sess"]
        name = dictParams["dest"]
        port = dictParams["port"]
        protocol = dictParams["protoVer"]
        broker = dictParams["broker"]
        # this is a Singleton
        self.receiver = dictParams["RcvdMsg"]
        try:
            # static methods are referenced as <class>.<method>
            Client.__init__(self, dictParams)
        except TypeError as e:
            logging.error("ERROR - could not call mqtt Client - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - could not call mqtt Client - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - could not call mqtt Client - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - could not call mqtt Client - unknown error")
            return False
        else:
            logging.debug("INFO - all OK - no problem on attempt to call mqtt Client")

            
        # Set the topics that will be subscribed to
        # Subscriptions are the opposite sense to Publishing so use hostname rather than myName
        try:
            # static methods are referenced as <class>.<method>
            self.PUBLIC = Client.topic_public(self.hostname)
        except TypeError as e:
            logging.error("ERROR - could not subscribe to mqtt topic- typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - could not subscribe to mqtt topic - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - could not subscribe to mqtt topic - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - could not subscribe to mqtt public topic - unknown error")
            return False
        else:
            logging.info("INFO - all OK - no problem on attempt to subscribe to mqtt topic Public") 
        try:           
            self.PROTECTED = Client.topic_protected(self.hostname)
        except:
            logging.error("ERROR - could not subscribe to mqtt protected topic - unknown error")
            return False
        else:
            logging.info("INFO - all OK - no problem on attempt to subscribe to mqtt topic Protected") 
        try:
            self.PRIVATE = Client.topic_private(self.hostname)
        except:
            logging.error("ERROR - could not subscribe to mqtt private topic - unknown error")
            return False
        else:
            logging.info("INFO - all OK - no problem on attempt to subscribe to mqtt topic Private") 
        try:
            self.PINGREQ = Client.topic_pingreq(self.hostname)
        except:
            logging.error("ERROR - could not subscribe to mqtt pingreq topic- unknown error")
            return False
        try:
            self.PINGACK = Client.topic_pingack(self.hostname)
        except:
            logging.error("ERROR - could not subscribe to mqtt pingack topic - unknown error")
            return False
        try:
            self.HANDSHAKE = Client.topic_handshake(self.hostname)
        except:
            logging.error("ERROR - could not subscribe to mqtt handshake topic - unknown error")
            return False
        
        self.broker_public_key = None
        
        return None
    
        
    def setup(self, dictParams):
        """
        This method sets up the actual MQTT client, assigns all callback 
        functions for event handling and sets a last will and testament (LWT)
        message. 
        
        It then attempts to connect to the broker. The connection call
        is blocking; it continues until a connection acknowlegement message is 
        received from the broker or until the timeout is reached.
        
        After connection has been acheived, it subscribes to the topics:
            oxpe2elib/[name]/public
            oxpe2elib/[name]/protected
            oxpe2elib/[name]/private
            oxpe2elib/[name]/public/pinreq
            oxpe2elib/[name]/public/pingack
            
        If another device wants to contact this smart agent, it must publish to
        one of these topics. 
        
        Finally, this method starts the MQTT loop running on a separate thread.
        This loop thread handles publishing and receiving messages, and also 
        routinely pings the broker to check the connection status. If the
        connection is lost, the thread automatically buffers messages and 
        attempts to reconnect
        """
        global connack
        # we dont use globals here now - instead use config.py which is imported where needed to 
        # give cross-module scope
        #global globalScope.incomingMessageBuffer
        global broker_public_key
        
        hostname = dictParams["sess"]
        name = dictParams["dest"]
        port = dictParams["port"]
        protocol = dictParams["protoVer"]
        broker = dictParams["broker"]
        # this is a Singleton
        self.receiver = dictParams["RcvdMsg"]
        timeout = dictParams["timeout"]
        oldtimestamp = dictParams["oldtimestamp"]
        anotherParam = dictParams["anotherParam"]
        
        self.brokerName = broker

        # Setting clean_session = False means that subsciption information and 
        # queued messages are retained after the client disconnects. It is suitable
        # in an environment where disconnects are frequent.
        # client_id is any unique identifier so our own fqdn should be alright to use
        mqtt_client = mqtt.Client(protocol=self.protocol, client_id=self.myName, clean_session=False)
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = self.on_message
        mqtt_client.on_publish = self.on_publish
        mqtt_client.on_disconnect = self.on_disconnect
        mqtt_client.on_subscribe = self.on_subscribe
        mqtt_client.on_unsubscribe = self.on_unsubscribe
        mqtt_client.on_log = self.on_log
        
                
        # Set the LWT
        # If the client disconnects without calling disconnect, the broker will
        # publish this message on its behalf
        # retain should be set to true
        mqtt_client.will_set(self.STATUS, 
                             self.status_message(STATUS_DISCONNECTED_UNGRACE), 
                             qos=QosType.FLAG_QOS_ATMOSTONCE.value, retain=True) 

        # Connect to the broker
        # keepalive is maximum number of seconds allowed between communications
        # with the broker. If no other messages are sent, the client will send a
        # ping request at this interval
        # set it high for devices that are disconnected for small periods of time, also for debugging
        # set it extremely high for devices that are out to sea for days
        keepalive=1800
        try:
            logging.info('Attempting to connect to broker at ' + self.brokerName)
            mqtt_client.connect(self.brokerName, self.port, keepalive)
        except:
            logging.error("ERROR - could not connect to broker at " + self.brokerName)
            return False
        else:
            logging.info("INFO - all OK - no problem on attempt to connect to broker at " + self.brokerName) 
            
        
        # Force function to block until connack is sent from the broker, or timeout
        connack = False
        start_time = time.time()
        while not connack:
            time.sleep(0.1)
            mqtt_client.loop()
        
            if time.time() - start_time > float(timeout):
                raise MqttTimeOutError("The program timed out while trying to connect to the broker!")
                break
        
        # When connected, subscribe to the relevant channels
        mqtt_client.subscribe([(self.PUBLIC, 1), (self.PROTECTED, 1),
                              (self.PRIVATE, 1), (self.PINGREQ, 1),
                              (self.PINGACK, 1), (self.HANDSHAKE, 1)
                             ])
        
        self.client = mqtt_client
        
        # init the globalScope.incomingMessageBuffer - this is now done in the config.py
        
        
        # Do a blocking call
        broker_public_key = None
        self.client.publish(self.STATUS, 
                     self.status_message(STATUS_CONNECTED), 
                     qos=QosType.FLAG_QOS_ATLEASTONCE.value)

        # TODO dont know what this does and it was getting stuck in the loop so i got rid of it     
#        while self.broker_public_key == None:
#            time.sleep(0.1)
#            mqtt_client.loop()
#            # Check the message buffer
#            if globalScope.incomingMessageBuffer != []:
#                for message in globalScope.incomingMessageBuffer:
#                    if message.topic == self.HANDSHAKE:
#                        # Check whether it is a broker key message.
#                        try:
#                            payload = json.loads(message.payload.decode())
## disabled for now
##                            self.broker_public_key = payload['public_key']
##                            print(self.broker_public_key)
#                            self.broker_public_key = json.loads(message.payload.decode())
#                        except:
#                            pass
#                globalScope.incomingMessageBuffer = []
            

        # Start the loop. This method is preferable to repeatedly calling loop
        # since it handles reconnections automatically. It is non-blocking and 
        # handles interactions with the broker in the background.
        logging.debug('DEBUG - Starting loop')
        try:
#            mqtt_client.loop()
            self.client.loop_start()
        except:
            logging.error("ERROR - failure of loop_start")
            
        return True
    
    

    def waitForCallback(self):
        time.sleep(0.1)
        self.loop()
        return True
        
      
    def status_message(self, status):
        payload = {
                   'status': status
                   }
# disabled for now
#        if status == STATUS_CONNECTED:
#            payload['public_key'] = self.public_key.exportKey().decode()
        return self.package(payload)

                            
    def loop(self):
        """
        This loop method can be run periodically to read messages out of the
        incoming message buffer. It also deals with replying to ping requests
        from other devices.
        
        Note that it is not necessary to handle reconnection to the broker in 
        this function; that task is done by the paho-mqtt loop function. 
        """
        # dump all incoming messages into a list and empty the string
        incoming_messages = self.receiver.getDataFromCallback()
        # empty the buffer
        self.receiver.emptyDataFromCallback()

        parsed_messages = []
        pingacks = []
        for message in incoming_messages:
            # Deal with ping requests

            if message.topic == self.PINGREQ:
                self.pingack(json.loads(message.payload.decode()))
            # Deal with acknowledgements to our own ping requests
            elif message.topic == self.PINGACK:
                pingacks.append(json.loads(message.payload.decode()))
            # Parse non-encrypted messages
            elif message.topic == self.PUBLIC:
                parsed_messages.append(json.loads(message.payload.decode()))

        return parsed_messages, pingacks
    
    def clean_up(self):
        # Send a hello message to broker services
        try:
            self.client.publish(self.STATUS, 
                         self.package({'status': STATUS_DISCONNECTED_GRACE}), 
                         qos=QosType.FLAG_QOS_ATLEASTONCE.value)
        except:
            logging.error("ERROR - unable to publish on clean_up - %s", sys.exc_info()[0])
            pass
             
        try:
            self.client.disconnect()
        except:
            logging.error("ERROR - unable to disconnect on clean_up - %s", sys.exc_info()[0])
            pass
             
        try:
            self.client.loop_stop()
        except:
            logging.error("ERROR - unable to loop_stop on clean_up - %s", sys.exc_info()[0])
            pass
             
        return True



    ### we are not using these here
    def encrypt(self, payload, destination_public_key):
        # Payload data can be anything; a list, a string, a dictionary...
        payload = json.dumps(payload)
        encrypted_payload = destination_public_key.encrypt(payload.encode(), 32)
        return encrypted_payload[0]
        
    def decrypt(self, encrypted_string):
        plaintext = encrypted_string
        return plaintext
    
    def generate_signature(self, name, public_key):
        hashed_name = SHA256.new(name.encode()).digest()
        signature = public_key.sign(hashed_name, '')
        return signature
        
    def timestamp(self, ):
        # Returns a string UNIX time
        return str(int(time.time()))
        
    
    
        
    def on_connect(self, mqtt_client, userdata, flags, rc):
        """
Called when the broker responds to our connection request.
client
the client instance for this callback
userdata
the private user data as set in Client() or user_data_set()
flags
response flags sent by the broker
rc
the connection result
flags is a dict that contains response flags from the broker:
flags['session present'] - this flag is useful for clients that are
using clean session set to 0 only. If a client with clean session=0, that reconnects to a broker that it has previously connected to, this flag indicates whether the broker still has the session information for the client. If 1, the session still exists.
The value of rc indicates success or not:
 0: Connection successful 1: Connection refused - incorrect protocol version 2: Connection refused - invalid client identifier 3: Connection refused - server unavailable 4: Connection refused - bad username or password 5: Connection refused - not authorised 6-255: Currently unused.
        
        This function sets a global connack flag when broker connection has been
        confirmed.
        """
        global connack
        logging.debug("DEBUG - Connected to broker")
        connack = True
        
    def on_disconnect(self, mqtt_client, userdata, rc):
        """
Called when the client disconnects from the broker.
client
the client instance for this callback
userdata
the private user data as set in Client() or user_data_set()
rc
the disconnection result
The rc parameter indicates the disconnection state. If MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call. If any other value the disconnection was unexpected, such as might be caused by a network error.

        This function is called when a disconnect packet is sent from this client.
        It is also used if the broker itself disconnects.
        """
        logging.debug('DEBUG - Disconnected from broker')
        
        
    def on_publish(self, mqtt_client, userdata, mid):
        """
Called when a message that was to be sent using the publish() call has completed transmission to the broker. For messages with QoS levels 1 and 2, this means that the appropriate handshakes have completed. For QoS 0, this simply means that the message has left the client. The mid variable matches the mid variable returned from the corresponding publish() call, to allow outgoing messages to be tracked.
This callback is important because even if the publish() call returns success, it does not always mean that the message has been sent.
        """
        logging.debug("DEBUG - publish ack received")
        
        
    
    def on_subscribe(self, mqtt_client, userdata, mid, granted_qos):
        """
Called when the broker responds to a subscribe request. The mid variable matches the mid variable returned from the corresponding subscribe() call. The granted_qos variable is a list of integers that give the QoS level the broker has granted for each of the different subscription requests.
        """
        logging.debug("DEBUG - subscribe ack received")
        
        
    def on_unsubscribe(self, mqtt_client, userdata, mid ):
        """
Called when the broker responds to an unsubscribe request. The mid variable matches the mid variable returned from the corresponding unsubscribe() call.
        """
        logging.debug("DEBUG - unsubscribe ack received")
        

    def on_log(self, mqtt_client, userdata, level, buf):
        """
Called when the client has log information. Define to allow debugging. The level variable gives the severity of the message and will be one of MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, and MQTT_LOG_DEBUG. The message itself is in buf.

This may be used at the same time as the standard Python logging, which can be enabled via the enable_logger method.
        """
        logging.debug("DEBUG - on_log received")
        
        
        
    
    def on_message(self, mqtt_client, userdata, message):
        """
Called when a message has been received on a topic that the client subscribes to and the message does not match an existing topic filter callback. Use message_callback_add() to define a callback that will be called for specific topic filters. on_message will serve as fallback when none matched.
client
the client instance for this callback
userdata
the private user data as set in Client() or user_data_set()
message
an instance of MQTTMessage. This is a class with members topic, payload, qos, retain.

        This function is called when a message is received.
        
        It adds the new messsage to the module-level message buffer. We have chosen 
        to use a buffer rather than dealing with messages in this callback
        function because it means we can provide greater flexibility for users
        """
        
        # data received from mqtt is put into a buffer that is a global variable.
        # It is up to the app to look at the buffer and access the data in it.
        # If the app does not do that the buffer could fill up.
        # TODO needs handling of buffer overflow condition
        logging.debug("DEBUG - incoming message received")
        
        self.receiver.setDataFromCallback(message)

        # For blocking reads the app will go into an infinite loop that terminates only on  
        # an error or this flag set to True
        
        self.receiver.setLoopCallbackReceivedFlag(True)
        
        return True
        
        
        
         