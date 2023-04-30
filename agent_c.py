#! /usr/bin/python3

import logging as log
import openai
import os
import requests

log.basicConfig(
    level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

openai.api_key = os.environ.get("OPENAI_API_KEY")

def handle(msg, reply):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": msg}
        ]
    )
    reply(completion.choices[0].message["content"])