# Wimpy Environment [![Build Status](https://travis-ci.org/wimpy/wimpy.environment.svg?branch=master)](https://travis-ci.org/wimpy/wimpy.environment)
Ansible role that creates resources in your AWS account so you can deploy applications using Wimpy.

## Parameters
The parameters are
  - `wimpy_deployment_environment`: Environment where you want to create the application resources.
  - `wimpy_environments_list`: List of different environments to create. If you overwrite this parameter, read the documentation carefully. By default `staging` and `production`.
  - `wimpy_application_name`: The name to identify your project.
  - `wimpy_application_port`: Port where your application is listening for requests.
  - `wimpy_application_protocol`: Protocol (tcp|udp|icmp) where your application is listening for requests. Defaults to `tcp`.
  - `boto_profile`: Boto profile to use. By default no profile is used.
  - `wimpy_aws_region`: AWS Region where to create the repository. By default `eu-west-1`.

## Usage

```yaml
- hosts: localhost
  connection: local
  roles:
    - wimpy.environment

```

This will create three different types of CloudFormation stacks

### Base Stack
It creates a base CloudFormation stack that contains
- KMS Master key
- S3 bucket for applications
- S3 bucket for CloudTrail audit log, ELB access log and S3 access log

### Environment Stack
Wimpy applications will be deployed to different environments, typically staging and production.
This role creates a CloudFormation stack for every environment that contains
- Virtual Private Cloud (VPC) for your applications
- Route tables for this VPC
- Internet gateway
- Public subnets for your Load Balancers
- Private subnets for your applications
- Private subnets for your databases

#### Defining your own set of environments
This role creates different VPC's for different environments, assinging a different IP range to each VPC.
Using the default environment list that contains `staging` and `production` , these ranges would be `10.0.0.0/16`, and `10.1.0.0/16` respectively. Adding a third environment would make a new VPC with the range `10.2.0.0/16`. And so on.
Keep in mind that the order matters. Keep the list of environments always in the same order, and if you want a new environment, add it to the list. Treat the list of environments as append only.

### Application Stack
For every application that you deploy, this role will create the following resources
- A repository in Elastic Container Registry to store Docker images.
- Security Group for your application that allows traffic to the application port from Load Balancers and from instances with the same security group.
- Security Group for your Load Balancers that allows public traffic.
- Security Group for your databases that allows traffic from your applications.
- IAM Role for the application so it can access to S3, KMS and CloudWatch.
