
## libraries
import ast
import boto3
from botocore.exceptions import ClientError
import os
import subprocess
import sys
import time

# custom imports
sys.path.append(os.path.join(os.environ["HOME"], ".aws_attributes"))
sys.path.append(os.path.join(os.environ["HOME"],"workspace", "awsbrainworks"))

import aws_attributes
import awsbrainworks


def get_instance(self):
    """
    Documentation:

        ---
        Description:
            Use a Name tag to return a single EC2 instance object.

        ---
        Returns:
            instance : EC2 instance
                EC2 instance object
    """
    # return
    # 6 dictionary containing Name tag / EC2 instance object
    instances = self.get_instances()

    # check that there is an instance with that name
    assert self.instance_name in self.get_instance_names(), "\nNo active instance with that name.\n"

    # filter instances by instance_name
    instance = instances[self.instance_name]

    return instance

def get_instance_username(self):
    """
    Documentation:

        ---
        Description:
            Determine instance username based on AMI type. If the AMI is
            an ubuntu image, the username is "ubuntu". If the AMI is an
            AWS image, the username is "ec2-root".

        ---
        Returns:
            instance_username : str
                User name associated with EC2 instance.
    """
    # use EC2 instance's image_id to determine
    ami_name = aws_attributes.AMI_NAME_MAPPINGS[self.instance.image_id]

    instance_username = "ec2-user" if "aws" in ami_name else "ubuntu"

    return instance_username

def get_ssh_tunnel(self):
    """
    Documentation:

        ---
        Description:
            Create SSH string. On its own, can be used to SSH into an instance. Can also
            be used with another command line script to execute a command on an EC2
            instance.

        ---
        Returns:
            ssh_tunnel : str
                Command line script for tunneling into EC2 instance using SSH.
    """
    # retrieve instance_username
    instance_username = self.get_instance_username()

    # create prefix for SSH tunneling command line script
    ssh_tunnel = "ssh -o 'StrictHostKeyChecking no' -i {}/.ssh/{}.pem {}@{}".format(
                                                                                os.environ["HOME"],
                                                                                self.instance.key_name,
                                                                                instance_username,
                                                                                self.instance.public_dns_name
                                                                            )
    return ssh_tunnel

def get_scp_tunnel(self):
    """
    Documentation:

        ---
        Description:
            Create secure copy (scp) string.  Can be used with another command
            line script to securely copy a local file to an EC2 instance.

        ---
        Returns:
            ssh_tunnel : str
                Command line script for tunneling into EC2 instance using SSH.
    """
    # create prefix for scp tunneling command line script
    scp_tunnel = """scp -i {}/.ssh/{}.pem """.format(
                                                    os.environ["HOME"],
                                                    self.instance.key_name,
                                                )
    return scp_tunnel

def go_access_instance(self):
    """
    Documentation:

        ---
        Description:
            Use SSH to remote into running EC2 instance.

    """
    ssh_tunnel = self.get_ssh_tunnel()
    subprocess.run(ssh_tunnel, shell=True)

def get_block_storage_detail(self, ssh_tunnel):
    """
    Documentation:

        ---
        Description:
            Gather detail of EC2 instance file system. Output is stored in a
             JSON file and returns as a dictionary.

        ---
        Parameters:
            ssh_tunnel : str
                String for using SSH to remotely execute script on EC2 instance.

        ---
        Returns:
            block_storage_detail : dict
                Dictionary containing block storage detail.
    """
    # command line script that create json file of lsblk output
    check_file = """ "lsblk --json -o KNAME,MAJ:MIN,FSTYPE,MOUNTPOINT,LABEL,UUID,PARTTYPE,PARTLABEL,PARTUUID,PARTFLAGS,RA,RO,RM,HOTPLUG,MODEL,SERIAL,SIZE,STATE,OWNER,MODE,ALIGNMENT,MIN-IO,OPT-IO,PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,DISC-ALN,DISC-GRAN,DISC-MAX,DISC-ZERO,WSAME,WWN,RAND,PKNAME,HCTL,TRAN,SUBSYSTEMS,REV,GROUP,TYPE,VENDOR,ZONED > /tmp/lsblk_status.json" """

    # create json file of lsblk block_storage_detail
    subprocess.run(
        ssh_tunnel + check_file,
        text=True,
        shell=True,
    )

    # read the json file
    block_storage_detail = subprocess.run(
                ssh_tunnel + """ "cat /tmp/lsblk_status.json" """,
                capture_output=True,
                shell=True
            )

    # parse reults
    block_storage_detail = block_storage_detail.stdout.decode("utf-8")
    block_storage_detail = block_storage_detail.replace("\n","")
    block_storage_detail = block_storage_detail.replace("null","None")

    # turn block_storage_detail into a dictionary
    block_storage_detail = ast.literal_eval(block_storage_detail)

    return block_storage_detail

