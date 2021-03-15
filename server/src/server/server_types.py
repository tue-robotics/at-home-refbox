import collections
import json


ServerConfig = collections.namedtuple("ServerConfig", [
    "event", "info_dir", "db_dir", "nr_arenas"
])


class MetaData(object):
    def __init__(self, team, challenge, attempt):
        self._team = team
        self._challenge = challenge
        self._attempt = int(attempt)

    @property
    def team(self):
        return self._team

    @property
    def challenge(self):
        return self._challenge

    @property
    def attempt(self):
        return self._attempt

    def to_dict(self):
        return {"team": self.team, "challenge": self.challenge, "attempt": str(self.attempt)}

    def to_json_string(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json_string(cls, json_string):
        data = json.loads(json_string)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data):
        return cls(data["team"], data["challenge"], int(data["attempt"]))

    def __eq__(self, other):
        return  self.team == other.team and \
            self.challenge == other.challenge and \
            self.attempt == other.attempt


RecordData = collections.namedtuple("Record", ["stamp", "event", "metadata", "score_key", "score_increment"])


# noinspection PyClassHasNoInit
class Record(RecordData):
    def to_csv_string(self):
        raw_data = [
            self.stamp,
            self.event,
            self.metadata.team,
            self.metadata.challenge,
            self.metadata.attempt,
            self.score_key,
            self.score_increment,
        ]
        assert not any([";" in str(item) for item in raw_data])
        data = [str(item) for item in raw_data]
        result = ";".join(data) + "\n"
        return result

    @classmethod
    def from_csv_string(cls, input_str):
        args = input_str.rstrip().split(";")
        stamp = float(args[0])
        event = args[1]
        meta_data = MetaData(args[2], args[3], int(args[4]))
        score_key = int(args[5])
        score_increment = int(args[6])
        return cls(stamp, event, meta_data, score_key, score_increment)


class SendKeys(object):
    EVENT = "event"
    TEAMS = "availableTeams"
    CHALLENGES = "availableChallenges"
    METADATA = "metadata"
    CHALLENGE_INFO = "challenge_info"
    CURRENT_SCORES = "current_scores"
    STANDINGS = "standings"


class ReceiveKeys(object):
    SETTING = "setting"
    SCORE = "score"


class SettingKeys(object):
    TEAM = "team"
    CHALLENGE = "challenge"
    ATTEMPT = "attempt"


class ChallengeInfoKeys(object):
    NAME = "name"
    DESCRIPTION = "description"
    AVAILABLE_ATTEMPTS = "availableAttempts"
    NR_ATTEMPTS = "nr_attempts"
    SCORING_SYSTEM = "scoringSystem"
    SCORE_TABLE = "score_table"
    SCORE_KEY = "key"
    SCORE_INCREMENT = "scoreIncrement"
    MAX_SCORE = "maxScore"


class ScoreKeys(object):
    SCORES = "scores"
    SUBTOTALS = "subtotals"
    TOTAL = "total"


class ScoringSystem(object):
    LAST_OR_MEAN = "last_or_mean"
    MEAN_DROP_WORST = "mean_drop_worst"
