import os
import yaml

class CompetitionInfo(object):
    def __init__(self, data_dir, event):
        self._event = event
        event_dir = os.path.join(data_dir, event)
        self._teams = self._load_teams(event_dir)

    @staticmethod
    def _load_teams(event_dir):
        with open(os.path.join(event_dir, "teams.yaml"), "r") as f:
            teams = yaml.safe_load(f)
        return teams

    def list_teams(self):
        return list(self._teams)
