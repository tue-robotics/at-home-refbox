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
from score_register import Record, ScoreRegister
from server_types import MetaData, ScoreKeys

SCORE_TABLE = [
    {"key": 123, "description": 'Detect customer', "scoreIncrement": 100, "maxScore": 100},
    {"key": 124, "description": 'Get Order from customer', "scoreIncrement": 100, "maxScore": 300},
    {"key": 125, "description": 'Request order from cook', "scoreIncrement": 100, "maxScore": 300},
    {"key": 126, "description": 'Deliver order', "scoreIncrement": 100, "maxScore": 300},
]

EVENT = "RoboCup 2021"
ATTEMPT = 1
METADATA = MetaData('Tech United Eindhoven', 'Restaurant', ATTEMPT)
SCORE_KEY = 123
SCORE_INCREMENT = 100


def test_record_serialization_deserialization():
    original_record = Record(time.time(), EVENT, METADATA, SCORE_KEY, SCORE_INCREMENT)
    csv = original_record.to_csv_string()
    recreated_record = Record.from_csv_string(csv)
    assert original_record == recreated_record


def test_record_serialization_comma():
    metadata = MetaData('Tech,United,Eindhoven', 'Restaurant', ATTEMPT)
    original_record = Record(time.time(), EVENT, metadata, SCORE_KEY, SCORE_INCREMENT)
    csv = original_record.to_csv_string()
    recreated_record = Record.from_csv_string(csv)
    assert original_record == recreated_record


def test_record_serialization_semicolon():
    metadata = MetaData('Tech;United;Eindhoven', 'Restaurant', ATTEMPT)
    record = Record(time.time(), EVENT, metadata, SCORE_KEY, SCORE_INCREMENT)
    with pytest.raises(AssertionError):
        record.to_csv_string()


def test_register_score(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)


def test_get_score_single(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    current_scores = register.get_score(METADATA, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][ATTEMPT]
    assert current_score[SCORE_KEY] == SCORE_INCREMENT


def test_get_score_double(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    current_scores = register.get_score(METADATA, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][ATTEMPT]
    assert current_score[SCORE_KEY] == 2 * SCORE_INCREMENT


def test_different_metadata(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    metadata2 = MetaData(METADATA.team, METADATA.challenge, METADATA.attempt+1)
    register.register_score(metadata=metadata2, score_key=SCORE_KEY + 1, score_increment=2 * SCORE_INCREMENT)
    current_scores = register.get_score(METADATA, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][ATTEMPT]
    assert current_score[SCORE_KEY] == SCORE_INCREMENT
    current_scores = register.get_score(metadata2, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][metadata2.attempt]
    assert current_score[SCORE_KEY + 1] == 2 * SCORE_INCREMENT


def test_get_score_negative(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=-SCORE_INCREMENT)
    current_scores = register.get_score(METADATA, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][ATTEMPT]
    assert current_score[SCORE_KEY] == 0


def test_load_from_file(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    register2 = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    current_scores = register2.get_score(METADATA, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][ATTEMPT]
    assert current_score[SCORE_KEY] == SCORE_INCREMENT


def test_load_from_file_multiple_lines(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    register2 = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    current_scores = register2.get_score(METADATA, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][ATTEMPT]
    assert current_score[SCORE_KEY] == 2 * SCORE_INCREMENT


def test_load_from_file_twice(tmpdir):
    register = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    register2 = ScoreRegister(EVENT, os.path.join(tmpdir, "db.csv"))
    register2.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    current_scores = register2.get_score(METADATA, SCORE_TABLE)
    current_score = current_scores[ScoreKeys.SCORES][ATTEMPT]
    assert current_score[SCORE_KEY] == 2 * SCORE_INCREMENT


def test_corrupt_file(tmpdir):
    filename = os.path.join(tmpdir, "db.csv")
    register = ScoreRegister(EVENT, filename)
    register.register_score(metadata=METADATA, score_key=SCORE_KEY, score_increment=SCORE_INCREMENT)
    with open(filename, "a") as f:
        f.write("\nfoo")
    with pytest.raises(ValueError):
        ScoreRegister(EVENT, filename)

