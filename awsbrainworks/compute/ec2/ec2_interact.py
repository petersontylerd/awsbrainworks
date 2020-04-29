
## libraries
import ast
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
                                                                                os.environ["WORKSPACE"],
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
                                                    os.environ["WORKSPACE"],
                                                    self.instance.key_name,
                                                )
    return scp_tunnel

def access_instance(self):
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

def sync_s3_bucket_to_ebs_volume(self, buckets_to_sync, ssh_tunnel, instance_username, volume_device_name, destination_dir="/home/s3buckets"):
    """
    Documentation:

        ---
        Description:
            Synchronize one or more s3 buckets with an EBS volume in an EC2 instance.

        ---
        Parameters:
            buckets_to_sync : str or list
                Preferably a list of strings of s3 buckets. If string is passed,, have
                the string take the form of a comma-separated list of s3 bucket names.
                This will be parsed into a list of string.
            ssh_tunnel : str, default=None
                String for using SSH to remotely execute script on EC2 instance.
            instance_username : str
                EC2 instance username.
            volume_device_name : str
                Device name of EBS volume in EC2 instance
            destination_dir : str, default=/home/s3buckets
                Destination directory for s3 bucket(s) on EBS volume
    """
    print("!!!!")
    print(buckets_to_sync)
    print(ssh_tunnel)
    print(instance_username)
    print(volume_device_name)
    print("!!!!")

    ### setup file system
    # treat special (block) files as ordinay ones
    special_files = """ "sudo file --special-files {0}" """.format(volume_device_name)
    subprocess.run(ssh_tunnel + special_files, shell=True)
    print(1)

    # create an ext4 filesystem on the EBS drive, if it's not already ext4
    make_file_system = """ "sudo mkfs -t ext4 {0}" """.format(volume_device_name)
    subprocess.run(ssh_tunnel + make_file_system, shell=True)
    print(2)

    # create a mount point, basically an empty directory
    make_s3_dir = """ "sudo mkdir {0}" """.format(destination_dir)
    subprocess.run(ssh_tunnel + make_s3_dir, shell=True)
    print(3)

    # mount the new volume
    mount_s3_dir = """ "sudo mount {0} {1}" """.format(volume_device_name, destination_dir)
    subprocess.run(ssh_tunnel + mount_s3_dir, shell=True)
    print(4)

    ### update fstab file
    # back up fstab file
    backup_fstab = """ "sudo cp /etc/fstab /etc/fstab.bak" """
    subprocess.run(ssh_tunnel + backup_fstab, shell=True)
    print(5)

    # add s3bucket to fstab
    append_file_system = """ "echo '{0} {1} ext4 defaults,nofail 0 0' | sudo tee -a /etc/fstab.bak >/dev/null" """.format(volume_device_name, destination_dir)
    subprocess.run(ssh_tunnel + append_file_system, shell=True)
    print(6)

    change_owner = """ "sudo chown -R {0}:{0} {1}" """.format(instance_username, destination_dir)
    subprocess.run(ssh_tunnel + change_owner, shell=True)
    print(7)

    ### sync buckets
    # sync each bucket
    for bucket in buckets_to_sync:
        directory_name = """ "sudo aws s3 sync s3://{0} {1}/{0}" """.format(bucket, destination_dir)
        subprocess.run(ssh_tunnel + directory_name, shell=True)
    print(8)

def modify_instance_type(self, instance_type):
    """
    Documentation:

        ---
        Description:


        ---
        Parameters:
            a : b
                c


    """
    self.ec2_client.modify_instance_attribute(
        InstanceId=instance_id,
        InstanceType={
            'Value': instance_type,
        },
    )