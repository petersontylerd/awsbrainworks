## libraries
import argparse
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

from awsbrainworks import (
    AWSBrainEC2InstanceService,
    AWSBrainEC2InstanceManager,
    AWSBrainEC2InstanceCreator,
    AWSBrainEBSVolumeCreator,
    AWSBrainS3BucketManager,
)


## arguments
parser = argparse.ArgumentParser(description="")

parser.add_argument(
    "--instance_name",
    required=True,
    type=str,
    dest="instance_name",
    help="Name of instance to self.ssh_tunnel.",
    )
parser.add_argument(
    "--key_name",
    required=True,
    type=str,
    dest="key_name",
    help="Name for the SSH key.",
    )
parser.add_argument(
    "--ami_name",
    required=True,
    type=str,
    dest="ami_name",
    help="Type of AMI to self.ssh_tunnel.",
    )
parser.add_argument(
    "--instance_type",
    required=True,
    type=str,
    dest="instance_type",
    help="The type of EC2 instance to create.",
    )
parser.add_argument(
    "--volume_name",
    required=False,
    type=str,
    dest="volume_name",
    help="Name of EBS volume.",
    )
parser.add_argument(
    "--volume_size",
    required=False,
    type=int,
    dest="volume_size",
    help="Size of EBS volume in gigabytes.",
    )
parser.add_argument(
    "--user_data",
    required=False,
    type=str,
    dest="user_data",
    help="Name of shell script to run at self.ssh_tunnel.",
    )
parser.add_argument(
    "--shutdown_behavior",
    required=False,
    type=str,
    dest="shutdown_behavior",
    help="Desired behavior of EC2 instance upon shutdown.",
    )
parser.add_argument(
    "--buckets_to_sync",
    required=False,
    type=str,
    dest="buckets_to_sync",
    help="Name of bucket to sync to EBS volume.",
    )
parser.add_argument(
    "--access_instance",
    required=False,
    default=False,
    action="store_true",
    dest="access_instance",
    help="Controls whether to SSH into instance.",
    )
args = parser.parse_args()


## execute
if __name__ == "__main__":


    ### launch EC2 instance
    # instantiate EC2 launcher
    ec2_launcher = AWSBrainEC2InstanceCreator(
        args.instance_name,
        args.key_name,
        args.ami_name,
        args.instance_type,
        args.volume_name,
        args.volume_size,
        args.buckets_to_sync,
        args.user_data,
        args.shutdown_behavior,
    )

    # parse buckets arg
    if args.buckets_to_sync is not None:
        # instantiate S3 bucket manager
        s3_manager = AWSBrainS3BucketManager()

        # convert input to string to list
        args.buckets_to_sync = s3_manager.parse_buckets_arg(args.buckets_to_sync)

        # if buckets_to_sync is not None, ensure these buckets exist
        assert set(args.buckets_to_sync).issubset(s3_manager.get_bucket_names()), "One or more of the buckets_to_sync does not exist on S3."

    # launch an EC2 instance
    ec2_launcher.go_launch_instance()

    # get scripting strings for interacting with EC2 instance
    scp_tunnel = ec2_launcher.get_scp_tunnel()
    ssh_tunnel = ec2_launcher.get_ssh_tunnel()

    ## Monitor setup and execute startup procedures
    # set gateway params
    attempts = 0
    time_elapsed = 0
    max_attempts=40
    seconds_to_pause=30

    # monitor user data completion
    test_file_exists = ec2_launcher.get_user_data_status(ssh_tunnel=ssh_tunnel)

    while not test_file_exists:

        test_file_exists = ec2_launcher.get_user_data_status(ssh_tunnel=ssh_tunnel)

        if attempts == max_attempts:
            print("Maximum attempts reached. Breaking.")
            break
        else:
            print("User data executing | attempt {} of {}".format(attempts + 1, max_attempts))
            attempts += 1
            time.sleep(seconds_to_pause)

    # report user data status
    if test_file_exists:
        print("\nUSER DATA COMPLETED\n")
    else:
        print("\n!! USER DATA DID NOT FINISH\n")

    ## environment setup
    # AWS
    ec2_launcher.go_setup_aws(
        scp_tunnel=scp_tunnel,
    )

    # bash
    ec2_launcher.go_setup_bash(
        ssh_tunnel=ssh_tunnel,
    )

    # git pulls
    ec2_launcher.go_setup_git_pulls(
        ssh_tunnel=ssh_tunnel,
    )

    # python
    ec2_launcher.go_setup_python(
        ssh_tunnel=ssh_tunnel,
        scp_tunnel=scp_tunnel,
        install_from_requirements=True,
    )

    # docker
    ec2_launcher.go_setup_docker(
        ssh_tunnel=ssh_tunnel,
    )

    # pyenv
    ec2_launcher.go_setup_pyenv(
        ssh_tunnel=ssh_tunnel,
    )

    # give EC2 user sudo privileges
    ec2_launcher.go_make_user_sudo(
        ssh_tunnel=ssh_tunnel,
        instance_username=ec2_launcher.instance_username,
    )

    # # create remote access config file for VS Code
    # ec2_launcher.go_create_vs_code_config()

    ### create EBS volume
    if ec2_launcher.volume_name is not None and ec2_launcher.volume_size is not None:

        # instantiate EBS volume creator
        ebs_volume_creator = AWSBrainEBSVolumeCreator(
            volume_name=ec2_launcher.volume_name,
            volume_size=ec2_launcher.volume_size,
        )

        # create EBS volume
        ebs_volume_creator.go_create_volume()

        # attach EBS volume to EC2 instance
        ebs_volume_creator.go_attach_volume(
            instance_name=ec2_launcher.instance_name,
        )

        # 5 second pause
        time.sleep(5)

        # get device name for EBS volume
        ebs_volume_creator.volume_device_name = ebs_volume_creator.get_volume_device_name()

        # setup EBS volume as file system and prep for sync with S3
        ec2_launcher.go_setup_ebs_volume_sync(
            ssh_tunnel,
            ec2_launcher.instance_username,
            ebs_volume_creator.volume_device_name,
        )

        ### S3 to EBS
        # sync S3 buckets to EBS volume
        if args.buckets_to_sync is not None:

            # sync S3 bucket to EBS volume
            ec2_launcher.go_sync_s3_bucket_to_ebs_volume(
                args.buckets_to_sync,
                ssh_tunnel,
                ec2_launcher.instance_username,
            )

    ### remote access
    # use SSH to remote into EC2 instance
    if args.access_instance:
        ec2_launcher.go_access_instance()