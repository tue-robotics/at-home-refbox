from server_types import ChallengeInfoKeys, Record, ScoreKeys

def get_score_computer(challenge_info):
    return LastOrMean(challenge_info)


class LastOrMean(object):
    def __init__(self, challenge_info: dict):
        """
        Computes the score for the records that have been added based on the scheme
        defined by the challenge info

        :param challenge_info: contains information to compute the result from the score records
        """
        self._challenge_info = challenge_info
        self._records = list()

    def add_record(self, record: Record):
        """
        Adds a record to the ScoreComputer

        :param record:
        """
        self._check_record(record)
        self._records.append(record)

    def _check_record(self, record: Record):
        """
        Checks if the team and challenge of the provided record are equal to the
        team and challenge of the first record in the set

        :param record: Record to test
        :raises: AssertionError
        """
        if not self._records:
            return

        first_record = self._records[0]
        assert record.metadata.team == first_record.metadata.team, \
            f"Team {record.metadata.team} is not equal to previous ({first_record.metadata.team})"
        assert record.metadata.challenge == first_record.metadata.challenge, \
            f"Challenge {record.metadata.challenge} is not equal to previous ({first_record.metadata.challenge})"

    def get_scores(self):
        score_table = self._challenge_info[ChallengeInfoKeys.SCORE_TABLE]
        nr_attempts = self._challenge_info[ChallengeInfoKeys.NR_ATTEMPTS]
        scores = {attempt: {item["key"]: 0 for item in score_table} for attempt in range(nr_attempts)}

        for record in self._records:  # type: Record
            scores[record.metadata.attempt][record.score_key] += record.score_increment
        return {ScoreKeys.SCORES: scores}

