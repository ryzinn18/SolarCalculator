# src/utils/delete_expired.py
from boto3 import resource as boto_resource, client as boto_client
from pydantic import BaseModel

import datetime as dt

BUCKET_NAMES = ['sc-outputs-csv', 'sc-outputs-graph-cost', 'sc-outputs-graph-energy']
S3_CLIENT = boto_client('s3')
S3_RESOURCE = boto_resource('s3')
DYNAMODB = boto_resource('dynamodb')


# From Utils
class Status(BaseModel):
    status_code: int
    message: str


# From Utils
def check_http_response(response_code: int) -> bool:
    """Check if a response code is non 200 and if so, and return correct bool value."""

    if (not response_code) or (response_code < 200) or (response_code >= 300):
        return False
    else:
        return True


# From Utils (though modified)
def delete_s3_obj(bucket_name: str, obj_key: str) -> int:
    """Delete an s3 object given bucket name and object's key and return the http response code."""

    response = S3_RESOURCE.Object(bucket_name, obj_key).delete()

    return response['ResponseMetadata']['HTTPStatusCode']


def get_expired_s3_items(bucket_name: str):
    """Removes objects from S3 buckets that are older than 1 week."""

    week_ago = dt.date.today() - dt.timedelta(weeks=1)
    objects = S3_CLIENT.list_objects(Bucket=bucket_name)

    expired_items = []
    for obj in objects["Contents"]:
        if obj["LastModified"].date() < week_ago:
            expired_items.append(obj['Key'])

    return expired_items


def delete_expired_s3_items(bucket_name):
    """Coordinates the deletion of expired S3 objects."""

    expired_items = get_expired_s3_items(bucket_name=bucket_name)
    failed_deletions = []
    for item in expired_items:
        response = delete_s3_obj(bucket_name=bucket_name, obj_key=item)
        if not response:
            # Log error for failed deletion
            failed_deletions.append(item)

    return failed_deletions


def cleanup_handler(event: dict, context):
    """Lambda handler function for deleting expired objects."""

    failed_deletions = []
    for bucket in BUCKET_NAMES:
        failed = delete_expired_s3_items(bucket_name=bucket)
        [failed_deletions.append(fail) for fail in failed]

    if not failed_deletions:
        return {
            "status": Status(
                status_code=200,
                message="All expired items were deleted."
            ).dict()
        }
    else:
        return {
            "failed_deletions": failed_deletions,
            "status": Status(
                status_code=206,
                message="Not all expired items were deleted."
            ).dict()
        }


if __name__ == "__main__":
    delete_expired_s3_items(bucket_name=BUCKET_NAMES[2])
