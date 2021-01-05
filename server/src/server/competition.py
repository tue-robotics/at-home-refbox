import copy
from server_types import MetaData

class Competition(object):
    def __init__(self, event):
        self._event = event
        self._metadatas = {
            "A": {"team": "", "challenge": "", "attempt": 0},
            "B": {"team": "", "challenge": "", "attempt": 0},
        }

    @property
    def event(self):
        return self._event

    def set_team(self, arena, team):
        self._metadatas[arena].update({"team": team})

    def set_challenge(self, arena, challenge):
        self._metadatas[arena].update({"challenge": challenge})

    def set_attempt(self, arena, attempt):
        self._metadatas[arena].update({"attempt": attempt})

    def get_metadata(self, arena):
        return MetaData(**self._metadatas[arena])

    def get_metadata_dict(self, arena):
        return copy.deepcopy(self._metadatas[arena])
