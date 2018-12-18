'''
Created on 5 Oct 2017

@author: cheney
'''

from enum import Enum, unique     # for enum34, or the stdlib version
@unique
class GdprType(Enum):
    # under no circumstances alter these values or names !!! 
    # the numbers must match the java enum which is positional not numbered.
    # altering the placeholder dummies so that they have new names with the same value is OK 
    # so long as the changes are rippled out to all progs using it.
    # deleting values or names is not allowed under any circumstances.
    # you have been warned !!!
    FLAG_PRIV_GDPR = 1
    FLAG_PRIV_NOTGDPR = 2
    FLAG_PRIV_NOTPII = 3
    FLAG_PRIV_UNKNOWN = 4
    # fail safe by defaulting to this invalid value when it's first instantiated
    FLAG_PRIV_INVALID = 5

    @classmethod
    def reverseLookup(cls, value):
        for _, member in cls.__members__.items():
            if member.value == value:
                return member
                raise LookupError
            
