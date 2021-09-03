import boto3
from dagster import resource, ModeDefinition


@resource
def get_s3_client(init_context):
    s3_client = boto3.client("s3")
    return s3_client


@resource
def get_s3_resource(init_context):
    s3_resource = boto3.resource("s3")
    return s3_resource


production_mode = ModeDefinition(
    "production_mode",
    resource_defs={"s3_client": get_s3_client, "s3_resource": get_s3_resource},
)
