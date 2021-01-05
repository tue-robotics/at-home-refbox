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


# noinspection PyProtectedMember
def _setup_default_server():
    server = Server(EVENT)
    server._competition.set_team(ARENA, TEAM)
    server._competition.set_challenge(ARENA, CHALLENGE)
    server._competition.set_attempt(ARENA, ATTEMPT)
    return server


class MockSocket(object):
    def __init__(self):
        # self.send = mock.MagicMock()
        self.send = mock.AsyncMock()


def _check_data(client, required_keys, arena=ARENA):
    for data_key in required_keys:
        assert any([data_key in json.loads(call_arg.args[0])[arena] for call_arg in client.send.call_args_list]), \
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
async def test_registration():
    server = _setup_default_server()
    client = MockSocket()
    # noinspection PyProtectedMember
    await server._register(client)
    _check_data(client, ["event", "metadata", "challenge_info", "standings"])


@pytest.mark.asyncio
async def test_registration_empty():
    server = Server(EVENT)
    client = MockSocket()
    # noinspection PyProtectedMember
    await server._register(client)
    _check_data(client, ["event", "metadata",  "challenge_info", "standings"])


@pytest.mark.asyncio
async def test_metadata():
    server = _setup_default_server()
    client = MockSocket()
    # noinspection PyProtectedMember
    await server._register(client)
    metadata = {}
    for call_args in client.send.call_args_list:
        data = json.loads(call_args.args[0])
        if ARENA in data:
            arena_data = data[ARENA]
            if "metadata" in data[ARENA]:
                metadata = arena_data["metadata"]
    assert metadata
    assert all([item in metadata for item in ["team", "challenge", "attempt"]])




# @pytest.mark.asyncio
# async def test_set_challenge():
