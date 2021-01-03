from collections import namedtuple
import json

_MetaData = namedtuple('MetaData', ['event', 'team', 'challenge', 'attempt'])

# noinspection PyClassHasNoInit
class MetaData(_MetaData):
    def to_json_string(self):
        data = {"event": self.event, "team": self.team, "challenge": self.challenge, "attempt": str(self.attempt)}
        return json.dumps(data)

    @classmethod
    def from_json_string(cls, json_string):
        data = json.loads(json_string)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data):
        return cls(data["event"], data["team"], data["challenge"], int(data["attempt"]))
