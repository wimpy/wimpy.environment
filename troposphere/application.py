from troposphere import Join, Parameter, Output
from troposphere import Ref, Tags, Template
from troposphere.ec2 import SecurityGroup, SecurityGroupIngress
from troposphere.ecr import Repository
from troposphere.iam import InstanceProfile
from troposphere.iam import PolicyType
from troposphere.iam import Role

t = Template()

t.add_version("2010-09-09")
t.add_description("Stack that creates resources needed for a specific application")

vpcId = t.add_parameter(Parameter(
    "VPC",
    Type="String",
    Description="VPC ID",
))
environment = t.add_parameter(Parameter(
    "Environment",
    Type="String",
    Description="Environment where this is deployed",
))
appName = t.add_parameter(Parameter(
    "AppName",
    Type="String",
    Description="Name of the application",
))
appPort = t.add_parameter(Parameter(
    "AppPort",
    Type="String",
    Description="Port where the application will be listening",
))
appProtocol = t.add_parameter(Parameter(
    "AppProtocol",
    Type="String",
    Description="Protocol used by the application",
))
exposedPort = t.add_parameter(Parameter(
    "ExposedPort",
    Type="String",
    Description="Port where the load balancer will be listening",
))
MasterKey = t.add_parameter(Parameter(
    "MasterKey",
    Type="String",
    Description="KMS key used",
))
StorageBucketName = t.add_parameter(Parameter(
    "StorageBucketName",
    Type="String",
    Description="S3 Bucket for application data storage",
))


LoadBalancerSecurityGroup = t.add_resource(SecurityGroup(
    "LoadBalancerSecurityGroup",
    SecurityGroupIngress=[
        {
            "ToPort": Ref(exposedPort),
            "FromPort": Ref(exposedPort),
            "IpProtocol": "tcp",
            "CidrIp": "0.0.0.0/0"
        }
    ],
    VpcId=Ref(vpcId),
    GroupDescription=Join("-", [Ref(environment), Ref(appName), "elb"]),
    Tags=Tags(
        Name=Join("-", [Ref(environment), Ref(appName), "elb"]),
    ),
))

InstanceSecurityGroup = t.add_resource(SecurityGroup(
    "InstanceSecurityGroup",
    VpcId=Ref(vpcId),
    GroupDescription=Join("-", [Ref(environment), Ref(appName), "instances"]),
    Tags=Tags(
        Name=Join("-", [Ref(environment), Ref(appName), "instances"]),
    ),
))

IngressForELB = t.add_resource(SecurityGroupIngress(
    "IngressForELB",
    IpProtocol=Ref(appProtocol),
    FromPort=Ref(appPort),
    ToPort=Ref(appPort),
    SourceSecurityGroupId=Ref("LoadBalancerSecurityGroup"),
    GroupId=Ref("InstanceSecurityGroup")
))
IngressForInstances = t.add_resource(SecurityGroupIngress(
    "IngressForInstances",
    IpProtocol=Ref(appProtocol),
    FromPort=Ref(appPort),
    ToPort=Ref(appPort),
    SourceSecurityGroupId=Ref("InstanceSecurityGroup"),
    GroupId=Ref("InstanceSecurityGroup")
))
IngressForSSH = t.add_resource(SecurityGroupIngress(
    "IngressForSSH",
    IpProtocol="tcp",
    FromPort=22,
    ToPort=22,
    CidrIp="0.0.0.0/0",
    GroupId=Ref("InstanceSecurityGroup")
))

DBSecurityGroup = t.add_resource(SecurityGroup(
    "DBSecurityGroup",
    SecurityGroupIngress=[
        {
            "SourceSecurityGroupId": Ref("InstanceSecurityGroup"),
            "FromPort": 0,
            "ToPort": 65535,
            "IpProtocol": "tcp"
        }
    ],
    VpcId=Ref(vpcId),
    GroupDescription=Join("-", [Ref(environment), Ref(appName), "db"]),
    Tags=Tags(
        Name=Join("-", [Ref(environment), Ref(appName), "db"]),
    ),
))

# Profile for application instances
IAMInstanceProfile = t.add_resource(InstanceProfile(
    "IAMInstanceProfile",
    Path=Join("", ["/", Ref(environment), "/", Ref(appName), "/"]),
    Roles=[Ref("IAMRole")],
))

# Role for application instances
IAMRole = t.add_resource(Role(
    "IAMRole",
    Path=Join("", ["/", Ref(environment), "/", Ref(appName), "/"]),
    ManagedPolicyArns=[
        "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM",
        "arn:aws:iam::aws:policy/AWSXrayFullAccess"
    ],
    AssumeRolePolicyDocument={
        "Statement": [
            {
                "Action": ["sts:AssumeRole"],
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"}
            }
        ]
    },
))

# Policy for instances so they can access the KMS key, the CloudWatch LogGroup and the S3 bucket
IAMPolicy = t.add_resource(PolicyType(
    "IAMPolicy",
    PolicyName=Join("-", [Ref("AWS::StackName"), "policy"]),
    Roles=[Ref(IAMRole)],
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["s3:*"],
            "Resource": Join("", ["arn:aws:s3:::", Ref(StorageBucketName), "/", Ref(environment), "/", Ref(appName), "/"]),
            "Effect": "Allow",
            "Sid": "allowScopedS3AccessRoot"
        }, {
            "Action": ["s3:*"],
            "Resource": Join("", ["arn:aws:s3:::", Ref(StorageBucketName), "/", Ref(environment), "/", Ref(appName), "/*"]),
            "Effect": "Allow",
            "Sid": "allowScopedS3Access"
        }, {
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": Join("/", [Join(":", ["arn:aws:kms", Ref("AWS::Region"), Ref("AWS::AccountId"), "key"]), Ref("MasterKey")]),
            "Effect": "Allow",
            "Sid": "allowKMSUse"
        }, {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Resource": Join(":", ["arn:aws:logs", Ref("AWS::Region"), Ref("AWS::AccountId"), "log-group", Join("", ["/", Ref(environment), "/", Ref(appName), "/*"]), "log-stream", "*"]),
            "Effect": "Allow",
            "Sid": "allowScopedLogAccess"
        }]
    },
))

ECRRepository = t.add_resource(Repository(
    "ECRRepository",
    RepositoryName=Ref(appName)
))

t.add_output(Output(
    "LoadBalancerSecurityGroup",
    Value=Ref("LoadBalancerSecurityGroup"),
    Description="Security group for load balancers")
)
t.add_output(Output(
    "InstanceSecurityGroup",
    Value=Ref("InstanceSecurityGroup"),
    Description="Security group for application instances")
)
t.add_output(Output(
    "DBSecurityGroup",
    Value=Ref("DBSecurityGroup"),
    Description="Security group for databases")
)
t.add_output(Output(
    "IAMRole",
    Value=Ref("IAMRole"),
    Description="Role that allows access to ssm and xray")
)
t.add_output(Output(
    "IAMInstanceProfile",
    Value=Ref("IAMInstanceProfile"),
    Description="Instance profile for application instances")
)
t.add_output(Output(
    "Registry",
    Value=Join(".", [Ref("AWS::AccountId"), "dkr.ecr", Ref("AWS::Region"), "amazonaws.com", ]),
    Description="Hostname of the registry")
)
t.add_output(Output(
    "Repository",
    Value=Join("/", [Join(".", [Ref("AWS::AccountId"), "dkr.ecr", Ref("AWS::Region"), "amazonaws.com", ]), Ref("ECRRepository")]),
    Description="Full name of the ECR Repository")
)

print(t.to_json())
