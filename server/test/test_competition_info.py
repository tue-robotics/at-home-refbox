import os

# At Home Refbox
# ToDo: fix imports
import pathlib
import sys

import pytest

path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from competition_info import CompetitionInfo, load_challenge_info

EVENT = "RoboCup 2021"
DATA_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")

def create_challenge_info():
    info = CompetitionInfo(DATA_DIR, EVENT)
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


def test_get_challenge_info():
    info = create_challenge_info()
    for challenge in info.list_challenges():
        challenge_info = info.get_challenge_info(challenge)
        check_challenge_info(challenge_info)


def test_get_challenge_info_empty():
    info = create_challenge_info()
    challenge_info = info.get_challenge_info("foo")
    check_challenge_info(challenge_info)


def check_challenge_info(challenge_info):
    assert "name" in challenge_info
    assert "description" in challenge_info
    assert "availableAttempts" in challenge_info
    assert "score_table" in challenge_info
    check_score_table(challenge_info["score_table"])


def check_score_table(score_table):
    unique_score_keys = []
    for item in score_table:
        check_score_item(item)
        unique_score_keys = check_unique_key(item["key"], unique_score_keys)


def check_score_item(item):
    assert "key" in item
    assert isinstance(item["key"], int)
    assert "description" in item
    assert "scoreIncrement" in item
    assert "maxScore" in item


def check_unique_key(key, unique_score_keys):
    assert key not in unique_score_keys
    unique_score_keys.append(key)
    return unique_score_keys


def test_missing_challenge():
    with pytest.raises(FileNotFoundError) as excinfo:
        load_challenge_info(DATA_DIR, "foo")
    assert "foo.yaml" in str(excinfo.value)

