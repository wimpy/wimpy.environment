from troposphere import Join, GetAtt, Output
from troposphere import Ref, Tags, Template
from troposphere.cloudtrail import Trail
from troposphere.iam import Role, Policy
from troposphere.kms import Key
from troposphere.s3 import Bucket, BucketPolicy, LoggingConfiguration, CorsConfiguration, CorsRules
from troposphere.logs import LogGroup

t = Template()

t.add_version("2010-09-09")
t.add_description("Stack that creates resources shared for all applications inside your AWS account")

# https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-access-logs.html
t.add_mapping("Principals", {
    "ap-northeast-1": {"ELB": "582318560864"},
    "ap-northeast-2": {"ELB": "600734575887"},
    "ap-southeast-1": {"ELB": "114774131450"},
    "ap-southeast-2": {"ELB": "783225319266"},
    "ap-south-1": {"ELB": "718504428378"},
    "ca-central-1": {"ELB": "985666609251"},
    "eu-west-1": {"ELB": "156460612806"},
    "eu-west-2": {"ELB": "652711504416"},
    "eu-central-1": {"ELB": "054676820928"},
    "sa-east-1": {"ELB": "507241528517"},
    "us-west-1": {"ELB": "027434742980"},
    "us-west-2": {"ELB": "797873946194"},
    "us-east-1": {"ELB": "127311923021"},
    "us-east-2": {"ELB": "033677994240"}
})

# Bucket for ELB access logs, S3 access logs and CloudTrail audit log
LogBucket = t.add_resource(Bucket(
    "LogBucket",
    BucketName="LogBucket",
    # Allows S3 to write S3 access logs
    AccessControl="LogDeliveryWrite",
    Tags=Tags(
        Name=Join(" ", [Ref("AWS::StackName"), "Logs"]),
        Managed="Wimpy",
    ),
))

# Bucket for the application to store images/files/whatever
# S3 Access Log https://docs.aws.amazon.com/AmazonS3/latest/dev/ServerLogs.html
StorageBucket = t.add_resource(Bucket(
    "StorageBucket",
    BucketName="StorageBucket",
    # Enable access log for this bucket
    LoggingConfiguration=LoggingConfiguration(
        # The name of an S3 bucket where AWS stores the access log for this bucket
        DestinationBucketName=Ref("LogBucket"),
        # A prefix for the all log object keys
        LogFilePrefix="S3AccessLogs/"
    ),
    Tags=Tags(
        Name=Join(" ", [Ref("AWS::StackName"), "Storage"]),
        Managed="Wimpy",
    ),
))

# Policy for LogBucket so CloudTrail and ELB can write logs in it
LogPolicy = t.add_resource(BucketPolicy(
    "LogPolicy",
    Bucket=Ref("LogBucket"),
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [
            {
                # https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html
                "Sid": "AWSCloudTrailAclCheck",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:GetBucketAcl",
                "Resource": {
                    "Fn::Join": ["", ["arn:aws:s3:::", Ref("LogBucket")]]
                }
            },
            {
                # CloudTrail automatically writes to the bucket_name/AWSLogs/account_ID/ folder,
                # so the bucket policy grants write privileges for that prefix
                # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html#w1ab2c19c12d143c15
                "Sid": "AWSCloudTrailWrite",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:PutObject",
                "Resource": {
                    "Fn::Join": ["", ["arn:aws:s3:::", Ref("LogBucket"), "/AWSLogs/", Ref("AWS::AccountId"), "/*"]]
                },
                "Condition": {
                    "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                }
            },
            {
                # https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-access-logs.html
                "Sid": "AWSELBLogWrite",
                "Effect": "Allow",
                "Action": "s3:PutObject",
                "Resource": {
                    "Fn::Join": ["", ["arn:aws:s3:::", Ref("LogBucket"), "/ELBLogs/*"]]
                },
                "Principal": {
                    "AWS": [{"Fn::FindInMap": ["Principals", Ref("AWS::Region"), "ELB"]}]
                }
            }
        ]
    }
))

# Role that Amazon CloudWatch Logs assumes to write logs to a log group
# https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-required-policy-for-cloudwatch-logs.html
IAMRole = t.add_resource(Role(
    "CloudTrailLoggingRole",
    Path="/cloudtrail/",
    Policies=[Policy(
        PolicyName="CloudTrailLogging",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "AWSCloudTrailCreateLogStream2014110",
                "Effect": "Allow",
                "Action": ["logs:CreateLogStream"],
                "Resource": [{
                    "Fn::GetAtt": ["CloudTrailLogs", "Arn"]
                }]
            }, {
                "Sid": "AWSCloudTrailPutLogEvents20141101",
                "Effect": "Allow",
                "Action": ["logs:PutLogEvents"],
                "Resource": [{
                    "Fn::GetAtt": ["CloudTrailLogs", "Arn"]
                }]
            }]
        })
    ],
    AssumeRolePolicyDocument={
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": "cloudtrail.amazonaws.com"}
        }]
    },
))

