'''
Created on 5 Oct 2017

@author: cheney
'''

from enum import Enum, unique     # for enum34, or the stdlib version
@unique
class SecurityType(Enum):
    # under no circumstances alter these values or names !!! 
    # the numbers must match the java enum which is positional not numbered.
    # altering the placeholder dummies so that they have new names with the same value is OK 
    # so long as the changes are rippled out to all progs using it.
    # deleting values or names is not allowed under any circumstances.
    # you have been warned !!!
    FLAG_SEC_PUBLIC = 1
    FLAG_SEC_PROTECTED = 2
    FLAG_SEC_PRIVATE = 3
    # fail safe by defaulting to this invalid value when it's first instantiated
    FLAG_SEC_INVALID = 99
    
    @classmethod
    def reverseLookup(cls, value):
        for _, member in cls.__members__.items():
            if member.value == value:
                return member
                raise LookupError
            
