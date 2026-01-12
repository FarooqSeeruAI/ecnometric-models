#!/bin/bash
# Quick SSH script for EC2 instance

SSH_KEY="pem/ecnometric_model.pem"
EC2_USER="ubuntu"
EC2_IP="13.203.193.142"

# SSH into the EC2 instance
ssh -i ${SSH_KEY} ${EC2_USER}@${EC2_IP} "$@"
