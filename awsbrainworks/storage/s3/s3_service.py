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


def get_buckets(self):
    """
    Documentation:

        ---
        Description:
            Associate each S3 bucket name with its S3 bucket object.

        ---
        Returns:
           raw_bucket : dict
                Dictonary where the keys are S3 bucket names and the
                values are the associated S3 bucket objects.
    """
    # gather S3 bucket object for each S3 bucket name
    raw_buckets = {}
    for instance in self.s3_resource.buckets.all():
        raw_buckets[instance.name] = instance

    return raw_buckets

def get_bucket_names(self):
    """
    Documentation:

        ---
        Description:
            Gather all Name tags of active EC2 instances.

        ---
        Returns:
            instance_names : list
                List containing Name tags of all active EC2 instances.
    """
    # return dictionary containing S3 bucket name / S3 bucket object pairs
    raw_buckets = self.get_buckets()

    # distill bucket names from raw_buckets dictionary
    bucket_names = [bucket_name for bucket_name in raw_buckets.keys()]
    return bucket_names