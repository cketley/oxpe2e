'''
Created on 5 Oct 2017

@author: cheney
'''

from enum import Enum, unique     # for enum34, or the stdlib version
@unique
class QosType(Enum):
    # under no circumstances alter these values or names !!! 
    # the numbers must match the java enum which is positional not numbered.
    # altering the placeholder dummies so that they have new names with the same value is OK 
    # so long as the changes are rippled out to all progs using it.
    # deleting values or names is not allowed under any circumstances.
    # you have been warned !!!
    # these values have to match what is expected by MQTT so dont change them
    FLAG_QOS_ATMOSTONCE = 0
    FLAG_QOS_ATLEASTONCE = 1
    FLAG_QOS_EXACTLYONCE = 2
    # fail safe by defaulting to this invalid value when it's first instantiated
    FLAG_QOS_INVALID = 99

    @classmethod
    def reverseLookup(cls, value):
        for _, member in cls.__members__.items():
            if member.value == value:
                return member
                raise LookupError
            
