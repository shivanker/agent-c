#! /usr/bin/python3

import logging as log
from abc import ABC, abstractmethod

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Agent(ABC):
    def __init__(self, name, purpose, memory):
        self.name = name
        self.purpose = purpose
        self.memory = memory

    @abstractmethod
    def invoke(self, user, prompt):
        pass
