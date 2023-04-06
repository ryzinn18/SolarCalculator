# src/backend/maintenance.py
import schedule
from boto3 import resource as boto_resource, client as boto_client

import datetime as dt

from utils import delete_s3_obj

BUCKET_NAMES = ['sc-outputs-csv', 'sc-outputs-', 'sc-outputs-energy']
S3 = boto_client('s3')
DYNAMODB = boto_resource('dynamodb')


def get_expired_s3_items(bucket_name: str):
    """Removes objects from S3 buckets that are older than 1 week."""

    week_ago = dt.date.today() - dt.timedelta(weeks=1)
    objects = S3.list_objects(Bucket=bucket_name)

    expired_items = []
    for obj in objects["Contents"]:
        if obj["LastModified"].date() < week_ago:
            expired_items.append(obj['Key'])

    return expired_items


def delete_expired_s3_items():
    """Coordinates the deletion of expired S3 objects."""

    for bucket in BUCKET_NAMES:
        expired_items = get_expired_s3_items(bucket_name=bucket)
        for item in expired_items:
            response = delete_s3_obj(bucket_name=bucket, obj_key=item)


if __name__ == "__main__":
    get_expired_s3_items(BUCKET_NAMES[0])