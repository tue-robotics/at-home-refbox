import os

# At Home Refbox
# ToDo: fix imports
import pathlib
import sys
path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from competition_info import CompetitionInfo

EVENT = "RoboCup 2021"


def create_challenge_info():
    path = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")
    info = CompetitionInfo(path, EVENT)
    return info


def test_list_teams():
    info = create_challenge_info()
    team_list = info.list_teams()
    assert(len(team_list) == 3)  # There are three team names in the testfile
    assert(all([isinstance(item, str) for item in team_list]))


def test_list_challenges():
    info = create_challenge_info()
    challenge_list = info.list_challenges()
    assert(len(challenge_list) == 2)  # There are two challenge names in the testfile
    assert(all([isinstance(item, str) for item in challenge_list]))


def test_immutability():
    info = create_challenge_info()
    info.list_teams().append('foo')
    info.list_challenges().append('bar')
    assert(len(info.list_teams()) == 3)
    assert(len(info.list_challenges()) == 2)
