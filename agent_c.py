#! /usr/bin/python3

import logging as log
import openai
import os
from memory.inplace import InPlaceMemory
import time

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

openai.api_key = os.environ.get("OPENAI_API_KEY")

users = {
    "+447718963471": "Shiv",
    "+447526184242": "Su",
    "+447850062789": "Infiloop",
}


def sizer(msg):
    return len(msg["content"].split())


def limiter(idx, ts, cum_size, msg):
    if msg["role"] == "system":
        return True
    if cum_size > 2048:
        return False
    if idx > 100:
        return False
    if time.time() - ts > 3600 * 24 * 14:
        return False
    return True


memory = InPlaceMemory(limiter, sizer)


def handle(sender, msg, reply):
    if msg == "/reset":
        memory.pop(sender)
        reply("Your session has been reset.")
        return

    if memory.get(sender) == None:
        memory.append(
            sender,
            {
                "role": "system",
                "content": "Your name is SushiBot. You are a helpful assistant.",
            },
        )
        memory.append(
            sender,
            {
                "role": "system",
                "content": "You are actually implemented as a chatbot on the Signal app. Your number is +919711106306",
            },
        )
        memory.append(
            sender,
            {
                "role": "system",
                "content": "The corporation that created you is called Sushi Labs.",
            },
        )
        memory.append(
            sender,
            {
                "role": "system",
                "content": "Your memory is not guaranteed to be persisted.",
            },
        )
        memory.append(
            sender, {"role": "system", "content": f"User's name is {users[sender]}."}
        )
        memory.append(
            sender,
            {
                "role": "system",
                "content": "You talk in the style of an MIB agent unless otherwise indicated by the user.",
            },
        )
        memory.append(
            sender,
            {
                "role": "system",
                "content": "Your answers are always supposed to be brief.",
            },
        )
    memory.append(sender, {"role": "user", "content": msg})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=memory.get(sender),
        max_tokens=250,
    )
    response = completion.choices[0].message.to_dict_recursive()
    memory.append(sender, response)
    reply(response["content"])
