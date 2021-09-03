import sys
import mock
import unittest
import boto3
from moto import mock_s3
from dagster import build_solid_context, Output, AssetKey, AssetMaterialization

sys.path.insert(0, "../backup_to_s3")

from solids import get_bucket_objects, upload_file


class TestSolids(unittest.TestCase):
    @mock_s3
    def setUp(self):
        """
        We can't create the bucket and objects here
        because when we go from the setUp func to a test, they will disappear
        As a filename to upload, we use this file
        """
        self.s3_client = boto3.client("s3")
        self.s3_resource = boto3.resource("s3")
        self.bucket_name = "bucket_test"
        self.first_key = "first_object"
        self.second_key = "second_object"
        self.filename = "test_solids.py"

    @mock_s3
    def test_get_bucket_objects(self):
        """
        We upload two objects and we retrieve them via get_bucket_objects
        We should receive back the bucket name
        and a list of the two keys of the objects
        """
        self.s3_resource.create_bucket(Bucket=self.bucket_name)
        self.s3_client.put_object(
            Bucket=self.bucket_name, Key=self.first_key, Body="Body of the object"
        )
        self.s3_client.put_object(
            Bucket=self.bucket_name, Key=self.second_key, Body="Second object!"
        )

        context = build_solid_context(
            resources={"s3_resource": self.s3_resource},
            config={"bucket_name": self.bucket_name},
        )
        bucket_name, bucket_objects = get_bucket_objects(context)

        self.assertEqual(bucket_name.value, self.bucket_name)
        self.assertEqual(
            bucket_objects.value.sort(), [self.first_key, self.second_key].sort()
        )

    @mock_s3
    @mock.patch("solids.os")
    def test_upload_file(self, mock_os):
        """
        We try to upload a file to s3.
        An asset Materialization and an output should be yielded if the
        operation succeeds.
        We mock the os.remove so as not to remove this file.
        """
        self.s3_resource.create_bucket(Bucket=self.bucket_name)
        self.s3_client.put_object(
            Bucket=self.bucket_name, Key=self.first_key, Body="Body of the object"
        )

        context = build_solid_context(
            resources={"s3_client": self.s3_client},
            config={"filename": self.filename, "backup_folder": "."},
        )
        asset, output = upload_file(
            context,
            self.bucket_name,
            [
                self.first_key,
            ],
        )

        self.assertIsInstance(asset, AssetMaterialization)
        self.assertEqual(asset.asset_key, AssetKey(["test_solids_py"]))
        self.assertIsInstance(output, Output)
        mock_os.remove.assert_called_with(self.filename)
