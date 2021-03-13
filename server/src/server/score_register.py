import threading
import time

from server_types import MetaData, Record, ScoreKeys



class ScoreRegister(object):
    def __init__(self, event: str, db_filename: str):
        self._event = event
        self._db_filename = db_filename
        self._cache = self._load_cache()
        self._file_lock = threading.RLock()

    def _load_cache(self):
        try:
            return self._try_load_cache()
        except (FileNotFoundError, IOError):
            return []

    def _try_load_cache(self):
        cache = []
        with open(self._db_filename, "r") as f:
            for line in f:
                cache.append(Record.from_csv_string(line))
        return cache

    def register_score(self, metadata: MetaData, score_key: int, score_increment: int):
        record = Record(time.time(),
                        self._event,
                        metadata,
                        score_key,
                        score_increment
                        )
        self._cache.append(record)
        self._write_record_to_file(record)

    def _write_record_to_file(self, record):
        with self._file_lock:
            with open(self._db_filename, "a") as f:
                f.writelines([record.to_csv_string()])

    def get_score(self, metadata, score_table):
        # result = {ScoreKeys.SCORES: {}, ScoreKeys.SUBTOTALS: {}, ScoreKeys.TOTAL: 0}
        scores = {}
        # result = {item["key"]: 0 for item in score_table}
        for record in self._cache:  # type: Record
            # Add attempt to scores
            if record.metadata.team == metadata.team and record.metadata.challenge == metadata.challenge:
                if record.metadata.attempt not in scores:
                    scores[record.metadata.attempt] = {item["key"]: 0 for item in score_table}
            if self._should_update(metadata, score_table, record):
                scores[record.metadata.attempt][record.score_key] += record.score_increment
        return {ScoreKeys.SCORES: scores}

    @staticmethod
    def _should_update(metadata, score_table, record):
        return any([item["key"] == record.score_key for item in score_table]) and metadata == record.metadata
