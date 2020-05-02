## libraries
import boto3
import subprocess
import time

import os
import sys

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"workspace", "awsbrainworks"))

import aws_attributes
import awsbrainworks


class AWSBrainEC2InstanceService:
    """
    Documentation:

        ---
        Description:
            Gather information about current utilization of EC2 service.
    """

    from .compute.ec2.ec2_service import (
        get_instances,
        get_instance_name_tags,
        get_instance_names,
        get_instance_types,
        get_raw_instances,
        go_create_ssh_key,
    )

    def __init__(self):
        """
        Documentation:

            ---
            Description:
                Create EC2 instance client and resource APIs.

            ---
            Attributes:
                ec2_resource : EC2 instance resource object
                    EC2 instance resource API
                ec2_client : EC2 instance client object
                    EC2 instance client API

        """

        self.ec2_resource = boto3.resource("ec2")
        self.ec2_client = boto3.client("ec2")

class AWSBrainEC2InstanceManager(AWSBrainEC2InstanceService):
    """
    Documentation:

        ---
        Description:
            Manage EC2 instance-related tasks.
    """

    from .compute.ec2.ec2_interact import (
        access_instance,
        get_block_storage_detail,
        get_block_storage_device_ext4_status,
        get_instance,
        get_instance_username,
        get_scp_tunnel,
        get_ssh_tunnel,
        go_modify_instance_type,
        go_reboot_instance,
        go_start_instance,
        go_stop_instance,
        go_terminate_instance,
        import_s3_buckets_into_ebs_volume,
    )

    def __init__(self, instance_name=None):
        """
        Documentation:

            ---
            Description:
                Access and interact with an individual EC2 instance.

            ---
            Parameters:
                instance_name : str, default=None
                    Name of EC2 instance Name corresponds to the "Name" tag associated with the instance.
                    This is an optional parameter.

            ---
            Attributes:
                instance : EC2 instance object
                    EC2 instance object. Only gets created if a valid value is provided to instance_name.

        """
        AWSBrainEC2InstanceService.__init__(self)
        self.instance_name = instance_name

        # if instance_name is provided, get instance
        if self.instance_name is not None:

            # check to ensure there exists an EC2 instance with the specified name
            assert self.instance_name in self.get_instance_names(), "No active EC2 instance with that name."

            # get EC2 instance object
            self.instance = self.get_instance()

class AWSBrainEC2InstanceCreator(AWSBrainEC2InstanceManager):
    """
    Documentation:

        ---
        Description:
            Launch new EC2 instance.
    """

    from .compute.ec2.ec2_create import (
        get_ami_id,
        get_user_data_status,
        go_launch_instance,
        go_setup_aws,
        go_setup_bash,
        go_setup_python,
    )

    def __init__(self, instance_name, key_name, ami_name, instance_type, volume_name=None, volume_size=None, buckets_to_sync=None, user_data=None, shutdown_behavior="stop"):
        """
        Documentation:

            ---
            Description:
                Launch new EC2 instance.

            ---
            Parameters:
                instance_name : str
                    Name of instance. The value is stored as a tag, and the associated key is "Name".
                key_name : str
                    Name of private SSH .pem file stored locally.
                ami_name : str
                    Name of Amazon Machine Image (AMI) to use when creating instance.
                instance_type : str
                    The type of computing environment.
                volume_name : str, default=None
                    Name of EBS volume drive. Optional.
                volume_size : int or float, default=None
                    Size in gigabytes of the EBS volume. Optional
                buckets_to_sync : str or list, default=None
                    Name(s) of S3 bucket object(s) to sync. Provide as a string or a list of strings.
                user_data : str, default=None
                    Optional shell script executed as instance is first created.
                shutdown_behavior : str, default="stop"
                    Action to perform upon stopping. Options include "stop" and "terminate".
        """
        AWSBrainEC2InstanceManager.__init__(self)

        self.instance_name = instance_name
        self.key_name = key_name
        self.ami_name = ami_name
        self.instance_type = instance_type
        self.volume_name = volume_name
        self.volume_size = volume_size
        self.buckets_to_sync = buckets_to_sync
        self.user_data = user_data
        self.shutdown_behavior = shutdown_behavior

        # make sure there isn't already an EC2 instance with the specified name
        assert self.instance_name not in self.get_instance_names(), "\nThere is already an active EC2 instance with that name.\n"

        # # make sure EC2 instance type is among available instance types
        # assert self.instance_type in self.get_instance_types(), "\ninstance_type '{}' not among available options.\n".format(self.instance_type)

        # check to ensure that both volume_name and volume_size are provided if either is provided
        if self.volume_name is not None or self.volume_size is not None:
            assert self.volume_name is not None, "volume_name must be provided with volume_size."
            assert self.volume_size is not None, "volume_size must be provided with volume_name."

            # check that volume name is available
            current_volume_names = AWSBrainEBSVolumeService().get_volume_names()
            assert self.volume_name not in current_volume_names, "volume_name already in use."

        # check to ensure that both volume_name and volume_size are provided if buckets_to_sync is provided
        if self.buckets_to_sync is not None:
            assert self.volume_name is not None, "both volume_name and volume size must be provided with buckets_to_sync."
            assert self.volume_size is not None, "both volume_name and volume size must be provided with buckets_to_sync."

