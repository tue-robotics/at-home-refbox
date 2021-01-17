import copy
import os
import typing
import yaml

from server_types import ChallengeInfoKeys


class CompetitionInfo(object):
    def __init__(self, data_dir: str, event: str):
        self._event = event
        event_dir = os.path.join(data_dir, event)
        self._teams = load_teams(event_dir)
        self._challenges = load_challenges(event_dir)
        self._challenge_infos = load_challenge_infos(event_dir, self._challenges)

    @property
    def event(self) -> str:
        return self._event

    def list_teams(self) -> typing.List[str]:
        return list(self._teams)

    def list_challenges(self) -> typing.List[str]:
        return list(self._challenges)

    def get_challenge_info(self, challenge: str) -> dict:
        return copy.deepcopy(self._challenge_infos[challenge])


def load_teams(event_dir: str) -> typing.List[str]:
    with open(os.path.join(event_dir, "teams.yaml"), "r") as f:
        teams = yaml.safe_load(f)
    return teams


def load_challenges(event_dir: str) -> typing.List[str]:
    with open(os.path.join(event_dir, "challenges.yaml"), "r") as f:
        challenges = yaml.safe_load(f)
    return challenges


def load_challenge_infos(event_dir: str, challenges: typing.List[str]) -> dict:
    result = {}
    for challenge in challenges:
        challenge_info = load_challenge_info(event_dir, challenge)
        result[challenge] = challenge_info
    return result


def load_challenge_info(event_dir: str, challenge: str) -> dict:
    with open(os.path.join(event_dir, challenge + ".yaml"), "r") as f:
        raw_info = yaml.safe_load(f)
        challenge_info = _extend_info(challenge, raw_info)
    return challenge_info


def _extend_info(challenge: str, raw_info: dict) -> dict:
    raw_info[ChallengeInfoKeys.NAME] = challenge
    raw_info[ChallengeInfoKeys.SCORE_TABLE] = _add_keys_to_score_table(
        challenge, raw_info[ChallengeInfoKeys.SCORE_TABLE
        ])
    return raw_info


def _add_keys_to_score_table(challenge, score_table):
    for item in score_table:
        item[ChallengeInfoKeys.KEY] = _get_score_key(challenge, item)
    return score_table


def _get_score_key(challenge, item):
    description = item[ChallengeInfoKeys.DESCRIPTION]
    return hash(challenge + " - " + description)






