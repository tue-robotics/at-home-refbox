import json
import mock
import os
import pytest

# At Home Refbox
# ToDo: fix imports
import pathlib
import sys
path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from server import Server
from server_types import ServerConfig, ChallengeInfoKeys

EVENT = "RoboCup 2021"
TEAM = "Tech United Eindhoven"
CHALLENGE = "Restaurant"
ATTEMPT = 1
ARENA = "A"
NR_ARENAS = 2
SCORE_VALUE = 100
INFO_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")


async def setup_default_server_and_client(server_path):
    server = _setup_default_server(server_path)
    client = MockSocket()
    # noinspection PyProtectedMember
    await server._register(client)
    return server, client


# noinspection PyProtectedMember
def _setup_default_server(server_path):
    config = ServerConfig(EVENT, INFO_DIR, server_path, NR_ARENAS)
    server = Server(config)
    server._arenastates.set_team(ARENA, TEAM)
    server._arenastates.set_challenge(ARENA, CHALLENGE)
    server._arenastates.set_attempt(ARENA, ATTEMPT)
    return server


def _get_score_key(server, idx):
    # noinspection PyProtectedMember
    challenge_info = server._competition_info.get_challenge_info(CHALLENGE)
    score_item = challenge_info[ChallengeInfoKeys.SCORE_TABLE][idx]
    return score_item[ChallengeInfoKeys.SCORE_KEY]


class MockSocket(object):
    def __init__(self):
        self.send = mock.AsyncMock()

    def get_arena_arg_list(self, arena=ARENA):
        result = []
        for call_args in self.send.call_args_list:
            data = json.loads(call_args.args[0])
            if arena in data:
                result.append(data[arena])
        return result

    def reset_mock(self):
        self.send.reset_mock()

    def check_data(self, required_keys, arena=ARENA):
        call_args_list = self.send.call_args_list
        for data_key in required_keys:
            assert any([data_key in json.loads(call_arg.args[0])[arena] for call_arg in call_args_list]), \
                f"'{data_key}' has not been sent to client"

    def check_score(self, score_key, score_value):
        for arena_data in self.get_arena_arg_list():  # type: dict
            if "current_scores" in arena_data:
                scores = {int(key): value for key, value in arena_data["current_scores"].items()}
                assert scores[score_key] == score_value


async def add_score(server, score_key, score_value):
    data = {ARENA: {"score": {score_key: score_value}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))


# Upon registration, we need to receive metadata, score table, challenge info and standings
# (even if one or more are empty). Although not strictly necessary, all of them (including standings)
# are defined per arena (for easy filtering)
# In principle, there are three types of data:
# 1. Static: never changes:
#     # event
#     # teams
#     # challenges
# 2. Quasi-static: changes based on selecting a new challenge:
#     # challenge info (name, description, score table)
# 3. Dynamic: score info.
#     # Hereto, challenge, team as well as attempt are required
#     # This must be sent on receiving a score, or setting team or attempt
# Where standings are sent is a choice. We might choose to do this upon each quasi-static update (1 & 2)

@pytest.mark.asyncio
async def test_registration(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.check_data([
        "event",
        "availableTeams",
        "availableChallenges",
        "metadata",
        "challenge_info",
        "standings",
    ])


@pytest.mark.asyncio
async def test_registration_empty(tmpdir):
    config = ServerConfig(EVENT, INFO_DIR, tmpdir, NR_ARENAS)
    server = Server(config)
    client = MockSocket()
    # noinspection PyProtectedMember
    await server._register(client)
    client.check_data([
        "event",
        "availableTeams",
        "availableChallenges",
        "metadata",
        "standings"
    ])


@pytest.mark.asyncio
async def test_metadata(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    metadata = {}
    for data in client.get_arena_arg_list():  # type: dict
        if "metadata" in data:
            metadata = data["metadata"]
    assert metadata
    assert all([item in metadata for item in ["team", "challenge", "attempt"]])


@pytest.mark.asyncio
async def test_set_team(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.reset_mock()
    data = {ARENA: {"setting": {"team": "Hibikino Musashi"}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))
    client.check_data(["metadata", "current_scores"])


@pytest.mark.asyncio
async def test_set_challenge(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.reset_mock()
    data = {ARENA: {"setting": {"challenge": "Restaurant"}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))
    client.check_data(["metadata", "challenge_info", "current_scores"])


@pytest.mark.asyncio
async def test_challenge_info(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.reset_mock()
    data = {ARENA: {"setting": {"challenge": "Restaurant"}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))
    call_args_list = client.send.call_args_list
    call_dicts = [json.loads(call_arg.args[0])[ARENA] for call_arg in call_args_list]
    # ToDo: use 'get_arena_arg_list'
    for call_dict in call_dicts:  # type: dict
        if "challenge_info" in call_dict:
            for key in ["name", "description", "score_table"]:
                assert(key in call_dict["challenge_info"])


@pytest.mark.asyncio
async def test_set_attempt(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    score_key = _get_score_key(server, 0)
    await add_score(server, score_key, SCORE_VALUE)
    client.reset_mock()
    data = {ARENA: {"setting": {"attempt": 2}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))
    client.check_data(["metadata", "current_scores"])
    client.check_score(score_key, 0)


@pytest.mark.asyncio
async def test_set_attempt_str(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    score_key = _get_score_key(server, 0)
    await add_score(server, score_key, SCORE_VALUE)
    client.reset_mock()
    data = {ARENA: {"setting": {"attempt": "2"}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))
    client.check_data(["metadata", "current_scores"])
    client.check_score(score_key, score_value=0)


@pytest.mark.asyncio
async def test_set_attempt_twice(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    score_key = _get_score_key(server, 0)
    await add_score(server, score_key, SCORE_VALUE)
    data = {ARENA: {"setting": {"attempt": "2"}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))
    score_key1 = _get_score_key(server, 1)
    await add_score(server, score_key1, SCORE_VALUE)
    client.reset_mock()
    data = {ARENA: {"setting": {"attempt": "1"}}}
    # noinspection PyProtectedMember
    await server._process_message(json.dumps(data))
    print(f"Server state: {server._score_register._cache}")
    client.check_data(["metadata", "current_scores"])
    client.check_score(score_key, SCORE_VALUE)


@pytest.mark.asyncio
async def test_score(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.reset_mock()
    score_key = _get_score_key(server, 0)
    await add_score(server, score_key, SCORE_VALUE)
    assert(any(["current_scores" in item for item in client.get_arena_arg_list()]))
    client.check_score(score_key, SCORE_VALUE)
