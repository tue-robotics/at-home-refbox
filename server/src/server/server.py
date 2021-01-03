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
import os

import websockets

from score_register import ScoreRegister
from server_types import MetaData

logging.basicConfig()


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
METADATA = {
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


class Server(object):
    def __init__(self):
        self._clients = set()
        self._score_register = self._create_score_register()

    @staticmethod
    def _create_score_register():
        path = os.path.join(os.path.expanduser("~"), ".at-home-refbox-data")
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, "score_db.csv")
        return ScoreRegister(filename)

    async def serve(self, websocket, path):
        # register(websocket) sends user_event() to websocket
        await self._register(websocket)
        print("Websocket registered")
        try:
            await websocket.send(self._get_score_message())
            async for message in websocket:
                print(f"Received message: {message}")
                data = json.loads(message)
                if "score" in data:
                    self._on_score(data)
                    await self._notify_state()
                else:
                    logging.error("unsupported event: {}", data)
        finally:
            await self._unregister(websocket)
            print("Unregistered")

    async def _register(self, websocket):
        self._clients.add(websocket)
        await self._notify_users()

    async def _notify_users(self):
        if self._clients:  # asyncio.wait doesn't accept an empty list
            message = self._get_data_on_registration()
            await asyncio.wait([client.send(message) for client in self._clients])
            message = self._get_score_message()
            await asyncio.wait([client.send(message) for client in self._clients])

    # ToDo: update
    # * improve name
    # * should send (large amount of data) in case of
    #     * Registering a user
    #     * Updating settings
    # * data should contain everything that's specific per challenge (metadata, description, scoretable), currentscores
    #   and general: standings
    # * convenient to do this per arena, hence:
    #   data = {'A': {metadata: ..., score_table: ..., challenge_info: ..., current_scores: ...}, 'standings': ...}
    @staticmethod
    def _get_data_on_registration():
        data = {
            "metadata": METADATA,
            "score_table": score_table,
            "challenge_info": challenge_info,
            "standings": standings,
        }
        return json.dumps(data)

    def _on_score(self, data):
        metadata = self._get_metadata(data["arena"])
        self._score_register.register_score(
            metadata=metadata, score_key=data["score"]["key"], score_increment=data["score"]["value"]
        )

    @staticmethod
    def _get_metadata(arena):  # Shouldn't be static once setting metadata is possible
        arena_metadata = METADATA[arena]
        return MetaData(
            arena_metadata["event"], arena_metadata["team"], arena_metadata["challenge"], arena_metadata["attempt"]
        )

    def _get_score_message(self):
        arena = "A"  # ToDo: allow multiple arenas
        metadata = self._get_metadata(arena)
        new_score = self._score_register.get_score(metadata, score_table)
        data = {"current_scores": {arena: new_score}}
        return json.dumps(data)

    async def _notify_state(self):
        if self._clients:  # asyncio.wait doesn't accept an empty list
            message = self._get_score_message()
            await asyncio.wait([client.send(message) for client in self._clients])

    async def _unregister(self, websocket):
        self._clients.remove(websocket)


if __name__ == "__main__":
    print("Creating server")
    server = Server()
    start_server = websockets.serve(server.serve, "localhost", 6789)

    print("Starting")
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Start running forever")
    asyncio.get_event_loop().run_forever()