class AWSBrainS3BucketService:
    """
    Documentation:

        ---
        Description:
            Gather information about S3 buckets.

    """

    from .storage.s3.s3_service import (
        get_bucket_names,
        get_buckets,
    )

    def __init__(self):
        """
        Documentation:

            ---
            Description:
                Create EC2 instance client and resource APIs.

            ---
            Attributes:
                s3_resource : S3 bucket resource object
                    S3 bucket resource API
                s3_client : S3 bucket client object
                    S3 bucket client API
        """
        self.s3_resource = boto3.resource("s3")
        self.s3_client = boto3.client("s3")

class AWSBrainS3BucketManager(AWSBrainS3BucketService):
    """
    Documentation:

        ---
        Description:
            Interact with S3 services.
    """
    from .storage.s3.s3_interact import (
        get_bucket,
        get_s3_bucket_contents,
        go_delete_bucket_file,
        go_delete_bucket_folder,
        go_empty_bucket,
        go_upload_local_object_to_bucket,
        parse_buckets_arg,
    )

    def __init__(self, bucket_name=None):
        """
        Documentation:

            ---
            Description:
                Manage S3 bucket-related tasks.

            ---
            Parameters:
                bucket_name : str, default=None
                    Name of S3 bucket
        """
        AWSBrainS3BucketService.__init__(self)

        self.bucket_name = bucket_name

        # if bucket_name is provided, get bucket
        if self.bucket_name is not None:

            # check to ensure there exists an EC2 instance with the specified name
            assert self.bucket_name in self.get_bucket_names(), "No S3 bucket with that name."

            # get EC2 instance object
            self.bucket = self.get_bucket()

class AWSBrainS3BucketCreator(AWSBrainS3BucketManager):
    """
    Documentation:

        ---
        Description:
            Create new S3 bucket.
    """
    from .storage.s3.s3_create import (
        create_bucket,
    )


    def __init__(self, bucket_name):
        """
        Documentation:

            ---
            Description:
                Create new S3 bucket.

            ---
            Parameters:
                bucket_name : str
                    Name of S3 bucket
        """
        AWSBrainS3BucketManager.__init__(self)

        self.bucket_name = bucket_name

class AWSBrainEBSVolumeService:
    """
    Documentation:

        ---
        Description:
            Gather information about EBS volumes.
    """
    from .storage.ebs.ebs_service import (
        get_raw_volumes,
        get_volume_name_tags,
        get_volume_names,
        get_volumes,
    )

    def __init__(self):
        """
        Documentation:

            ---
            Description:
                Create EBS client and resource APIs.

            ---
            Attributes:
                ebs_resource : EBS volume resource object
                    EBS volume resource API
                ebs_client : EBS volume client object
                    EBS volume client API

        """
        self.ebs_resource = boto3.resource("ec2")
        self.ebs_client = boto3.client("ec2")

class AWSBrainEBSVolumeManager(AWSBrainEBSVolumeService):
    """
    Documentation:

        ---
        Description:
            Interact with EBS services.
    """
    from .storage.ebs.ebs_interact import (
        get_volume,
        get_volume_device_name,
        go_attach_volume,
        go_delete_volume,
        go_detach_volume,
    )

    def __init__(self, volume_name=None):
        """
        Documentation:

            ---
            Description:
                Manage EBS volume-related tasks.

            ---
            Parameters:
                volume_name : str
                    Name of EBS volume.
                ebs_volume_size : int or float
                    Size in gigabytes of the EBS volume.

        """
        AWSBrainEBSVolumeService.__init__(self)

        self.volume_name = volume_name

        # if instance_name is provided, get instance and instance_username
        if self.volume_name is not None:

            # check to ensure there exists an EBS volume with the specified name
            assert self.volume_name in self.get_volume_names(), "No EBS volume with that name."

            # get EBS volume object
            self.volume = self.get_volume()

class AWSBrainEBSVolumeCreator(AWSBrainEBSVolumeManager):
    """
    Documentation:

        ---
        Description:
            Create new EBS volume.
    """
    from .storage.ebs.ebs_create import (
        go_create_volume,
    )

    def __init__(self, volume_name, volume_size, volume_type="gp2"):
        """
        Documentation:

            ---
            Description:
                Create new EBS volume.

            ---
            Parameters:
                volume_name : str
                    Name of EBS volume. Applied as a tag.
                volume_size : int
                    Size of EBS volume in gigabytes.
                volume_type : str, default="gp2"
                    Type of storage.
        """
        AWSBrainEBSVolumeManager.__init__(self)

        self.volume_name = volume_name
        self.volume_size = volume_size
        self.volume_type = volume_type

        # make sure there isn't already an EBS volume with the specified name
        assert self.volume_name not in self.get_volume_names(), "\nThere is already an EBS volume with that name.\n"
