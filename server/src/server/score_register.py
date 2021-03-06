import threading
import time
from collections import namedtuple

from server_types import MetaData


RecordData = namedtuple("Record", ["stamp", "event", "metadata", "score_key", "score_increment"])

# noinspection PyClassHasNoInit
class Record(RecordData):
    def to_csv_string(self):
        raw_data = [
            self.stamp,
            self.event,
            self.metadata.team,
            self.metadata.challenge,
            self.metadata.attempt,
            self.score_key,
            self.score_increment,
        ]
        assert not any([";" in str(item) for item in raw_data])
        data = [str(item) for item in raw_data]
        result = ";".join(data) + "\n"
        return result

    @classmethod
    def from_csv_string(cls, input_str):
        args = input_str.rstrip().split(";")
        stamp = float(args[0])
        event = args[1]
        meta_data = MetaData(args[2], args[3], int(args[4]))
        score_key = int(args[5])
        score_increment = int(args[6])
        return cls(stamp, event, meta_data, score_key, score_increment)


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
        result = {item["key"]: 0 for item in score_table}
        for record in self._cache:  # type: Record
            if self._should_update(metadata, score_table, record):
                result[record.score_key] += record.score_increment
        return result

    @staticmethod
    def _should_update(metadata, score_table, record):
        return any([item["key"] == record.score_key for item in score_table]) and metadata == record.metadata
