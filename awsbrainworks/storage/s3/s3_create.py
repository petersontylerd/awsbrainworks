## libraries
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"repos", "awsbrainworks"))

import aws_attributes
import awsbrainworks


def create_bucket(self):
    """
    Documentation:

        ---
        Description:
            Create a new S3 bucket
    """
    # catch naming convention error
    if "_" in self.bucket_name:
        raise NameError ("bucket_name cannot include underscores.")

    # create the S3 bucket
    self.s3_client.create_bucket(
        ACL="private",
        Bucket=self.bucket_name,
        CreateBucketConfiguration={
            "LocationConstraint": aws_attributes.REGION
        },
    )