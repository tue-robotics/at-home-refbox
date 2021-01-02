import os
import threading
import time
from collections import namedtuple

from server_types import MetaData


RecordData = namedtuple("Record", ["stamp", "metadata", "score_key", "score_increment"])

class Record(RecordData):
    def to_csv_string(self):
        data = [str(item) for item in [
            self.stamp,
            self.metadata.event,
            self.metadata.team,
            self.metadata.challenge,
            self.metadata.attempt,
            self.score_key,
            self.score_increment,
        ]]
        result = ",".join(data)
        return result

    @classmethod
    def from_csv_string(cls, input_str):
        args = input_str.split(",")
        print(f"Args: {args}")
        stamp = float(args[0])
        meta_data = MetaData(args[1], args[2], args[3], int(args[4]))
        score_key = int(args[5])
        score_increment = int(args[6])
        return cls(stamp, meta_data, score_key, score_increment)


class ScoreRegister(object):
    def __init__(self, db_filename: str):
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
                        metadata,
                        score_key,
                        score_increment
                        )
        self._cache.append(record)
        self._write_record_to_file(record)

    def _write_record_to_file(self, record):
        with self._file_lock:
            with open(self._db_filename, "a") as f:
                f.write(record.to_csv_string())

    def get_score(self, metadata, score_table):
        result = {item["key"]: 0 for item in score_table}
        for record in self._cache:  # type: Record
            if self._should_update(metadata, score_table, record):
                result[record.score_key] += record.score_increment
        return result

    @staticmethod
    def _should_update(metadata, score_table, record):
        return any([item["key"] == record.score_key for item in score_table]) and metadata == record.metadata
