#! /usr/bin/python3

import logging as log
from abc import ABC, abstractmethod

log.basicConfig(
    level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Memory(ABC):
    def __init__(self, limiter_fn, sizer_fn):
        """Generic class to describe a memory container.
        Arguments:

        limiter_fn -- (int, float, int, dict) -> boolean. Takes recency index of message,
            timestamp, cumulative size of messages so far, and the message dict. Returns whether to
            retain the message or not.
        sizer_fn -- dict -> int. Takes the message dict and returns it's *size* - however the agent
            wants to define it.
        """
        self.limiter = limiter_fn
        self.sizer = sizer_fn

    @abstractmethod
    def get(self, user):
        pass

    @abstractmethod
    def append(self, user, msg):
        pass

    @abstractmethod
    def pop(self, user):
        pass

