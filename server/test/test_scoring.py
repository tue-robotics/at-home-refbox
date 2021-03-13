import os
import pathlib
import pytest
import sys

# ToDo: duplicated in many files, move to test_utils?
path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from competition_info import CompetitionInfo, load_challenge_info
from scoring import get_score_computer
from server_types import MetaData, Record

EVENT = "RoboCup 2021"
DATA_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")

ATTEMPT = 1
TEAM = "Tech United Eindhoven"
SCORE_KEY = 3387669373
SCORE_INCREMENT = 100


# ToDo: duplicate (e.g., from test competition info)
def create_challenge_info() -> CompetitionInfo:
    info = CompetitionInfo(DATA_DIR, EVENT)
    return info


def get_challenge_info(challenge):
    info = create_challenge_info()  # type: CompetitionInfo
    return info.get_challenge_info(challenge=challenge)


def test_last_or_mean():
    challenge = "Restaurant"
    challenge_info = get_challenge_info(challenge)
    score_computer = get_score_computer(challenge_info)
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT};{SCORE_KEY};{SCORE_INCREMENT}")
    score_computer.add_record(record)  # Add the records to the score computer
    score_computer.get_scores()  # Get the results

