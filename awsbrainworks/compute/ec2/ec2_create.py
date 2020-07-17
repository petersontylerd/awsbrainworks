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


def go_launch_instance(self):
        """
        Documentation:

            ---
            Description:
                Launch EC2 instance, setup bash and python environment, and optionally sync one or
                more S3 buckets to EBS volume.
        """
        # check that there is an instance with that name
        assert self.instance_name not in self.get_instance_names(), "\nInstance name already associated with another instance.\n"

        # use custom AMI name to get AMI ID
        ami_id = self.get_ami_id(self.ami_name)

        # identify user data shell script
        user_data_dir = "../../compute/ec2/user_data_files"
        user_data = "{}/pass.sh".format(user_data_dir) if self.user_data is None else "{}/{}".format(user_data_dir, self.user_data)

        # create instance
        self.ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=self.instance_type,
            KeyName=self.key_name,
            MinCount=1,
            MaxCount=1,
             BlockDeviceMappings=[
                {
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 20,
                        'VolumeType': 'standard',
                    },
                },
            ],
            Monitoring={
                "Enabled": False
            },
            Placement={
                "AvailabilityZone": aws_attributes.AVAILABILITY_ZONE,
            },
            SecurityGroupIds=[
                aws_attributes.SECURITY_GROUP_ID,
            ],
            SubnetId=aws_attributes.SUBNET_ID,
            UserData=open("{}".format(user_data)).read(),
            DisableApiTermination=False,
            DryRun=False,
            EbsOptimized=False,
            InstanceInitiatedShutdownBehavior=self.shutdown_behavior,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": self.instance_name,
                        },
                    ],

                },
                {
                    "ResourceType": "volume",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": self.instance_name + "_" + "ebs",
                        },
                    ],

                },
            ],
        )

        ## EC2 Instance wake-up process
        ## waiter

        # wait until EC2 instance is available
        custom_filter = [{
                    "Name":"tag:Name",
                    "Values": [self.instance_name]
                },
        ]
        waiter = self.ec2_client.get_waiter('instance_exists')
        waiter.wait(Filters=custom_filter)
        print("Success: EC2 Instance '{}' now exists".format(self.instance_name))

        # get EC2 instance object for newly created instance
        self.instance = self.get_instance()

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

        # reload EC2 instance
        self.instance.reload()

        # get username
        self.instance_username = self.get_instance_username()


def get_ami_id(self, ami_name):
    """
    Documentation:

        ---
        Description:
            Get AMI ID based on custom AMI name.

        ---
        Parameters:
            ami_name : str
                Custom AMI name.
    """
    # check to ensure ami_name is among
    assert ami_name.lower() in aws_attributes.AMI_NAMES, "ami_name provided is not in list of options. use one of these: \n\t- 'aws_basic'\n\t- 'aws_deep'\n\t- 'ubuntu_1804_basic'\n\t- 'ubuntu_1804_deep'"

    # use ami_name to retrieve ami_id
    ami_id = aws_attributes.AMI_ID_MAPPINGS[ami_name]

    return ami_id

def go_setup_git_pulls(self, ssh_tunnel):
    """
    Documentation:

        ---
        Description:
            Run command to pull git repos.

        ---
        Parameters:
            ssh_tunnel : str
                String for using SSH to remotely execute script on EC2 instance.
    """
    # git pulls
    git_pulls = """ "{}" """.format(open("../../compute/setup/git/setup_git_pulls.sh").read())
    subprocess.run(ssh_tunnel + git_pulls, shell=True)


def go_setup_docker(self, ssh_tunnel):
    """
    Documentation:

        ---
        Description:
            Run series of commands to setup docker and docker compose.

        ---
        Parameters:
            ssh_tunnel : str
                String for using SSH to remotely execute script on EC2 instance.
    """
    # install docker
    docker_install = """ "{}" """.format(open("../../compute/setup/docker/docker_install.sh").read())
    subprocess.run(ssh_tunnel + docker_install, shell=True)

    # install docker compose
    docker_compose_install = """ "{}" """.format(open("../../compute/setup/docker/docker_compose_install.sh").read())
    subprocess.run(ssh_tunnel + docker_compose_install, shell=True)

    # add username to groups
    docker_setup = """ "{}" """.format(open("../../compute/setup/docker/docker_setup.sh").read())
    subprocess.run(ssh_tunnel + docker_setup, shell=True)


