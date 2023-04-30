#! /usr/bin/python3

import logging as log
import requests

log.basicConfig(
    level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


OPENAI_API_KEY = "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"

def handle(msg, reply):
    reply(f"I received: {msg}")