def get_block_storage_device_ext4_status(self, ssh_tunnel, volume_device_name):
    """
    Documentation:

        ---
        Description:
            Check to see if block device is alredy set as an ext4 file system.

        ---
        Parameters:
            ssh_tunnel : str
                String for using SSH to remotely execute script on EC2 instance.
            file_system_name : str
                File system to assess.
    """
    block_storage_detail = self.get_block_storage_detail(ssh_tunnel)

    # identify mountpoint of block_Device_name
    for block in block_storage_detail["blockdevices"]:
        if block["kname"] == volume_device_name:
            result = block["mountpoint"]

    # set block_device_is_ext4 variable
    block_device_is_ext4 = False
    if result is not None:
        block_device_is_ext4 = True
    return block_device_is_ext4

def go_setup_ebs_volume_sync(self, ssh_tunnel, instance_username, volume_device_name, destination_dir="/home/s3buckets"):
    """
    Documentation:

        ---
        Description:
            Prepare EBS volume for synchronization with S3 bucket.

        ---
        Parameters:
            ssh_tunnel : str, default=None
                String for using SSH to remotely execute script on EC2 instance.
            instance_username : str
                EC2 instance username.
            volume_device_name : str
                Device name of EBS volume in EC2 instance
            destination_dir : str, default=/home/s3buckets
                Destination directory for S3 bucket(s) on EBS volume
    """
    ### setup file system
    # treat special (block) files as ordinay ones
    special_files = """ "sudo file --special-files {0}" """.format(volume_device_name)
    subprocess.run(ssh_tunnel + special_files, shell=True)

    # create an ext4 filesystem on the EBS drive, if it's not already ext4
    make_file_system = """ "sudo mkfs -t ext4 {0}" """.format(volume_device_name)
    subprocess.run(ssh_tunnel + make_file_system, shell=True)

    # create a mount point, basically an empty directory
    make_s3_dir = """ "sudo mkdir {0}" """.format(destination_dir)
    subprocess.run(ssh_tunnel + make_s3_dir, shell=True)

    # mount the new volume
    mount_s3_dir = """ "sudo mount {0} {1}" """.format(volume_device_name, destination_dir)
    subprocess.run(ssh_tunnel + mount_s3_dir, shell=True)

    ### update fstab file
    # back up fstab file
    backup_fstab = """ "sudo cp /etc/fstab /etc/fstab.bak" """
    subprocess.run(ssh_tunnel + backup_fstab, shell=True)

    # add s3bucket to fstab
    append_file_system = """ "echo '{0} {1} ext4 defaults,nofail 0 0' | sudo tee -a /etc/fstab.bak >/dev/null" """.format(volume_device_name, destination_dir)
    subprocess.run(ssh_tunnel + append_file_system, shell=True)

    change_owner = """ "sudo chown -R {0}:{0} {1}" """.format(instance_username, destination_dir)
    subprocess.run(ssh_tunnel + change_owner, shell=True)

def go_sync_s3_bucket_to_ebs_volume(self, buckets_to_sync, ssh_tunnel, destination_dir="/home/s3buckets"):
    """
    Documentation:

        ---
        Description:
            Synchronize one or more S3 buckets with an EBS volume attached to an EC2 instance.

        ---
        Parameters:
            buckets_to_sync : str or list
                Preferably a list of strings of S3 buckets. If string is passed,, have
                the string take the form of a comma-separated list of S3 bucket names.
                This will be parsed into a list of string.
            ssh_tunnel : str, default=None
                String for using SSH to remotely execute script on EC2 instance.
            destination_dir : str, default=/home/s3buckets
                Destination directory for S3 bucket(s) on EBS volume
    """
    ### sync buckets
    # sync each bucket
    for bucket in buckets_to_sync:
        directory_name = """ "sudo aws s3 sync s3://{0} {1}/{0}" """.format(bucket, destination_dir)
        subprocess.run(ssh_tunnel + directory_name, shell=True)

def go_sync_ebs_volume_to_s3_bucket(self, buckets_to_sync, ssh_tunnel, ebs_bucket_dir="/home/s3buckets"):
    """
    Documentation:

        ---
        Description:
            Synchronize EBS volume attached to an EC2 instance with an S3 bucket.

        ---
        Parameters:
            buckets_to_sync : str or list
                Preferably a list of strings of S3 buckets. If string is passed,, have
                the string take the form of a comma-separated list of S3 bucket names.
                This will be parsed into a list of string.
            ssh_tunnel : str, default=None
                String for using SSH to remotely execute script on EC2 instance.
            ebs_bucket_dir : str, default=/home/s3buckets
                Location of S3 bucket folder on EBS volume.
    """
    ### sync buckets
    # sync each bucket
    for bucket in buckets_to_sync:
        directory_name = """ "sudo aws s3 sync {1}/{0} s3://{0} --delete" """.format(bucket, ebs_bucket_dir)
        subprocess.run(ssh_tunnel + directory_name, shell=True)

