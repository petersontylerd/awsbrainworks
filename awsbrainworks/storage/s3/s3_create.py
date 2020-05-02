## libraries
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"workspace", "awsbrainworks"))

import aws_attributes
import awsbrainworks


def create_bucket(self, bucket_name):
    """
    Documentation:

        ---
        Description:
            Create a new S3 bucket

        ---
        Parameters:
            bucket_name : str
                Name to give S3 bucket.
    """
    # catch naming convention error
    if "_" in bucket_name:
        raise NameError ("bucket_name cannot include underscores.")

    # create the S3 bucket
    self.s3_client.create_bucket(
        ACL="private",
        Bucket=bucket_name,
        CreateBucketConfiguration={
            "LocationConstraint": aws_attributes.REGION
        },
    )