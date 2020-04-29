## libraries
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append("{}/.aws".format(os.environ["WORKSPACE"]))
# custom imports
sys.path.append("{}/.aws".format(os.environ["WORKSPACE"]))
sys.path.append("{}/awsbrainworks".format(os.environ["WORKSPACE"]))

import aws_attributes
import awsbrainworks


def create_bucket(self, bucket_name):
    """
    Documentation:

        ---
        Description:
            Create a new s3 bucket

        ---
        Parameters:
            bucket_name : str
                Name to give s3 bucket.
    """
    # catch naming convention error
    if "_" in bucket_name:
        raise NameError ("bucket_name cannot include underscores.")

    # create the s3 bucket
    self.s3_client.create_bucket(
        ACL="private",
        Bucket=bucket_name,
        CreateBucketConfiguration={
            "LocationConstraint": aws_attributes.REGION
        },
    )