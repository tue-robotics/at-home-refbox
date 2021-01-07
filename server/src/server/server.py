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

from competition import Competition
from score_register import ScoreRegister

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
    def __init__(self, event, nr_arenas=2):
        self._arenas = [chr(65 + i) for i in range(nr_arenas)]  # "A", "B", etc.
        self._competition = Competition(event)
        self._score_register = self._create_score_register(event)
        self._clients = set()

    @staticmethod
    def _create_score_register(event):
        path = os.path.join(os.path.expanduser("~"), ".at-home-refbox-data")
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, "score_db.csv")
        return ScoreRegister(event, filename)

    async def serve(self, websocket, path):
        # register(websocket) sends user_event() to websocket
        await self._register(websocket)
        print("Websocket registered")
        try:
            await websocket.send(self._get_score_message())
            async for message in websocket:
                print(f"Received message: {message}")
                data = json.loads(message)
                if "setting" in data:
                    await self._on_setting(data)
                elif "score" in data:
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
    def _get_data_on_registration(self):
        data = {"A":
            {
                "event": self._competition.event,
                "metadata": self._competition.get_metadata_dict("A"),
                "score_table": score_table,
                "challenge_info": challenge_info,
                "standings": standings,
            },
        }
        return json.dumps(data)

    async def _on_setting(self, data):
        setting = data["setting"]
        if "team" in setting:
            self._competition.set_team(data["arena"], setting["team"])
            message = json.dumps({
                "metadata": self._competition.get_metadata_dict(data["arena"])
            })
        else:
            print(f"Cannot update setting: {data}")
            return
        if self._clients:  # asyncio.wait doesn't accept an empty list
            await asyncio.wait([client.send(message) for client in self._clients])

    def _on_score(self, data):
        metadata = self._competition.get_metadata(data["arena"])  # type: dict
        for key, value in data["score"].items():
            self._score_register.register_score(
                metadata=metadata, score_key=int(key), score_increment=value,
            )

    # @staticmethod
    # def _get_metadata(arena):  # Shouldn't be static once setting metadata is possible
    #     arena_metadata = METADATA[arena]
    #     return MetaData(
    #         arena_metadata["event"], arena_metadata["team"], arena_metadata["challenge"], arena_metadata["attempt"]
    #     )

    def _get_score_message(self):
        arena = "A"  # ToDo: allow multiple arenas
        metadata = self._competition.get_metadata(arena)
        new_score = self._score_register.get_score(metadata, score_table)
        # data = {"current_scores": {arena: new_score}}
        data = {arena: {"current_scores": new_score}}
        return json.dumps(data)

    async def _notify_state(self):
        if self._clients:  # asyncio.wait doesn't accept an empty list
            message = self._get_score_message()
            await asyncio.wait([client.send(message) for client in self._clients])

    async def _unregister(self, websocket):
        self._clients.remove(websocket)


if __name__ == "__main__":
    print("Creating server")
    server = Server("RoboCup 2021")
    # Set some default values for easy testing
    server._competition.set_team("A", "Tech United Eindhoven")
    server._competition.set_challenge("A", "Cocktail party")
    server._competition.set_attempt("A", 1)
    start_server = websockets.serve(server.serve, "localhost", 6789)

    print("Starting")
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Start running forever")
    asyncio.get_event_loop().run_forever()
