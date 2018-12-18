'''
Created on 15 Sep 2017

@author: cheney
'''


import uuid

# logging defined in the Channel class

import logging


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
    
    
@Singleton
class Identity():
    '''
    Decorated class to implement a Singleton design pattern.
    
    The class can have only one instance.
     
    f = Foo() # Error, this isn't how you get the instance of a singleton

    f = Foo.Instance() # Good. Being explicit is in line with the Python Zen
    g = Foo.Instance() # Returns already created instance

    print f is g # True

    From wikipedia:- 
    In software engineering, the singleton pattern is a software design pattern that restricts the instantiation of a class to 
    one object. This is useful when exactly one object is needed to coordinate actions across the system. The concept is 
    sometimes generalized to systems that operate more efficiently when only one object exists, or that restrict the 
    instantiation to a certain number of objects. The term comes from the mathematical concept of a singleton.
    
    There are some who are critical of the singleton pattern and consider it to be an anti-pattern in that it is 
    frequently used in scenarios where it is not beneficial, introduces unnecessary restrictions in situations where a 
    sole instance of a class is not actually required, and introduces global state into an application.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        logging.debug('Singleton created for the channel', )


    def idGetInstance(self):
        return True
    
    def idGetDevice(self):
        return True
    
    def idGetHuman(self):
        return True
    
    def idSetStream(self, friendlyName):
        self.idStream = friendlyName
        return True
    
    
    