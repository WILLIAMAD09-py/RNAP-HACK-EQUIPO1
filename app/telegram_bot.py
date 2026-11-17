import threading
import time

import httpx

from app import inbox
from receipt import pipeline

API = "https://api.telegram.org"
RECEIVED_TEXT = "Recibimos tu nota de voz, la tienda la está revisando."
ERROR_TEXT = "No pudimos entender tu nota de voz. Intenta grabarla de nuevo, por favor."
HELP_TEXT = ("Hola, soy el bot de Ferretería Los Nogales. Mándame una nota de voz con tu pedido: "
             "tu nombre, el producto, la cantidad, la medida y la hora de entrega.")
state = {"token": None, "bot_username": None, "thread": None, "build_result": None, "stop": threading.Event()}


def call(method, data=None, timeout=15):
    response = httpx.post(f"{API}/bot{state['token']}/{method}", data=data or {}, timeout=timeout)
    response.raise_for_status()
    return response.json().get("result")


def send_message(chat_id, text):
    try:
        call("sendMessage", {"chat_id": chat_id, "text": text})
        return True
    except Exception as error:
        print(f"No se pudo enviar el mensaje: {type(error).__name__}")
        return False


def download_voice(file_id, destination):
    info = call("getFile", {"file_id": file_id})
    response = httpx.get(f"{API}/file/bot{state['token']}/{info['file_path']}", timeout=60)
    response.raise_for_status()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)


def customer_from(message):
    sender = message.get("from") or {}
    name = " ".join(part for part in (sender.get("first_name"), sender.get("last_name")) if part)
    return {"name": name or None, "username": sender.get("username"), "chat_id": message["chat"]["id"]}


def handle_voice(message, voice):
    chat_id = message["chat"]["id"]
    item_id = inbox.new_id()
    path = inbox.audio_path(item_id)
    send_message(chat_id, RECEIVED_TEXT)
    try:
        download_voice(voice["file_id"], path)
        result = state["build_result"](pipeline.process_audio(str(path), "solution"))
    except Exception as error:
        print(f"Falló el procesamiento de una nota de voz: {type(error).__name__}")
        send_message(chat_id, ERROR_TEXT)
        return None
    customer = customer_from(message)
    ticket = result["ticket"]
    if not ticket.get("cliente") and customer["name"]:
        ticket["cliente"] = customer["name"]
        result["review_fields"] = [name for name in result["review_fields"] if name != "cliente"]
    return inbox.create(customer, result, item_id)


def handle_update(update):
    message = update.get("message")
    if not message:
        return
    voice = message.get("voice") or message.get("audio")
    if voice:
        handle_voice(message, voice)
    else:
        send_message(message["chat"]["id"], HELP_TEXT)


def poll_loop():
    offset = None
    while not state["stop"].is_set():
        try:
            params = {"timeout": 25, "allowed_updates": '["message"]'}
            if offset is not None:
                params["offset"] = offset
            updates = call("getUpdates", params, timeout=40) or []
        except Exception as error:
            print(f"Telegram no respondió: {type(error).__name__}")
            state["stop"].wait(5)
            continue
        for update in updates:
            offset = update["update_id"] + 1
            try:
                handle_update(update)
            except Exception as error:
                print(f"Error al atender una actualización: {type(error).__name__}")


def start(token, build_result):
    state["token"] = token
    state["build_result"] = build_result
    state["stop"].clear()
    me = call("getMe")
    state["bot_username"] = me.get("username")
    state["thread"] = threading.Thread(target=poll_loop, name="telegram-bot", daemon=True)
    state["thread"].start()
    return state["bot_username"]


def stop():
    state["stop"].set()
    state["bot_username"] = None
    state["token"] = None


def status():
    return {"enabled": bool(state["bot_username"]), "bot_username": state["bot_username"]}
