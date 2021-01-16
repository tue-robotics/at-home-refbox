import os
import pytest
import time


# At Home Refbox
# ToDo: fix imports
import pathlib
import sys
path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from competition_info import CompetitionInfo

EVENT = "RoboCup 2021"

def test_list_teams():
    path = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")
    print(f"Path: {path}")
    info = CompetitionInfo(path, EVENT)
    team_list = info.list_teams()
    assert(len(team_list) == 3)  # There are three team names in the testfile
    assert(all([isinstance(item, str) for item in team_list]))
