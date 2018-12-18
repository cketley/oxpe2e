'''
Created on 29 Sep 2017

@author: cheney
'''


import paho.mqtt.client as mqtt
from oxpe2elib.channel.msg.protocol.mqtt.mqttClient import MqttClient as Client
from oxpe2elib.channel.msg.protocol.mqtt.mqttSmartAgent import MqttSmartAgent as Agent
from oxpe2elib.channel.msg.protocol.mqtt.mqttTimeOutError import MqttTimeOutError

import time
import json
import logging

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random



__author__ = "Emma Tattershall & Callum Iddon"
__version__ = "1.3"
__email__ = "etat02@gmail.com, jens.jensen@stfc.ac.uk"
__status__ = "Pre-Alpha"


class MqttBrokerServices(Client):
    def __init__(self, hostname, name, port=1883, protocol='3.1'):
        Client.__init__(self, hostname, name, port, protocol)
        self.devices = {}

    
    def setup(self, timeout=20):
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
        global incoming_message_buffer

        # Setting clean_session = False means that subsciption information and 
        # queued messages are retained after the client disconnects. It is suitable
        # in an environment where disconnects are frequent.
        mqtt_client = mqtt.Client(protocol=self.protocol, client_id=self.name, clean_session=False)
        mqtt_client.on_connect = Agent.on_connect
        mqtt_client.on_message = Agent.on_message
        mqtt_client.on_publish = Agent.on_publish
        mqtt_client.on_disconnect = Agent.on_disconnect

        # Connect to the broker
        # keepalive is maximum number of seconds allowed between communications
        # with the broker. If no other messages are sent, the client will send a
        # ping request at this interval
        logging.info('Attempting to connect to broker at ' + self.hostname)
        mqtt_client.connect(self.hostname, self.port, keepalive=60)
        
        # Force function to block until connack is sent from the broker, or timeout
        connack = False
        start_time = time.time()
        while not connack:
            time.sleep(0.1)
            mqtt_client.loop()
        
            if time.time() - start_time > timeout:
                raise MqttTimeOutError("The program timed out while trying to connect to the broker!")
                break
                            
        # When connected, subscribe to the relevant channels
        mqtt_client.subscribe(self.STATUS, 1)
        
        self.client = mqtt_client
        

                            
        # Set a message buffer
        incoming_message_buffer = []

        # Start the loop. This method is preferable to repeatedly calling loop
        # since it handles reconnections automatically. It is non-blocking and 
        # handles interactions with the broker in the background.
        logging.info('Starting loop')
        self.client.loop_start()
    
    def respond_handshake(self, agent_name):
        # Share the broker's public key
        self.client.publish(Client.topic_handshake(agent_name), 
                            self.package({'public_key': self.public_key.exportKey().decode()}), 
                            qos=1, retain=True)
                            
    def loop(self):
        """
        This loop method can be run periodically to read messages out of the
        incoming message buffer. It also deals with replying to ping requests
        from other devices.
        
        Note that it is not necessary to handle reconnection to the broker in 
        this function; that task is done by the paho-mqtt loop function. 
        """
        global incoming_message_buffer
        
        # dump all incoming messages into a list and empty the string
        incoming_messages = incoming_message_buffer
        # empty the buffer
        incoming_message_buffer = []
        parsed_messages= []

        for message in incoming_messages:
            # Add new devices to the dictionary
            if message.topic == self.STATUS:
                try:
                    payload = json.loads(message.payload.decode())
                    parsed_messages.append(payload)
                    # If we have already met the device...
                    if payload['sess'] in self.devices.keys():
                        # And it would like to disconnect...
                        if payload['status'] != 'C':
                            # Remove it from our dictionary
                            del self.devices[payload['sess']]
                            logging.info('Device ' + payload['sess'] + ' disconnected')
                    # If we do not recognise the device...
                    else:
                        # And it would like to connect...
                        if payload['status'] == 'C':
                            # Add it to our dictionary
                            try:
                                self.devices[payload['sess']] = RSA.importKey(payload['public_key'].encode())
                                logging.info('Device ' + payload['sess'] + ' connected')
                                
                                # Send back our own public key
                                self.respond_handshake(payload['sess'])
                            except Exception as e:
                                print(e)
                                logging.error(e)
                except:
                    logging.info('Error while reading message: ' + str(message.payload))
        return parsed_messages
    
    def clean_up(self):
        self.client.disconnect()
        self.client.loop_stop()
                