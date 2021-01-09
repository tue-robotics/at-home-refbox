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
from server_types import ReceiveKeys, SendKeys, SettingKeys

logging.basicConfig()


CHALLENGE_INFO = [
    {
        "name": "Cocktail party",
        "description": "Enter the arena, take the orders of the three guests trying to yet your attention, "
                       "serve the drinks and exit the arena",
        "score_table": [
                {"key": 123, "description": 'Enter arena', "scoreIncrement": 100, "maxScore": 100},
                {"key": 124, "description": 'Pick up drink', "scoreIncrement": 100, "maxScore": 300},
                {"key": 125, "description": 'Deliver drink', "scoreIncrement": 100, "maxScore": 300},
                {"key": 126, "description": 'Correct person', "scoreIncrement": 100, "maxScore": 300},
                {"key": 127, "description": 'Exit arena', "scoreIncrement": 100, "maxScore": 100},
        ],
    },
    {
        "name": "Restaurant",
        "description": "Find the customers trying to get their attention and ask what they would like. "
                       "Retrieve the orders from the bar and serve them to the customers",
        "score_table": [
            {"key": 223, "description": 'Detect bar', "scoreIncrement": 100, "maxScore": 100},
            {"key": 224, "description": 'Find waving person', "scoreIncrement": 200, "maxScore": 600},
            {"key": 225, "description": 'Understand order', "scoreIncrement": 100, "maxScore": 300},
            {"key": 226, "description": 'Deliver order', "scoreIncrement": 200, "maxScore": 600},
        ],
    },
]


def get_challenge_info_dict(challenge):
    if challenge:
        return [info_dict for info_dict in CHALLENGE_INFO if info_dict["name"] == challenge][0] if challenge else {}
    else:
        return {"name": {}, "description": "", "score_table": []}


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
    def __init__(self, path, event, nr_arenas=2):
        self._arenas = [chr(65 + i) for i in range(nr_arenas)]  # "A", "B", etc.
        self._competition = Competition(event)
        self._score_register = self._create_score_register(path, event)
        self._clients = set()

    @staticmethod
    def _create_score_register(path, event):
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
                # ToDo: make nice (don't indent this far)
                for arena in self._arenas:
                    if arena not in data:
                        continue

                    arena_data = data[arena]
                    if ReceiveKeys.SETTING in arena_data:
                        await self._on_setting(arena, arena_data[ReceiveKeys.SETTING])
                    elif ReceiveKeys.SCORE in arena_data:
                        await self._on_score(arena, arena_data[ReceiveKeys.SCORE])
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
        arena = "A"
        metadata = self._competition.get_metadata(arena)
        data = {arena:
            {
                SendKeys.EVENT: self._competition.event,
                SendKeys.METADATA: metadata.to_dict(),
                SendKeys.CHALLENGE_INFO: get_challenge_info_dict(metadata.challenge),
                SendKeys.STANDINGS: standings,
            },
        }
        return json.dumps(data)

    async def _on_setting(self, arena, setting):
        if SettingKeys.TEAM in setting:
            await self._on_set_team(arena, setting[SettingKeys.TEAM])
        if SettingKeys.CHALLENGE in setting:
            await self._on_set_challenge(arena, setting[SettingKeys.CHALLENGE])
        # else:
        #     print(f"Cannot update setting: {data}")
        #     return

    async def _on_set_team(self, arena, team):
        self._competition.set_team(arena, team)
        metadata = self._competition.get_metadata(arena)
        score_table = get_challenge_info_dict(metadata.challenge)["score_table"]
        new_score = self._score_register.get_score(metadata, score_table)
        data = {
            arena: {
                "metadata": metadata.to_dict(),
                "current_scores": new_score,
            }
        }
        await self._send_data_to_all(data)

    async def _on_set_challenge(self, arena, challenge):
        self._competition.set_challenge(arena, challenge)
        metadata = self._competition.get_metadata(arena)
        challenge_info = get_challenge_info_dict(metadata.challenge)
        score_table = get_challenge_info_dict(metadata.challenge)["score_table"]
        new_score = self._score_register.get_score(metadata, score_table)
        data = {
            arena: {
                SendKeys.METADATA: metadata.to_dict(),
                SendKeys.CHALLENGE_INFO: challenge_info,
                SendKeys.CURRENT_SCORES: new_score,
            }
        }
        print(f"Challenge data: {data}")
        await self._send_data_to_all(data)

    async def _on_score(self, arena, score):
        metadata = self._competition.get_metadata(arena)  # type: dict
        for key, value in score.items():
            self._score_register.register_score(
                metadata=metadata, score_key=int(key), score_increment=value,
            )
        await self._notify_score()

    def _get_score_message(self):
        arena = "A"  # ToDo: allow multiple arenas
        metadata = self._competition.get_metadata(arena)
        score_table = get_challenge_info_dict(metadata.challenge)["score_table"]
        new_score = self._score_register.get_score(metadata, score_table)
        data = {arena: {SendKeys.CURRENT_SCORES: new_score}}
        return json.dumps(data)

    async def _send_data_to_all(self, data):
        # print(f"Sending {data} to {len(self._clients)}")
        if self._clients:  # asyncio.wait doesn't accept an empty list
            message = json.dumps(data)
            await asyncio.wait([client.send(message) for client in self._clients])

    # ToDo: change to 'notify score'
    async def _notify_score(self):
        if self._clients:  # asyncio.wait doesn't accept an empty list
            message = self._get_score_message()
            await asyncio.wait([client.send(message) for client in self._clients])

    async def _unregister(self, websocket):
        self._clients.remove(websocket)


# noinspection PyProtectedMember
def select_defaults_in_server(server):
    # Set some default values for easy testing
    server._competition.set_team("A", "Tech United Eindhoven")
    server._competition.set_challenge("A", "Cocktail party")
    server._competition.set_attempt("A", 1)

if __name__ == "__main__":
    print("Creating server")
    path = os.path.join(os.path.expanduser("~"), ".at-home-refbox-data")
    server = Server(path, "RoboCup 2021")
    select_defaults_in_server(server)
    start_server = websockets.serve(server.serve, "localhost", 6789)

    print("Starting")
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Start running forever")
    asyncio.get_event_loop().run_forever()
