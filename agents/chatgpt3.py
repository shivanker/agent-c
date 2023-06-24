#! /usr/bin/python3

import logging as log
from agents.agent import Agent

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ChatGpt3(Agent):
    def invoke(self, user, prompt):
        pass
