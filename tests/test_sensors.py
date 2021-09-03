import sys
import unittest
from importlib import reload
from dagster import validate_run_config, SkipReason
from test.support import EnvironmentVarGuard

sys.path.insert(0, "../backup_to_s3")

from pipelines import upload_file_pipeline


class TestNewFilesSensor(unittest.TestCase):
    def setUp(self):
        """
        We use the tests folder as a backup folder so '.'
        Our sensors require environmental variables so we have to 'mock' them
        """
        self.env = EnvironmentVarGuard()
        self.env.set("INTERVAL", "10")
        self.env.set("BACKUP_FOLDER", ".")
        self.env.set("S3_BUCKET_NAME", "useless-bucket")
        self.env.set("EMAIL_FROM", "email_from@gmail.com")
        self.env.set("EMAIL_PASSWORD", "dummy_pwd")
        self.env.set("EMAIL_TO", "email_to@gmail.com")

    def test_sensor(self):
        """
        We know that there're files in the tests folder
        So run requests should be yielded
        For an empty folder, only a SkipReason should be yielded
        """
        with self.env:
            # We have to put it here to override the .env file
            # present in the backup_to_s3 folder
            from sensors import new_files_sensor

            for run_request in new_files_sensor():
                assert validate_run_config(upload_file_pipeline, run_request.run_config)

        # We switch now to an empty folder
        self.env.set("BACKUP_FOLDER", "empty_folder_for_tests")
        with self.env:
            import sensors

            sensors = reload(sensors)
            for run_request in sensors.new_files_sensor():
                self.assertIsInstance(run_request, SkipReason)
