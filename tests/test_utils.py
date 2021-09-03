import sys
import unittest

sys.path.insert(0, "..")
from backup_to_s3.utils import get_future_s3_filename


class TestGetFutureS3Filename(unittest.TestCase):
    def setUp(self):
        self.bucket_objects = ["picture.jpg", "temp.txt", "file.c", "file-1.c"]

    def test_no_filename_in_bucket_objects(self):
        """
        No filename in bucket so the final filename in the bucket
        should be the same one as the input
        """
        future_filename = get_future_s3_filename("dont_exist.py", self.bucket_objects)
        self.assertEqual(future_filename, "dont_exist.py")

    def test_filename_exists_but_only_one(self):
        """
        The filename already exists but with no suffix
        e.g temp.txt exists but not temp-1.txt
        The updated filename should thus have the prefix -1
        """
        future_filename = get_future_s3_filename("temp.txt", self.bucket_objects)
        self.assertEqual(future_filename, "temp-1.txt")

    def test_filename_exists_many_duplicates(self):
        """
        The filename already exists + at least another one with a suffix
        e.g temp.txt exists, temp-1.txt also exists
        The updated filename should thus have a prefix,
        the number will depend on the duplicate with the highest number
        """
        future_filename = get_future_s3_filename("file.c", self.bucket_objects)
        self.assertEqual(future_filename, "file-2.c")