# CloudWatch Log Group where CloudTrail will log
CloudTrailLogs = t.add_resource(LogGroup(
    "CloudTrailLogs"
))

CloudTrail = t.add_resource(Trail(
    "CloudTrail",
    DependsOn=["LogPolicy"],
    # ARN of a log group to which CloudTrail logs will be delivered
    CloudWatchLogsLogGroupArn=GetAtt("CloudTrailLogs", "Arn"),
    # Role that Amazon CloudWatch Logs assumes to write logs to a log group
    CloudWatchLogsRoleArn=GetAtt("CloudTrailLoggingRole", "Arn"),
    # Indicates whether CloudTrail validates the integrity of log files
    EnableLogFileValidation=True,
    # Whether the trail is publishing events from global services, such as IAM, to the log files
    IncludeGlobalServiceEvents=True,
    # Indicates whether the CloudTrail trail is currently logging AWS API calls
    IsLogging=True,
    # Whether the trail is created in the region in which you create the stack or in all regions
    IsMultiRegionTrail=True,
    # The AWS KMS key ID that you want to use to encrypt CloudTrail logs
    KMSKeyId=Ref("MasterKey"),
    # The name of the Amazon S3 bucket where CloudTrail publishes log files
    S3BucketName=Ref("LogBucket"),
    # An Amazon S3 object key prefix that precedes the name of all log files
    # S3KeyPrefix="",
    # The name of an Amazon SNS topic that is notified when new log files are published
    # SnsTopicName=GetAtt(Topic, "TopicName"),
))

# The AWS KMS key used to encrypt CloudTrail logs
# https://docs.aws.amazon.com/awscloudtrail/latest/userguide/default-cmk-policy.html
MasterKey = t.add_resource(Key(
    "MasterKey",
    Description="Master Key for this Account",
    Enabled=True,
    EnableKeyRotation=True,
    KeyPolicy={
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": {
                    "Fn::Join": [":", ["arn:aws:iam:", Ref("AWS::AccountId"), "root"]]
                }
            },
            "Action": "kms:*",
            "Resource": "*"
        }, {
            # https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-kms-key-policy-for-cloudtrail-encrypt.html
            "Sid": "Allow CloudTrail to encrypt logs",
            "Effect": "Allow",
            "Principal": {
                "Service": ["cloudtrail.amazonaws.com"]
            },
            "Action": "kms:GenerateDataKey*",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "kms:EncryptionContext:aws:cloudtrail:arn": {
                        "Fn::Join": ["", ["arn:aws:cloudtrail:*:", Ref("AWS::AccountId"), ":trail/*"]]
                    }
                }
            }
        }, {
            "Sid": "Allow CloudTrail to describe key",
            "Effect": "Allow",
            "Principal": {
                "Service": ["cloudtrail.amazonaws.com"]
            },
            "Action": "kms:DescribeKey",
            "Resource": "*"
        }, {
            "Sid": "Allow principals in the account to decrypt log files",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": ["kms:Decrypt", "kms:ReEncryptFrom"],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "kms:CallerAccount": Ref("AWS::AccountId")
                },
                "StringLike": {
                    "kms:EncryptionContext:aws:cloudtrail:arn": {
                        "Fn::Join": ["", ["arn:aws:cloudtrail:*:", Ref("AWS::AccountId"), ":trail/*"]]
                    }
                }
            }
        }, {
            "Sid": "Allow alias creation during setup",
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "kms:CreateAlias",
            "Resource": "*",
            "Condition": {"StringEquals": {
                "kms:ViaService": {
                    "Fn::Join": [".", ["ec2", Ref("AWS::Region"), "amazonaws.com"]]
                },
                "kms:CallerAccount": Ref("AWS::AccountId")
            }}
        }, {
            "Sid": "Enable cross account log decryption",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": ["kms:Decrypt", "kms:ReEncryptFrom"],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "kms:CallerAccount": Ref("AWS::AccountId")
                },
                "StringLike": {
                    "kms:EncryptionContext:aws:cloudtrail:arn": {
                        "Fn::Join": ["", ["arn:aws:cloudtrail:*:", Ref("AWS::AccountId"), ":trail/*"]]
                    }
                }
            }
        }]
    }
))

t.add_output(Output(
    "LogBucket",
    Value=Ref("LogBucket"),
    Description="Bucket for logs CloudTrail and ELB logs")
)
t.add_output(Output(
    "StorageBucket",
    Value=Ref("StorageBucket"),
    Description="Bucket for applications to store data")
)
t.add_output(Output(
    "MasterKey",
    Value=Ref("MasterKey"),
    Description="KMS Key to encrypt CloudTrail logs")
)


print(t.to_json())
