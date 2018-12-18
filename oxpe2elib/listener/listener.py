'''
Created on 15 Sep 2017

@author: cheney
'''



import uuid
import time
import sys

#from oxpe2elib.received.receivedMessage import ReceivedMessage
#import oxpe2elib.config

import logging




class Listener():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''



    def poll(self, objReceivedMessage, objClient, friendlyName):
        '''
        poll will check whether or not there is a message waiting in the buffer to be read
        '''
        try:
            dataAvailableFlag = objReceivedMessage.pollBuffer(objClient, friendlyName)
        except TypeError as e:
            logging.error("ERROR - could not pollBuffer - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - could not pollBuffer - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - could not pollBuffer - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - could not pollBuffer - %s", sys.exc_info()[0])
            return False

        if not dataAvailableFlag:
            logging.debug("DEBUG - no data available at the moment")
            raise ValueError("no data available at the moment - as at %s", str(time.time()))
        return True


    
    def pop(self, objReceivedMessage, objClient, friendlyName):
        '''
        pop will access any messages waiting in the buffer and read them.
        It is not a pop but is actually a dequeue. The name is confusingly incorrect.
        '''

        # First check whether or not there are any messages waiting in the buffer to be read.
        # This might already have been done.
        try:
            dataAvailableFlag = objReceivedMessage.pollBuffer(objClient, friendlyName)
        except TypeError as e:
            logging.error("ERROR - could not pollBuffer2 - typeerror %s", e)
            return False
        except ValueError as e:
            logging.error("ERROR - could not pollBuffer2 - valueerror %s", e)
            return False
        except AttributeError as e:
            logging.error("ERROR - could not pollBuffer2 - attributeerror %s", e)
            return False
        except:
            logging.error("ERROR - could not pollBuffer2 - %s", sys.exc_info()[0])
            return False

        if not dataAvailableFlag:
            logging.debug("DEBUG - no data available at the moment")
            raise ValueError("no data available at the moment - as at %s", str(time.time()))
        
        # now retrieve the data
        try:
            dictFlags, dictMetaHdr, dictPayload, dictMetaPayload = objReceivedMessage.popBuffer(objClient, friendlyName)
        except ValueError as e:
            logging.error("ERROR - unable to handle received data - valueerror %s", e)
            # TODO bodge to bypass bugs
            dictFlags = {} 
            dictMetaHdr = {}
            dictPayload = {}
            dictMetaPayload = {}
            return True
            return False
        except:
            logging.error("ERROR - error handling received data - error is - %s", sys.exc_info()[0])
            return False
            
            
        return dictFlags, dictMetaHdr, dictPayload, dictMetaPayload 
    
   