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
SCORE_KEY_RESTAURANT1 = 3387669373
SCORE_INCREMENT_RESTAURANT1 = 100
SCORE_KEY_RESTAURANT2 = 7108977477
SCORE_INCREMENT_RESTAURANT2 = 200

SCORE_KEY_NAVIGATION1 = 2237262804
SCORE_INCREMENT_NAVIGATION1 = 100
SCORE_KEY_NAVIGATION2 = 9539993937
SCORE_INCREMENT_NAVIGATION2 = 200


# ToDo: duplicate (e.g., from test competition info)
def create_challenge_info() -> CompetitionInfo:
    info = CompetitionInfo(DATA_DIR, EVENT)
    return info


def get_challenge_info(challenge):
    info = create_challenge_info()  # type: CompetitionInfo
    return info.get_challenge_info(challenge=challenge)


def get_score_computer_from_challenge(challenge):
    challenge_info = get_challenge_info(challenge)
    return get_score_computer(challenge_info)


def test_last_or_mean_first():
    challenge = "Restaurant"
    score_computer = get_score_computer_from_challenge(challenge)
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT};{SCORE_KEY_RESTAURANT1};{SCORE_INCREMENT_RESTAURANT1}")
    score_computer.add_record(record)  # Add the records to the score computer
    scores = score_computer.get_results()  # Get the results
    assert scores[ScoreKeys.SUBTOTALS][ATTEMPT] == SCORE_INCREMENT_RESTAURANT1
    assert scores[ScoreKeys.TOTAL] == SCORE_INCREMENT_RESTAURANT1


def test_last_or_mean_mean():
    challenge = "Restaurant"
    score_computer = get_score_computer_from_challenge(challenge)
    score_increment1 = 200
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT};{SCORE_KEY_RESTAURANT1};{score_increment1}")
    score_computer.add_record(record)  # Add the records to the score computer
    score_increment2 = 100
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT + 1};{SCORE_KEY_RESTAURANT2};{score_increment2}")
    score_computer.add_record(record)  # Add the records to the score computer
    scores = score_computer.get_results()  # Get the results
    assert scores[ScoreKeys.SUBTOTALS][1] == score_increment1
    assert scores[ScoreKeys.SUBTOTALS][2] == score_increment2
    assert scores[ScoreKeys.TOTAL] == (score_increment1 + score_increment2)/2.


def test_last_or_mean_last():
    challenge = "Restaurant"
    score_computer = get_score_computer_from_challenge(challenge)
    score_increment1 = 100
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT};{SCORE_KEY_RESTAURANT1};{score_increment1}")
    score_computer.add_record(record)  # Add the records to the score computer
    score_increment2 = 200
    assert score_increment2 == 2 * score_increment1  # This is the purpose of the test
    record = Record.from_csv_string(f"0.0;{EVENT};{TEAM};{challenge};{ATTEMPT + 1};{SCORE_KEY_RESTAURANT2};{score_increment2}")
    score_computer.add_record(record)  # Add the records to the score computer
    scores = score_computer.get_results()  # Get the results
    assert scores[ScoreKeys.SUBTOTALS][1] == score_increment1
    assert scores[ScoreKeys.SUBTOTALS][2] == score_increment2
    assert scores[ScoreKeys.TOTAL] == score_increment2


def test_mean_drop_worst():
    challenge = "Navigation"
    score_computer = get_score_computer_from_challenge(challenge)
    record = Record.from_csv_string(
        f"0.0;{EVENT};{TEAM};{challenge};{1};{SCORE_KEY_NAVIGATION2};{SCORE_INCREMENT_NAVIGATION2}")
    score_computer.add_record(record)  # Add the records to the score computer
    record = Record.from_csv_string(
        f"0.0;{EVENT};{TEAM};{challenge};{3};{SCORE_KEY_NAVIGATION1};{SCORE_INCREMENT_NAVIGATION1}")
    score_computer.add_record(record)  # Add the records to the score computer
    scores = score_computer.get_results()
    assert scores[ScoreKeys.SUBTOTALS][1] == SCORE_INCREMENT_NAVIGATION2
    assert scores[ScoreKeys.SUBTOTALS][2] == 0
    assert scores[ScoreKeys.SUBTOTALS][3] == SCORE_INCREMENT_NAVIGATION1
    assert scores[ScoreKeys.TOTAL] == (SCORE_INCREMENT_NAVIGATION1 + SCORE_INCREMENT_NAVIGATION2)/2
