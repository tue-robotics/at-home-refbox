import json

# At Home Refbox
# ToDo: fix imports
import pathlib
import sys
path = pathlib.Path(__file__).parent.absolute().parent
path = path.joinpath("src", "server")
sys.path.insert(1, str(path))
from server_types import MetaData

METADATA = MetaData('Tech United Eindhoven', 'Restaurant', 1)

def test_record_serialization_deserialization_str():
    json_str = METADATA.to_json_string()
    metadata2 = MetaData.from_json_string(json_str)
    assert METADATA == metadata2


def test_record_serialization_deserialization_str_attempt():
    metadata = MetaData('Tech United Eindhoven', 'Restaurant', '1')
    json_str = metadata.to_json_string()
    metadata2 = MetaData.from_json_string(json_str)
    assert metadata == metadata2


def test_record_serialization_deserialization():
    json_str = METADATA.to_json_string()
    data = json.loads(json_str)
    metadata2 = MetaData.from_dict(data)
    assert METADATA == metadata2
