# Wimpy Build [![Build Status](https://travis-ci.org/wimpy/wimpy.environment.svg?branch=master)](https://travis-ci.org/wimpy/wimpy.environment)
Ansible role that creates resources in your AWS account so you can deploy applications using Wimpy.

## Base
It creates a `base` CloudFormation that contains
- KMS Master key
- S3 bucket for applications
- S3 bucket for CloudTrail audit log, ELB access log and S3 access log

## Environments
It creates one stack for every environment, typically stating and production. This stack contains
- VPC
- Route tables for this VPC
- Internet gateway
- Public subnets for your Load Balancers
- Private subnets for your applications
- Private subnets for your databases

## Applications
For every application that you deploy, this role will create the following resources
- Security Group for your application that allows traffic to the application port from Load Balancers
- Security Group for your Load Balancers that allows public traffic
- Security Group for your databases that allows traffic from your applications
- IAM Role for the application so it can access to S3, KMS and CloudWatch

## Parameters
The parameters are

  - `wimpy_project_name`: The name to identify your project.
  - `wimpy_app_port`: Port where your application is listening for requests
  - `wimpy_deployment_environment`: Environment where you want to create the application resources
  - `wimpy_environments_list`: List of different environments to create. By default staging and production.
  - `boto_profile`: Boto profile to use. Default none is used.
  - `wimpy_aws_region`: AWS Region where to create the repository. By default eu-west-1.
  - `wimpy_aws_vpc_id`

## Usage

```yaml
- hosts: localhost
  connection: local
  roles:
    - wimpy.environment

```

