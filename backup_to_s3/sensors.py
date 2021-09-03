import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from dagster import sensor, RunRequest, SkipReason
from dagster.utils import make_email_on_pipeline_failure_sensor

load_dotenv()

INTERVAL = int(os.environ["INTERVAL_CHECK_SECONDS"])
BACKUP_FOLDER = os.environ["BACKUP_FOLDER"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]


@sensor(
    pipeline_name="upload_file_pipeline",
    minimum_interval_seconds=INTERVAL,
    mode="production_mode",
)
def new_files_sensor():
    """
    If there's one or more new file(s) in the backup folder,
    we launch the pipeline. To not process the same file twice, we use
    the filename + last modified date as the run_key
    If no files found, a SkipReason is yielded to inform us
    """
    filenames = os.listdir(BACKUP_FOLDER)
    has_files = False
    files_to_process = []
    for filename in filenames:
        full_filename_path = Path(BACKUP_FOLDER, filename)
        if os.path.isfile(full_filename_path):
            files_to_process.append(filename)
            last_modified = time.ctime(os.path.getmtime(full_filename_path))
            run_key = filename + " " + last_modified
            has_files = True

            yield RunRequest(
                run_key=re.sub(r"[^A-Za-z0-9]+", "_", run_key),
                run_config={
                    "solids": {
                        "get_bucket_objects": {
                            "config": {"bucket_name": S3_BUCKET_NAME}
                        },
                        "upload_file": {
                            "config": {
                                "filename": filename,
                                "backup_folder": BACKUP_FOLDER,
                            }
                        },
                    }
                },
            )

    if not has_files:
        yield SkipReason("No files found.")


# When an error happens, we'll receive an email alert with some basic info
email_on_pipeline_failure = make_email_on_pipeline_failure_sensor(
    email_from=EMAIL_FROM,
    email_password=EMAIL_PASSWORD,
    email_to=[EMAIL_TO],
    name="email_on_backup_s3_pipeline_failure",
)
