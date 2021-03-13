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
    SCORE_TABLE = "score_table"
    SCORE_KEY = "key"
    SCORE_INCREMENT = "scoreIncrement"
    MAX_SCORE = "maxScore"


class ScoreKeys(object):
    SCORES = "scores"
    SUBTOTALS = "subtotals"
    TOTAL = "total"
