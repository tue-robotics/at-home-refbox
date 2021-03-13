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
from server_types import MetaData, Record, ScoreKeys

EVENT = "RoboCup 2021"
DATA_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "data")

ATTEMPT = 1
TEAM = "Tech United Eindhoven"
SCORE_KEY = 3387669373
SCORE_INCREMENT = 100
SCORE_KEY2 = 7108977477
SCORE_INCREMENT2 = 200


# ToDo: duplicate (e.g., from test competition info)
def create_challenge_info() -> CompetitionInfo:
    info = CompetitionInfo(DATA_DIR, EVENT)
    return info


def get_challenge_info(challenge):
    info = create_challenge_info()  # type: CompetitionInfo
    return info.get_challenge_info(challenge=challenge)


def test_last_or_mean_first():
    challenge = "Restaurant"
    challenge_info = get_challenge_info(challenge)
    score_computer = get_score_computer(challenge_info)
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT};{SCORE_KEY};{SCORE_INCREMENT}")
    score_computer.add_record(record)  # Add the records to the score computer
    scores = score_computer.get_scores()  # Get the results
    assert scores[ScoreKeys.SUBTOTALS][ATTEMPT] == SCORE_INCREMENT
    assert scores[ScoreKeys.TOTAL] == SCORE_INCREMENT


def test_last_or_mean_mean():
    challenge = "Restaurant"
    challenge_info = get_challenge_info(challenge)
    score_computer = get_score_computer(challenge_info)
    score_increment1 = 200
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT};{SCORE_KEY};{score_increment1}")
    score_computer.add_record(record)  # Add the records to the score computer
    score_increment2 = 100
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT + 1};{SCORE_KEY2};{score_increment2}")
    score_computer.add_record(record)  # Add the records to the score computer
    scores = score_computer.get_scores()  # Get the results
    assert scores[ScoreKeys.SUBTOTALS][1] == score_increment1
    assert scores[ScoreKeys.SUBTOTALS][2] == score_increment2
    assert scores[ScoreKeys.TOTAL] == (score_increment1 + score_increment2)/2.


def test_last_or_mean_last():
    challenge = "Restaurant"
    challenge_info = get_challenge_info(challenge)
    score_computer = get_score_computer(challenge_info)
    score_increment1 = 100
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT};{SCORE_KEY};{score_increment1}")
    score_computer.add_record(record)  # Add the records to the score computer
    score_increment2 = 200
    assert score_increment2 == 2 * score_increment1  # This is the purpose of the test
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT + 1};{SCORE_KEY2};{score_increment2}")
    score_computer.add_record(record)  # Add the records to the score computer
    scores = score_computer.get_scores()  # Get the results
    assert scores[ScoreKeys.SUBTOTALS][1] == score_increment1
    assert scores[ScoreKeys.SUBTOTALS][2] == score_increment2
    assert scores[ScoreKeys.TOTAL] == score_increment2
