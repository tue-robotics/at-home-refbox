import os
import yaml

class CompetitionInfo(object):
    def __init__(self, data_dir, event):
        self._event = event
        event_dir = os.path.join(data_dir, event)
        self._teams = self._load_teams(event_dir)
        self._challenges = self._load_challenges(event_dir)

    @staticmethod
    def _load_teams(event_dir):
        with open(os.path.join(event_dir, "teams.yaml"), "r") as f:
            teams = yaml.safe_load(f)
        return teams

    @staticmethod
    def _load_challenges(event_dir):
        with open(os.path.join(event_dir, "challenges.yaml"), "r") as f:
            challenges = yaml.safe_load(f)
        return challenges

    @property
    def event(self):
        return self._event

    def list_teams(self):
        return list(self._teams)

    def list_challenges(self):
        return list(self._challenges)
