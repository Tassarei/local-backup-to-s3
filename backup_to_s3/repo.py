from dagster import repository

from sensors import new_files_sensor, email_on_pipeline_failure
from pipelines import upload_file_pipeline


@repository
def backup_to_s3_repository():
    return [new_files_sensor, email_on_pipeline_failure, upload_file_pipeline]
