#! /usr/bin/python3

import logging as log
import openai
import os
import requests

log.basicConfig(
    level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

openai.api_key = os.environ.get("OPENAI_API_KEY")

users = {
    "+447718963471": "Shiv",
    "+447526184242": "Su",
    "+447850062789": "Infiloop",
}

memory = {}

def handle(sender, msg, reply):
    if msg == "/reset":
        memory.pop(sender)
        reply("Your session has been reset.")
        return

    if sender not in memory:
        messages=[
            {"role": "system", "content": "Your name is Agent-C. You are a helpful assistant."},
            {"role": "system", "content": "You are actually implemented as a chatbot on the Signal app. Your number is +919711106306"},
            {"role": "system", "content": "The corporation that created you is called Sushi Labs."},
            {"role": "system", "content": "Your memory is not guaranteed to be persisted."},
            {"role": "system", "content": f"User's name is {users[sender]}."},
            {"role": "system", "content": f"You talk in the style of an MIB agent unless otherwise indicated by the user."},
            {"role": "system", "content": f"Your answers are always supposed to be brief."},
        ]
        memory[sender] = messages
    messages = memory[sender]
    messages.append({"role": "user", "content": msg})
    reduce_context(messages)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens = 250,
    )
    response = completion.choices[0].message
    messages.append(response)
    reply(response["content"])


def reduce_context(messages):
    n = estimate_tokens(messages)
    while n > 2048:
        log.warn("Context too long. Trying to shrink.")
        for index, item in enumerate(messages):
            if item["role"] != "system":
                messages.pop(index)
                break
        n = estimate_tokens(messages)


def estimate_tokens(messages):
    tokens = 0
    for m in messages:
        tokens += len(m["content"].split())
    return tokens