This is the library for oxpe2e (The Offline Cross-Program language End to End encryption utility)

Capabilities:-
To send and receive data via RabbitMQ or MQTT. 
It is expected that the comms link will be intermittently down. An MQ server must be located either side of the comms link to store and forward the data.

To encrypt data from its first creation to its last moment at the storage server. It is expected that Bad Guys will have physical access to any of the intermediate servers and so will attempt to read the data while it is located in the MQ mailbox i.e. at rest. Hence the encryption rather than use of SSL.

To provide multiple clients.

To provide independence of the program language used at either end of the comms link. Hence the use of RabbitMQ which has clients in a large number of programming languages.

To be callable from within a user app or from the command line. 



To install:-

pip install oxpe2elib-<version>.tar.gz

To run:-

First install this library then install the demo suite and run it.
pip install oxpe2e_alice2bob-<version>.tar.gz
python oxpe2e-alice2bob


Released under the Apache v2 license.

A fork of a part of the mF2C project.


