#! /usr/bin/python3

from datetime import datetime

import agent_c
import json
import logging as log
import requests
import threading
import traceback
import websocket
import base64
import mimetypes
import re
import os

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot_number = os.environ.get("SIGNAL_BOT")
admin = os.environ.get("SIGNAL_ADMIN")
allowlist = os.environ.get("SIGNAL_ALLOWLIST").split(",")

agents = {}

# Initialize the API URL
api_url = "http://localhost:8080"

url_pattern = re.compile(r"\bhttps?://[\w$+\-*/=\\#?&@~!%\.,:;]+")


def timestamp():
    return datetime.now().strftime("%b %d, %H:%M:%S")


def send_and_load_urls(recipient_phone_number, message):
    urls = re.findall(url_pattern, message)
    try:
        attachments = []
        for url in urls:
            mime_type = mimetypes.guess_type(url)[0]
            if mime_type.startswith("text"):
                continue
            log.debug(f"Trying to fetch & encode {mime_type} from URL: {url}")
            data = base64.b64encode(requests.get(url).content).decode("utf-8")
            attachments.append(f"data:{mime_type};base64,{data}")

        extra_data = {"base64_attachments": attachments} if attachments else {}
        return send(recipient_phone_number, message, extra_data)
    except Exception as e:
        traceback.print_exc()
        log.error(f"Failed to load URL(s) with error: {str(e)}")
        return send(recipient_phone_number, message)


# Send a message
def send(recipient_phone_number, message, extra_data={}):
    log.debug(f"Trying to text {recipient_phone_number}: {message}")
    url = f"{api_url}/v2/send"
    payload = extra_data | {
        "recipients": [recipient_phone_number],
        "message": message,
        "number": bot_number,
    }
    response = requests.post(url, json=payload)
    if response.status_code != 201:
        log.error(
            f"Failed to send message. Status code: [{response.status_code}], Error: [{response.text}]"
        )
        return False
    return True


def start_typing(recipient_phone_number):
    url = f"{api_url}/v1/typing-indicator/{bot_number}"
    payload = {"recipient": recipient_phone_number}
    response = requests.put(url, json=payload)
    if response.status_code // 100 != 2:
        log.error(
            f"Failed to set typing status. Status code: [{response.status_code}], Error: [{response.text}]"
        )
        return False
    return True


def stop_typing(recipient_phone_number):
    url = f"{api_url}/v1/typing-indicator/{bot_number}"
    payload = {"recipient": recipient_phone_number}
    response = requests.delete(url, json=payload)
    if response.status_code // 100 != 2:
        log.error(
            f"Failed to delete typing status. Status code: [{response.status_code}], Error: [{response.text}]"
        )
        return False
    return True


# Receive messages in normal mode
def receive_normal():
    url = f"{api_url}/v1/receive/{bot_number}"
    # , headers={"Content-Type": "application/json"})
    response = requests.get(url)
    return response


# Fetch an attachment by string id
def fetch_attachment(id):
    url = f"{api_url}/v1/attachments/{id}"
    response = requests.get(url)
    return response


def on_error(ws, error):
    log.error(f"WebSocket error: {error}")


def on_close(ws, status_code, msg):
    log.info(f"WebSocket connection closed. status:[{status_code}], msg:[{msg}]")


def on_open(ws):
    log.info("WebSocket connection established.")
    message = "Starting server on " + timestamp()
    send(admin, message)


# Receive messages using WebSocket
def on_message(ws, message):
    try:
        message = json.loads(message)
        if "envelope" not in message or "sourceNumber" not in message["envelope"]:
            log.error(f"Malformed message: {message}")
            return
        if "dataMessage" not in message["envelope"]:
            return

        sender = message["envelope"]["sourceNumber"]
        senderName = message["envelope"]["sourceName"]
        if sender == None:
            log.info(f"Received first message from a new sender: [{senderName}].")
            send(
                message["envelope"]["sourceUuid"],
                "Hi! Since this was your first message, Signal does not allow me to do much. Please prompt me again.",
            )
            return

        if sender not in allowlist:
            log.warning(f"Received message from disallowed number: {sender}")
            return

        msg_txt = message["envelope"]["dataMessage"]["message"]
        if "attachments" in message["envelope"]["dataMessage"]:
            metadata = message["envelope"]["dataMessage"]["attachments"]
            if "id" in metadata:
                attachment = fetch_attachment(metadata["id"])
        log.info(f"{sender} says:" + msg_txt)
        if sender not in agents:
            agents[sender] = agent_c.AgentC()

        start_typing(sender)
        try:
            agents[sender].handle(
                sender, msg_txt, lambda x: send_and_load_urls(sender, x)
            )
        finally:
            stop_typing(sender)

    except Exception as e:
        traceback.print_exc()


def receive_bg():
    websocket_url = f"ws{api_url[4:]}/v1/receive/{bot_number}"
    ws = websocket.WebSocketApp(
        websocket_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever(reconnect=5)


# Start the receive_messages function in a separate thread
receive_thread = threading.Thread(target=receive_bg)
receive_thread.start()

# Wait for the WebSocket thread to end, then exit the program
receive_thread.join()
