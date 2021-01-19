# At Home Refbox
# ToDo: fix imports
import pathlib
import sys
path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from competition import Competition
from server_types import MetaData

EVENT = "RoboCup 2021"
TEAM = "Tech United Eindhoven"
CHALLENGE = "Restaurant"
ATTEMPT = 1
ARENA = "A"

def test_setup():
    competition = Competition("RoboCup 2021")
    competition.set_team(ARENA, TEAM)
    competition.set_challenge(ARENA, CHALLENGE)
    competition.set_attempt(ARENA, ATTEMPT)
    assert competition.get_metadata(ARENA) == MetaData(TEAM, CHALLENGE, ATTEMPT)


def test_dict():
    competition = Competition("RoboCup 2021")
    competition.set_team(ARENA, TEAM)
    competition.set_challenge(ARENA, CHALLENGE)
    competition.set_attempt(ARENA, ATTEMPT)
    reference_dict = {"team": TEAM, "challenge": CHALLENGE, "attempt": 1}
    assert all([competition.get_metadata_dict(ARENA)[key] == reference_dict[key] for key in reference_dict.keys()])