def go_setup_bash(self, ssh_tunnel):
    """
    Documentation:

        ---
        Description:
            Run series of commands to setup various bash environment attributes. Includes bash
            aliases, bash functions, git configuration, and bash profile configurations.

        ---
        Parameters:
            ssh_tunnel : str
                String for using SSH to remotely execute script on EC2 instance.
    """
    # setup bash aliases
    bash_aliases = """ "{}" """.format(open("../../compute/setup/bash/setup_bash_aliases.sh").read())
    subprocess.run(ssh_tunnel + bash_aliases, shell=True)

    # setup bash functions
    bash_functions = """ "{}" """.format(open("../../compute/setup/bash/setup_bash_functions.sh").read())
    subprocess.run(ssh_tunnel + bash_functions, shell=True)

    # setup git configuration
    bash_git = """ "{}" """.format(open("../../compute/setup/git/setup_git_config.sh").read())
    subprocess.run(ssh_tunnel + bash_git, shell=True)

    # setup bash profile
    bash_profile = """ "{}" """.format(open("../../compute/setup/bash/setup_bash_profile.sh").read())
    subprocess.run(ssh_tunnel + bash_profile, shell=True)

    # source the .bashrc
    bash_main = """ "{}" """.format(open("../../compute/setup/bash/setup_bash.sh").read())
    subprocess.run(ssh_tunnel + bash_main, shell=True)

def go_setup_python(self, ssh_tunnel, scp_tunnel=None, install_from_requirements=False):
    """
    Documentation:

        ---
        Description:
            Run series of commands to setup Python enviroment. Optionally, pip install a custom
            list of libraries listed in a requirement.txt file.

        ---
        Parameters:
            ssh_tunnel : str
                String for using SSH to remotely execute script on EC2 instance.
            scp_tunnel : str, default=None
                String for using SCP to securely copy local files to EC2 instance.
            install_from_requirements : boolean, default=False
                Controls whether to install additional Python packages from
                local requirement.txt file.
    """
    # set bash environment attributes to support Python
    bash_python = """ "{}" """.format(open("../../compute/setup/python/setup_bash_python.sh").read())
    subprocess.run(ssh_tunnel + bash_python, shell=True)


    # install pip into Python3.7 environment
    pip_install = """ "python3.7 -m pip install pip" """
    subprocess.run(ssh_tunnel + pip_install, shell=True)

    # optionally install libraries from requirements file
    if install_from_requirements:
        # retrieve instance_username
        instance_username = self.get_instance_username()

        # scurely copy requirements.txt file into .python folder in EC2 instance
        python_hidden_folder = """-r ../../compute/setup/python/ {}@{}:~/.python/""".format(
                                                                        instance_username,
                                                                        self.instance.public_dns_name,
                                                                    )
        subprocess.run(scp_tunnel + python_hidden_folder, shell=True)

        # pip install each library in the requirements.txt file one at a time
        req_install = """ "cat ~/.python/requirements.txt | xargs -n 1 python3.7 -m pip install" """
        subprocess.run(ssh_tunnel + req_install, shell=True)

        # # setup material theme in jupyter
        # req_install = """ "jt -t monokai -f fira -fs 13 -nf ptsans -nfs 11 -N -kl -cursw 5 -cursc r -cellw 95% -T" """
        # subprocess.run(ssh_tunnel + req_install, shell=True)

def go_setup_aws(self, scp_tunnel):
    """
    Documentation:

        ---
        Description:
            Setup configuration for AWSCLI

        ---
        Parameters:
            scp_tunnel : str
                String for using SCP to securely copy local files to EC2 instance.
    """
    # retrieve instance_username
    instance_username = self.get_instance_username()

    # securely copy .aws file stored locally into EC2 instance
    aws_cred = """-r ~/.aws {}@{}:~/""".format(
                                        instance_username,
                                        self.instance.public_dns_name,
                                    )
    subprocess.run(scp_tunnel + aws_cred, shell=True)

def get_user_data_status(self, ssh_tunnel):
    """
    Documentation:

        ---
        Description:
            Check to see if /tmp/testfile.txt exists. Used to indicate whether user data file
            successfuly ran during EC2 instance creation.

        ---
        Parameters:
            ssh_tunnel : str
                String for using SSH to remotely execute script on EC2 instance.
    """
    # command line script to test whether a file exists on EC2 instance. returns "yes" is True
    check_file = """ "(ls /tmp/testfile.txt >> /dev/null 2>&1 && echo yes) || echo no" """

    # store result of command line script
    result = subprocess.Popen(
                    ssh_tunnel + check_file,
                    stdout=subprocess.PIPE,
                    stderr=None,
                    shell=True
                )

    # parse reults
    result = result.communicate()
    result = result[0].decode("utf-8").replace("\n","")

    # set status variable based on results
    status = False
    if result == "yes":
        status = True
    return status