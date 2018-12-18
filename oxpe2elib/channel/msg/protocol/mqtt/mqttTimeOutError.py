'''
Created on 2 Oct 2017

@author: cheney
'''

class MqttTimeOutError(Exception):
    """
    Timout Error is called when the time taken to receive a connection 
    acknowledgement packet exceeds the user-defined wait time.
    """
    def __init__(self, value):
        self.value = value


