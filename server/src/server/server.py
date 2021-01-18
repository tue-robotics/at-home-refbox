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
import typing
import websockets

# Server
from arena_states import ArenaStates
from competition_info import CompetitionInfo
from score_register import ScoreRegister
from server_types import ServerConfig, ReceiveKeys, SendKeys, SettingKeys, ChallengeInfoKeys

logging.basicConfig()


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
    def __init__(self, config: ServerConfig):
        self._arenas = [chr(65 + i) for i in range(config.nr_arenas)]  # "A", "B", etc.
        self._competition_info = CompetitionInfo(config.info_dir, config.event)
        self._arenastates = ArenaStates(config.event)
        self._score_register = self._create_score_register(config.db_dir, config.event)
        self._clients = set()

    @staticmethod
    def _create_score_register(path: str, event: str) -> ScoreRegister:
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, "score_db.csv")
        return ScoreRegister(event, filename)

    async def serve(self, websocket, path):
        await self._register(websocket)
        print("Websocket registered")
        try:
            await self._process_messages(websocket)
        finally:
            await self._unregister(websocket)
            print("Unregistered")

    async def _register(self, websocket):
        data = self._get_data_on_registration()
        await websocket.send(json.dumps(data))
        self._clients.add(websocket)

    def _get_data_on_registration(self) -> dict:
        data = {}
        for arena in self._arenas:
            data.update(self._get_data(arena, [
                SendKeys.EVENT,
                SendKeys.TEAMS,
                SendKeys.CHALLENGES,
                SendKeys.METADATA,
                SendKeys.CHALLENGE_INFO,
                SendKeys.STANDINGS,
                SendKeys.CURRENT_SCORES,
            ]))
        return data

    async def _process_messages(self, websocket):
        async for message in websocket:
            await self._process_message(message)

    async def _process_message(self, message: str):
        print(f"Received message: {message}")
        data = json.loads(message)
        for arena in self._arenas:
            if arena in data:
                await self._process_arena_data(arena, data[arena])

    async def _process_arena_data(self, arena: str, arena_data: str):
        if ReceiveKeys.SETTING in arena_data:
            await self._on_setting(arena, arena_data[ReceiveKeys.SETTING])
        elif ReceiveKeys.SCORE in arena_data:
            await self._on_score(arena, arena_data[ReceiveKeys.SCORE])
        else:
            logging.error("unsupported event: {}", arena_data)

    async def _on_setting(self, arena: str, setting: dict):
        if SettingKeys.TEAM in setting:
            await self._on_set_team(arena, setting[SettingKeys.TEAM])
        if SettingKeys.CHALLENGE in setting:
            await self._on_set_challenge(arena, setting[SettingKeys.CHALLENGE])
        if SettingKeys.ATTEMPT in setting:
            await self._on_set_attempt(arena, setting[SettingKeys.ATTEMPT])
        # else:
        #     print(f"Cannot update setting: {data}")
        #     return

    async def _on_set_team(self, arena: str, team: str):
        self._arenastates.set_team(arena, team)
        data = self._get_data(arena, [SendKeys.METADATA, SendKeys.CURRENT_SCORES])
        await self._send_data_to_all(data)

    async def _on_set_challenge(self, arena: str, challenge: str):
        self._arenastates.set_challenge(arena, challenge)
        data = self._get_data(arena, [SendKeys.METADATA, SendKeys.CHALLENGE_INFO, SendKeys.CURRENT_SCORES])
        await self._send_data_to_all(data)

    async def _on_set_attempt(self, arena: str, challenge: str):
        self._arenastates.set_attempt(arena, challenge)
        data = self._get_data(arena, [SendKeys.METADATA, SendKeys.CURRENT_SCORES])
        await self._send_data_to_all(data)

    def _get_data(self, arena: str, requested_keys: typing.List[str]) -> dict:
        metadata = self._arenastates.get_metadata(arena)
        challenge_info = self._competition_info.get_challenge_info(metadata.challenge)
        data = {}
        if SendKeys.EVENT in requested_keys:
            data[SendKeys.EVENT] = self._competition_info.event
        if SendKeys.TEAMS in requested_keys:
            data[SendKeys.TEAMS] = self._competition_info.list_teams()
        if SendKeys.CHALLENGES in requested_keys:
            data[SendKeys.CHALLENGES] = self._competition_info.list_challenges()
        if SendKeys.METADATA in requested_keys:
            data[SendKeys.METADATA] = metadata.to_dict()
        if SendKeys.CHALLENGE_INFO in requested_keys:
            data[SendKeys.CHALLENGE_INFO] = challenge_info
        if SendKeys.CURRENT_SCORES in requested_keys:
            score_table = challenge_info["score_table"]
            score = self._score_register.get_score(metadata, score_table)
            data[SendKeys.CURRENT_SCORES] = score
        if SendKeys.STANDINGS in requested_keys:
            data[SendKeys.STANDINGS] = standings
        return {arena: data}

    async def _on_score(self, arena: str, score: typing.Dict[int, int]):
        metadata = self._arenastates.get_metadata(arena)  # type: dict
        for key, value in score.items():
            self._score_register.register_score(
                metadata=metadata, score_key=int(key), score_increment=value,
            )
        data = self._get_data(arena, [SendKeys.CURRENT_SCORES])
        await self._send_data_to_all(data)

    async def _send_data_to_all(self, data: dict):
        # print(f"Sending {data} to {len(self._clients)} clients")
        if self._clients:  # asyncio.wait doesn't accept an empty list
            message = json.dumps(data)
            await asyncio.wait([client.send(message) for client in self._clients])

    async def _unregister(self, websocket):
        self._clients.remove(websocket)


# noinspection PyProtectedMember
def select_defaults_in_server(server):
    # Set some default values for easy testing
    server._arenastates.set_team("A", "Tech United Eindhoven")
    server._arenastates.set_challenge("A", "Cocktail Party")
    server._arenastates.set_attempt("A", 1)


if __name__ == "__main__":
    print("Creating server")
    import pathlib
    info_dir = os.path.join(
        pathlib.Path(__file__).parent.absolute().parent.parent,
        "test", "data"
    )
    db_dir = os.path.join(os.path.expanduser("~"), ".at-home-refbox-data")
    config = ServerConfig("RoboCup 2021", info_dir, db_dir, 2)
    server = Server(config)
    select_defaults_in_server(server)
    start_server = websockets.serve(server.serve, "localhost", 6789)

    print("Starting")
    asyncio.get_event_loop().run_until_complete(start_server)
    print("Start running forever")
    asyncio.get_event_loop().run_forever()
