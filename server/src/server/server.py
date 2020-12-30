#!/usr/bin/python3.7
# #!/usr/bin/env python

# Copied/adapted from https://websockets.readthedocs.io/en/stable/intro.html
# To make this work:
# * Use Python 3.7
# * Make sure path is correct

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = set()

# Static data, retrieved directly from the database
score_table = [
  {"key": 123, "description": 'Enter arena', "scoreIncrement": 100, "maxScore": 100},
  {"key": 124, "description": 'Pick up drink', "scoreIncrement": 100, "maxScore": 300},
  {"key": 125, "description": 'Deliver drink', "scoreIncrement": 100, "maxScore": 300},
  {"key": 126, "description": 'Correct person', "scoreIncrement": 100, "maxScore": 300},
  {"key": 127, "description": 'Exit arena', "scoreIncrement": 100, "maxScore": 100},
]


challenge_info = {
  "Cocktail party": {
    "description": "Enter the arena, take the orders of the three guests trying to yet your attention, serve the drinks and exit the arena",
  },
}

# State: should 'live' server side in order to keep referee and audience clients in sync
# Should support multiple arenas
metadata = {
  "A":
    {
      "event": "RoboCup 2021, Bordeaux, France",
      "challenge": "Cocktail party",
      "team": "Tech United Eindhoven",
      "attempt": 1,
    },
}


standings = [
  {
    "team": "Tech United Eindhoven",
    "played": 3,
    "points": 1225,
  },
  {
    "team": "Hibikino Musashi",
    "played": 3,
    "points": 1175,
  },
  {
    "team": "er@sers",
    "played": 3,
    "points": 1125,
  },
]


current_scores = {
  "A": {
    123: 0,
    124: 0,
    125: 0,
    126: 0,
    127: 0,
  },
}


def update_score(data):
    global current_scores
    arena_score = current_scores[data["arena"]]
    arena_score[data["score"]["key"]] = data["score"]["value"]


def state_event():
    data = {"type": "state", **STATE}
    data["current_scores"] = current_scores
    return json.dumps(data)

# ToDo: update
# * improve name
# * should send (large amount of data) in case of
#     * Registering a user
#     * Updating settings
# * data should contain everything that's specific per challenge (metadata, description, scoretable), currentscores
#   and general: standings
# * convenient to do this per arena, hence:
#   data = {'A': {metadata: ..., score_table: ..., challenge_info: ..., current_scores: ...}, 'standings': ...}
def users_event():
    data = {"type": "users", "count": len(USERS)}
    data["metadata"] = metadata
    data["score_table"] = score_table
    data["challenge_info"] = challenge_info
    data["current_scores"] = current_scores
    data["standings"] = standings
    return json.dumps(data)


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    print("Websocket registered")
    try:
        await websocket.send(state_event())
        async for message in websocket:
            print(f"Received message: {message}")
            data = json.loads(message)
            if "score" in data:
                update_score(data)
                await notify_state()
            elif data["action"] == "minus":
                STATE["value"] -= 1
                await notify_state()
            elif data["action"] == "plus":
                STATE["value"] += 1
                await notify_state()
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)
        print("Unregistered")


print("Creating server")
start_server = websockets.serve(counter, "localhost", 6789)

print("Starting")
asyncio.get_event_loop().run_until_complete(start_server)
print("Start running forever")
asyncio.get_event_loop().run_forever()
