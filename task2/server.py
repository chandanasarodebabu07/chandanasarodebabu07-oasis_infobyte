"""
Chat Server - Run this first!
Usage: python server.py
"""

import asyncio
import json
import websockets
from datetime import datetime

# Store connected clients and chat rooms
clients = {}  # {websocket: {username, room}}
rooms = {}    # {room_name: [websocket, ...]}
message_history = {}  # {room_name: [messages]}

DEFAULT_ROOMS = ["general", "random", "tech"]

for room in DEFAULT_ROOMS:
    rooms[room] = []
    message_history[room] = []


async def broadcast_to_room(room, message, exclude=None):
    if room in rooms:
        dead = []
        for ws in rooms[room]:
            if ws == exclude:
                continue
            try:
                await ws.send(json.dumps(message))
            except:
                dead.append(ws)
        for ws in dead:
            await remove_client(ws)


async def remove_client(ws):
    if ws in clients:
        info = clients[ws]
        room = info["room"]
        username = info["username"]
        del clients[ws]
        if room in rooms and ws in rooms[room]:
            rooms[room].remove(ws)
        await broadcast_to_room(room, {
            "type": "system",
            "text": f"{username} left the room.",
            "room": room,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        await broadcast_user_list(room)


async def broadcast_user_list(room):
    users = [clients[ws]["username"] for ws in rooms.get(room, []) if ws in clients]
    await broadcast_to_room(room, {"type": "user_list", "users": users, "room": room})


async def handler(websocket):
    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except:
                continue

            msg_type = data.get("type")

            # --- JOIN ---
            if msg_type == "join":
                username = data.get("username", "Anonymous")[:20]
                room = data.get("room", "general")
                if room not in rooms:
                    rooms[room] = []
                    message_history[room] = []

                # Remove from old room if switching
                if websocket in clients:
                    old_room = clients[websocket]["room"]
                    if old_room != room:
                        if ws in rooms.get(old_room, []):
                            rooms[old_room].remove(websocket)
                        await broadcast_to_room(old_room, {
                            "type": "system",
                            "text": f"{username} switched to #{room}",
                            "room": old_room,
                            "timestamp": datetime.now().strftime("%H:%M")
                        })

                clients[websocket] = {"username": username, "room": room}
                if websocket not in rooms[room]:
                    rooms[room].append(websocket)

                # Send history
                await websocket.send(json.dumps({
                    "type": "history",
                    "messages": message_history[room][-50:],
                    "room": room
                }))

                await broadcast_to_room(room, {
                    "type": "system",
                    "text": f"{username} joined #{room} 👋",
                    "room": room,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                await broadcast_user_list(room)

            # --- MESSAGE ---
            elif msg_type == "message":
                if websocket not in clients:
                    continue
                info = clients[websocket]
                username = info["username"]
                room = info["room"]
                text = data.get("text", "").strip()[:500]
                if not text:
                    continue

                msg = {
                    "type": "message",
                    "username": username,
                    "text": text,
                    "room": room,
                    "timestamp": datetime.now().strftime("%H:%M")
                }
                message_history[room].append(msg)
                if len(message_history[room]) > 200:
                    message_history[room] = message_history[room][-200:]

                await broadcast_to_room(room, msg)

            # --- TYPING ---
            elif msg_type == "typing":
                if websocket not in clients:
                    continue
                info = clients[websocket]
                await broadcast_to_room(info["room"], {
                    "type": "typing",
                    "username": info["username"],
                    "isTyping": data.get("isTyping", False)
                }, exclude=websocket)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await remove_client(websocket)


async def main():
    print("🚀 Chat server started on ws://localhost:8765")
    print("   Rooms:", ", ".join(DEFAULT_ROOMS))
    print("   Waiting for connections...\n")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())