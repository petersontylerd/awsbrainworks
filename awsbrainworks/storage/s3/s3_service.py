## libraries
import boto3
import os
import subprocess
import sys
import time

# custom imports
sys.path.append("{}/.aws".format(os.environ["WORKSPACE"]))
sys.path.append("{}/awsbrainworks".format(os.environ["WORKSPACE"]))

import aws_attributes
import awsbrainworks


def get_raw_buckets(self):
    """
    Documentation:

        ---
        Description:
            Associate each s3 bucket name with its s3 bucket object.

        ---
        Returns:
           raw_bucket : dict
                Dictonary where the keys are s3 bucket names and the
                values are the associated s3 bucket objects.
    """
    # gather s3 bucket object for each s3 bucket name
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
    # return dictionary containing s3 bucket name / s3 bucket object pairs
    raw_buckets = self.get_raw_buckets()

    # distill bucket names from raw_buckets dictionary
    bucket_names = [bucket_name for bucket_name in raw_buckets.keys()]
    return bucket_names