def go_start_instance(self):
    """
    Documentation:

        ---
        Description:
            Start a stopped EC2 instance.
    """
    self.ec2_client.start_instances(
        InstanceIds=[self.instance.id],
        DryRun=False
    )

    ## EC2 Instance wake-up process
    # wait until EC2 instance is running
    print("EC2 Instance '{}' starting...".format(self.instance_name))
    waiter = self.ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[self.instance.id])
    print("Success: EC2 Instance '{}' is now running".format(self.instance_name))

    # wait until EC2 instance has a status of 'ok'
    print("EC2 Instance '{}' initializing...".format(self.instance_name))
    waiter = self.ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[self.instance.id])
    print("Success: EC2 Instance '{}' status is now ok".format(self.instance_name))

def go_stop_instance(self, hibernate=False):
    """
    Documentation:

        ---
        Description:
            Stop a running EC2 instance.

        ---
        Parameters:
            hibernate : boolean
                Conditional controlling whether to hibernate the stopped instance.
    """
    self.ec2_client.stop_instances(
        InstanceIds=[self.instance.id],
        Hibernate=hibernate,
        DryRun=False
    )

    ## EC2 Instance wake-up process
    ## waiter
    custom_filter = [{
                "Name":"tag:Name",
                "Values": [self.instance_name]
            },
    ]

    # wait until EC2 instance is available
    print("EC2 Instance '{}' stopping...".format(self.instance_name))
    waiter = self.ec2_client.get_waiter('instance_stopped')
    waiter.wait(Filters=custom_filter)
    print("Success: EC2 Instance '{}' now stopped".format(self.instance_name))

def go_terminate_instance(self):
    """
    Documentation:

        ---
        Description:
            Terminate an EC2 instance.
    """
    self.ec2_client.terminate_instances(
        InstanceIds=[self.instance.id],
        DryRun=False
    )

    ## EC2 Instance wake-up process
    ## waiter
    custom_filter = [{
                "Name":"tag:Name",
                "Values": [self.instance_name]
            },
    ]

    # wait until EC2 instance is available
    print("EC2 Instance '{}' terminating...".format(self.instance_name))
    waiter = self.ec2_client.get_waiter('instance_terminated')
    waiter.wait(Filters=custom_filter)
    print("Success: EC2 Instance '{}' now terminated".format(self.instance_name))

def go_reboot_instance(self):
    """
    Documentation:

        ---
        Description:
            Reboot and EC2 instance.
    """
    self.ec2_client.reboot_instances(
        InstanceIds=[self.instance.id],
        DryRun=False
    )
    # wait until EC2 instance is running
    print("EC2 Instance '{}' starting...".format(self.instance_name))
    waiter = self.ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[self.instance.id])
    print("Success: EC2 Instance '{}' is now running".format(self.instance_name))

    # wait until EC2 instance has a status of 'ok'
    print("EC2 Instance '{}' initializing...".format(self.instance_name))
    waiter = self.ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[self.instance.id])
    time.sleep(10)
    print("Success: EC2 Instance '{}' status is now ok".format(self.instance_name))
    print("Success: EC2 Instance '{}' now rebooted".format(self.instance_name))

def go_modify_instance_type(self, instance_type, stop_if_running=False, restart_instance=False):
    """
    Documentation:

        ---
        Description:
            Modify an EC2 instance's type.

        ---
        Parameters:
            stop_if_running : boolean, default=False
                Conditional controlling whether to stop an instance if it
                is running so that the instance type change can be applied.
            restart_insnce : boolean, default=False
                Conditional controlling whether to restart an instance after changing the
                instance type.


    """
    # # make sure EC2 instance type is among available instance types
    # assert instance_type in self.get_instance_types(), "\ninstance_type '{}' not among available options.\n".format(instance_type)

    # see if EC2 instance type is already set as the requested instance type
    assert self.instance.instance_type != instance_type, "\ninstance_type is already '{}'.\n".format(instance_type)

    try:
        # modify instance type
        self.ec2_client.modify_instance_attribute(
            InstanceId=self.instance.id,
            InstanceType={
                'Value': instance_type,
            },
        )
        print("Success: EC2 Instance '{}' now has the type '{}'".format(self.instance_name, instance_type))

        # start instance
        if restart_instance:
            self.go_start_instance()

    except ClientError:
        # stop instance before proceeding
        self.go_stop_instance()

        # modify instance type
        self.ec2_client.modify_instance_attribute(
            InstanceId=self.instance.id,
            InstanceType={
                'Value': instance_type,
            },
        )
        print("Success: EC2 Instance '{}' now has the type '{}'".format(self.instance_name, instance_type))

        # start instance
        if restart_instance:
            self.go_start_instance()