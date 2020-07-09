#!/bin/bash
cd ../script

python ec2_launch_instance.py \
                --instance_name=$1 \
                --key_name=tdpawskey \
                --ami_name=ubuntu_1804_basic \
                --instance_type=t2.large \
                --volume_name=tdp-data-store-ebs-$1 \
                --volume_size=2 \
                --user_data=wakeup_ubuntu.sh \
                --shutdown_behavior=stop \
                --access_instance \
                --buckets_to_sync=tdp-data-store