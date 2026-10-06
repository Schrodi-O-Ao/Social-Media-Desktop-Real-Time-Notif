import unittest
from pathlib import Path
from unittest.mock import patch

from aoo.models import Channel
from aoo.storage import Store


class StoreTests(unittest.TestCase):
    def test_reads_old_channel_file_and_writes_the_new_shape(self) -> None:
        store = Store(Path("data"))
        old_data = [{"ID": 0, "channelID": "UC123", "channelName": "Plain name"}]
        with patch.object(Store, "_read", return_value=old_data):
            self.assertEqual(store.load_channels(), [Channel("UC123", "Plain name")])
        with patch.object(Store, "_write") as write:
            store.save_channels([Channel("UC456", "New name")])
        self.assertEqual(write.call_args.args[1], [{"channel_id": "UC456", "name": "New name"}])

    def test_bad_json_does_not_stop_the_app(self) -> None:
        with patch.object(Store, "_read", return_value="not a mapping"):
            self.assertEqual(Store(Path("data")).load_seen(), {})


if __name__ == "__main__":
    unittest.main()
