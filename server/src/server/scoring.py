from server_types import ChallengeInfoKeys, Record, ScoreKeys, ScoringSystem


class ScoreComputer(object):
    def __init__(self, challenge_info: dict):
        """
        Computes the score for the records that have been added based on the scheme
        defined by the challenge info.

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

    def get_results(self) -> dict:
        result = {}

        scores = self._compute_scores_from_records()
        result[ScoreKeys.SCORES] = scores

        subtotals = self._compute_subtotals(scores)
        result[ScoreKeys.SUBTOTALS] = subtotals

        result[ScoreKeys.TOTAL] = self.compute_total(scores, subtotals)

        return result

    def _compute_scores_from_records(self) -> dict:
        score_table = self._challenge_info[ChallengeInfoKeys.SCORE_TABLE]
        nr_attempts = self._challenge_info[ChallengeInfoKeys.NR_ATTEMPTS]
        scores = {attempt + 1: {item["key"]: 0 for item in score_table} for attempt in range(nr_attempts)}
        for record in self._records:  # type: Record
            scores[record.metadata.attempt][record.score_key] += record.score_increment
        return scores

    @staticmethod
    def _compute_subtotals(scores: dict) -> dict:
        return {attempt: sum(scores[attempt].values()) for attempt in range(1, len(scores) + 1)}

    def compute_total(self, scores: dict, subtotals: dict) -> int:
        raise NotImplementedError("compute_total must be implemented by the deriving class")


class LastOrMean(ScoreComputer):
    def __init__(self, challenge_info: dict):
        super().__init__(challenge_info)
        nr_attempts = self._challenge_info[ChallengeInfoKeys.NR_ATTEMPTS]
        assert nr_attempts == 2, "LastOrMean only works with two attempts"

    def compute_total(self, scores: dict, subtotals: dict) -> int:
        if subtotals[2] > subtotals[1]:
            return subtotals[2]
        elif self._used_second_attempt():
            return (subtotals[1] + subtotals[2])/2.
        else:
            return subtotals[1]

    def _used_second_attempt(self) -> bool:
        return any([record.metadata.attempt == 2 for record in self._records])


class MeanDropWorst(ScoreComputer):
    def compute_total(self, scores: dict, subtotals: dict) -> int:
        subtotals_sorted_list = sorted(subtotals.values())
        subtotals_dropped_worst = subtotals_sorted_list[1:]
        return sum(subtotals_dropped_worst)/len(subtotals_dropped_worst)


_SCORING_SYSTEM_MAP = {
    ScoringSystem.LAST_OR_MEAN: LastOrMean,
    ScoringSystem.MEAN_DROP_WORST: MeanDropWorst,
}


# ToDo: proper implementation?
def get_score_computer(challenge_info):
    return _SCORING_SYSTEM_MAP[challenge_info[ChallengeInfoKeys.SCORING_SYSTEM]](challenge_info)
