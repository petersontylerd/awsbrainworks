## libraries
import ast
import boto3
import os
import subprocess
import sys
import time
from concurrent import futures

# custom imports
sys.path.append("{}/.aws".format(os.environ["WORKSPACE"]))
sys.path.append("{}/awsbrainworks".format(os.environ["WORKSPACE"]))

import aws_attributes
import awsbrainworks


def parse_buckets_arg(self, buckets):
    """
    Documentation:

        ---
        Description:
            Transform bucket name(s) into a list.

        ---
        Parameters:
            buckets : str
                String containing s3 bucket names. To pass multiple s3
                bucket names, have the string take the form of a
                comma-separated list of s3 bucket names

        ---
        Returns:
            buckets : list
                List containing one string per s3 bucket specified.
    """
    # if the string provided has a comma in it, treat this is a string
    # containing multiple s3 buckets, and turn this into a list of
    # separate strings
    if "," in buckets:
        buckets = buckets.split(",")

    # otherwise, wrap the single bucket name in a list
    else:
        buckets = [buckets]

    return buckets

def upload_directory_to_bucket(self, bucket_name, local_directory):
    """
    Documentation:

        ---
        Description:
            Upload local directory to s3 bucket. s3 bucket directory takes
            the same name of the local directory.

        ---
        Parameters:
            bucket_name : str
                Name of s3 bucket.
            local_directory : str
                Local directory to upload to bucket
    """
    def error(e):
        raise e

    # walk through each folder and file within the local directory
    def walk_local_directory(local_directory):
        for root, _, files in os.walk(local_directory, onerror=error):
            for f in files:
                yield os.path.join(root, f)
    # upload each file
    def upload_file(filename):
        self.s3_client.upload_file(
            Filename=filename,
            Bucket=bucket_name,
            Key=os.path.join(local_directory, os.path.relpath(filename, local_directory)),
        )

    # execute upload process
    with futures.ThreadPoolExecutor() as executor:
        futures.wait(
            [executor.submit(upload_file, filename) for filename in walk_local_directory(local_directory)],
            return_when=futures.FIRST_EXCEPTION,
        )

def upload_file_to_bucket(self, bucket_name, file_name):
    """
    Documentation:

        ---
        Description:
            Upload individual local file to s3 bucket. File on s3 bucket
            takes the same name as the local file.

        ---
        Parameters:
            bucket_name : str
                Name of s3 bucket.
            file_name : str
                Name of file to transfer
    """
    self.s3_resource.Bucket(bucket_name).upload_file(file_name, file_name)