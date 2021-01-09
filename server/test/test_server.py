import json
import mock
import pytest

# At Home Refbox
# ToDo: fix imports
import pathlib
import sys
path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from server import Server

EVENT = "RoboCup 2021"
TEAM = "Tech United Eindhoven"
CHALLENGE = "Restaurant"
ATTEMPT = 1
ARENA = "A"
SCORE_KEY = 123
SCORE_VALUE = 100


async def setup_default_server_and_client(path):
    server = _setup_default_server(path)
    client = MockSocket()
    # noinspection PyProtectedMember
    await server._register(client)
    return server, client

# noinspection PyProtectedMember
def _setup_default_server(path):
    server = Server(path, EVENT)
    server._competition.set_team(ARENA, TEAM)
    server._competition.set_challenge(ARENA, CHALLENGE)
    server._competition.set_attempt(ARENA, ATTEMPT)
    return server


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


def _check_data(client, required_keys, arena=ARENA):
    call_args_list = client.send.call_args_list
    for item in call_args_list:
        print(item)
    for data_key in required_keys:
        assert any([data_key in json.loads(call_arg.args[0])[arena] for call_arg in call_args_list]), \
            f"'{data_key}' has not been sent to client"


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
    _check_data(client, ["event", "metadata", "challenge_info", "standings"])


@pytest.mark.asyncio
async def test_registration_empty(tmpdir):
    server = Server(tmpdir, EVENT)
    client = MockSocket()
    # noinspection PyProtectedMember
    await server._register(client)
    _check_data(client, ["event", "metadata",  "challenge_info", "standings"])


@pytest.mark.asyncio
async def test_metadata(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    metadata = {}
    for data in client.get_arena_arg_list():
        if "metadata" in data:
            metadata = data["metadata"]
    assert metadata
    assert all([item in metadata for item in ["team", "challenge", "attempt"]])


@pytest.mark.asyncio
async def test_set_team(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.reset_mock()
    arena_data = {"setting": {"team": "Hibikino Musashi"}}
    # noinspection PyProtectedMember
    await server._on_setting(ARENA, arena_data)
    _check_data(client, ["metadata", "current_scores"])


@pytest.mark.asyncio
async def test_set_challenge(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.reset_mock()
    arena_data = {"setting": {"challenge": "Restaurant"}}
    # noinspection PyProtectedMember
    await server._on_setting(ARENA, arena_data)
    _check_data(client, ["metadata", "challenge_info", "current_scores"])


@pytest.mark.asyncio
async def test_score(tmpdir):
    server, client = await setup_default_server_and_client(tmpdir)
    client.reset_mock()
    data = {"score": {SCORE_KEY: SCORE_VALUE}}
    # noinspection PyProtectedMember
    await server._on_score(ARENA, data)
    assert(any(["current_scores" in item for item in client.get_arena_arg_list()]))
    for arena_data in client.get_arena_arg_list():
        if "current_scores" in arena_data:
            scores = {int(key): value for key, value in arena_data["current_scores"].items()}
            assert scores[SCORE_KEY] == SCORE_VALUE
