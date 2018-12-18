This is the library for oxpe2e (The Offline Cross-Program language End to End encryption utility for IoT comms)

Capabilities:-

- To send and receive data across a comms link that will be intermittently down via MQ-style protocols. 
    An MQ-style server must be located either side of the comms link to store and forward the data.

- To encrypt data from its first creation to its last moment at the storage server. 
    It is expected that Bad Guys will have physical access to any of the intermediate servers and so will attempt to read the data while it is located in the MQ mailbox i.e. at rest. Hence the encryption rather than use of SSL.

- To provide multiple clients eg RabbitMq, MQTT, http.

- To provide clients of different types that can interoperate eg RabbitMQ and MQTT

- To provide clients that will run in a low-power and small-memory environment eg MQTT

- To provide independence of the program language used at either end of the comms link. 
    Hence the use of RabbitMQ which has clients in a large number of programming languages.

- To intelligently handle many error states.

- To use mutual authentication to reduce the risk of man-in-the-middle attacks.

- To be callable from within a user app or from the command line. 



To install:-

pip install oxpe2elib-<version>.tar.gz

To run:-

First install this library then install the separate demo suite and run it.

For MQTT client:-
python env/bin/oxpe2eDemoMqttAlice2Bob.py
python env/bin/oxpe2eDemoMqttBobFromAlice.py


Released under the Apache v2 license.

A fork of a part of the mF2C project.


