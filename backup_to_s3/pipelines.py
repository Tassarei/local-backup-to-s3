from dagster import pipeline

from solids import get_bucket_objects, upload_file
from resources_modes import production_mode


@pipeline(
    mode_defs=[
        production_mode,
    ]
)
def upload_file_pipeline():
    """
    Main pipeline, we first need to get the bucket name and the list of bucket
    objects in that folder(it will allow us to not overwrite existing objects).
    Then we update the filename with maybe a different name so as not to
    overwrite any existing filename in that bucket.
    """
    bucket_name, bucket_objects = get_bucket_objects()
    upload_file(bucket_name, bucket_objects)
