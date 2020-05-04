## libraries
import ast
import boto3
import os
import subprocess
import sys
import time
from concurrent import futures

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"workspace", "awsbrainworks"))

import aws_attributes
import awsbrainworks

def get_bucket(self):
    """
    Documentation:

        ---
        Description:
            Use bucket name to return a single S3 bucket object.

        ---
        Returns:
            bucket : S3 bucket
                S3 bucket object
    """
    # return
    # 6 dictionary containing Name tag / EC2 instance object
    buckets = self.get_buckets()

    # check that there is an instance with that name
    assert self.bucket_name in self.get_bucket_names(), "\nNo S3 bucket with that name.\n"

    # filter instances by instance_name
    bucket = buckets[self.bucket_name]

    return bucket

def get_s3_bucket_contents(self, prefix="", extensions=None):
    """
    Documentation:

        ---
        Description:
            Retrieve all files from a specified folder in an S3 bucket,
            optionally filtering by one or more file extensions

        ---
        Returns:
            prefix : str, default=""
                Filter contents by object Key prefix.
            extensions : str or list
                Optional parameter for filter folder contents to one or more
                file extension types.
    """
    # get all files in bucket
    try:
        bucket_files = [file["Key"] for file in self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)["Contents"]]
    except KeyError:
        print("S3 bucket '{}' is empty.".format(self.bucket_name))

    # filter
    if extensions is not None:
        # build extensions filter if provided
        if isinstance(extensions, str):
            extensions = [extensions]

        # ensure each extension begins with "."
        extensions = [ext if ext.startswith(".") else "." + ext for ext in extensions]

        # filter bucket_files based on specified extensions
        bucket_files = [file for file in bucket_files if any(file.endswith(ext) for ext in extensions)]

    return bucket_files

def go_delete_bucket_file(self, file_name):
    """
    Documentation:

        ---
        Description:
            Use bucket name to return a single S3 bucket object.

        ---
        RetuParametersrns:
            file_name : str
                Name of file to delete.
    """
    # ensure that file_name is among existing S3 bucket files
    assert file_name in self.get_s3_bucket_contents(), "file_name not among existing S3 bucket files"

    self.s3_resource.Object(self.bucket_name, file_name).delete()

def go_delete_bucket_folder(self, folder_name):
    """
    Documentation:

        ---
        Description:
            Use bucket name to return a single S3 bucket object.

        ---
        Parametters:
            folder_name : str
                Name of folder to delete.
    """
    if folder_name[-1] != "/":
        folder_name = folder_name + "/"

    # make sure file is among objects in bucket
    self.bucket.objects.filter(Prefix=folder_name).delete()

def go_empty_bucket(self):
    """
    Documentation:

        ---
        Description:
            Use bucket name to return a single S3 bucket object.
    """
    self.bucket.objects.all().delete()

def parse_buckets_arg(self, buckets):
    """
    Documentation:

        ---
        Description:
            Transform bucket name(s) into a list.

        ---
        Parameters:
            buckets : str
                String containing S3 bucket names. To pass multiple S3
                bucket names, have the string take the form of a
                comma-separated list of S3 bucket names

        ---
        Returns:
            buckets : list
                List containing one string per S3 bucket specified.
    """
    # if the string provided has a comma in it, treat this is a string
    # containing multiple S3 buckets, and turn this into a list of
    # separate strings
    if "," in buckets:
        buckets = buckets.split(",")

    # otherwise, wrap the single bucket name in a list
    else:
        buckets = [buckets]

    return buckets

def go_upload_local_object_to_bucket(self, local_object, prefix=""):
    """
    Documentation:

        ---
        Description:
            Upload local object to S3 bucket. S3 object takes the same name of the
            local directory. Function detects whether the local object is a file or
            a folder. If a folder is provided, the entire folder is loaded into S3
            bucket.

            Note - The folder or file will be placed at the root directory of the
            S3 bucket. If the desired outcomes is for the folder or file to be placed
            in a folder within the S3 bucket, add a prefix.

        ---
        Parameters:
            local_object : str
                Local object to upload to bucket.
            prefix : str, default=""
                Optional string to append to front of S3 object name.
    """
    assert os.path.isdir(local_object) or os.path.isfile(local_object), "Cannot locate local object based on directory provided."

    # if the local_object is a reference to a folder
    if os.path.isdir(local_object):
        print("folder")
        def error(e):
            raise e

        # walk through each folder and file within the local directory
        def walk_local_directory(local_object):
            for root, _, files in os.walk(local_object, onerror=error):
                for f in files:
                    yield os.path.join(root, f)

        # upload each file
        def upload_file(filename):
            self.s3_client.upload_file(
                Filename=filename,
                Bucket=self.bucket_name,
                Key=os.path.join(prefix, local_object.split("/")[-1], os.path.relpath(filename, local_object)),
            )

        # execute upload process
        with futures.ThreadPoolExecutor() as executor:
            futures.wait(
                [executor.submit(upload_file, filename) for filename in walk_local_directory(local_object)],
                return_when=futures.FIRST_EXCEPTION,
            )

    # if the local_object is a reference to a file
    elif os.path.isfile(local_object):
        print("file")
        self.s3_client.upload_file(
            local_object,
            self.bucket_name,
            os.path.join(prefix,local_object.split("/")[-1]),
        )
