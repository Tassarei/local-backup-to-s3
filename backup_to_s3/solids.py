import os
import re
from dagster import (
    solid,
    AssetMaterialization,
    InputDefinition,
    Output,
    OutputDefinition,
)

from utils import get_future_s3_filename


@solid(
    config_schema={
        "bucket_name": str,
    },
    required_resource_keys={"s3_resource"},
    output_defs=[
        OutputDefinition(name="bucket_name", dagster_type=str),
        OutputDefinition(name="bucket_objects_list", dagster_type=list),
    ],
)
def get_bucket_objects(context):
    """
    Returns the bucket_name given in the environment variable
    and a list of bucket objects names
    """
    bucket_name = context.solid_config["bucket_name"]
    bucket = context.resources.s3_resource.Bucket(bucket_name)
    bucket_objects = bucket.objects.all()
    bucket_objects_list = [elem.key for elem in bucket_objects]
    bucket_objects_list.sort(reverse=True)
    yield Output(bucket_name, output_name="bucket_name")
    yield Output(bucket_objects_list, output_name="bucket_objects_list")


@solid(
    config_schema={"filename": str, "backup_folder": str},
    required_resource_keys={"s3_client"},
    input_defs=[
        InputDefinition("bucket_name", str),
        InputDefinition("bucket_objects", list),
    ],
)
def upload_file(context, bucket_name, bucket_objects):
    """
    Upload the file to the correct bucket in S3.
    We yield an asset materialization to alert us afterwards plus the filename.
    We then delete the file locally.
    """
    os.chdir(context.solid_config["backup_folder"])
    filename = context.solid_config["filename"]
    updated_name = get_future_s3_filename(filename, bucket_objects)
    context.resources.s3_client.upload_file(filename, bucket_name, updated_name)
    yield AssetMaterialization(
        asset_key=filename.replace(".", "_").replace("-", "_"),
        description=f"{filename} has been uploaded to S3!\nFinal name: {updated_name}",
    )
    yield Output(filename)
    os.remove(filename)
    context.log.info(f"{filename} deleted after successful upload to S3.")
