import sys
from troposphere import Join, Output
from troposphere import Ref, Tags, Template
from troposphere.ec2 import InternetGateway
from troposphere.ec2 import Route
from troposphere.ec2 import RouteTable
from troposphere.ec2 import Subnet
from troposphere.ec2 import SubnetRouteTableAssociation
from troposphere.ec2 import VPC
from troposphere.ec2 import VPCGatewayAttachment
from troposphere.elasticache import SubnetGroup
from troposphere.rds import DBSubnetGroup

environment_index = int(sys.argv[1])

t = Template()

t.add_version("2010-09-09")
t.add_description("Stack that creates resources for a specific environment")

ELBRouteTable1 = t.add_resource(RouteTable(
    "ELBRouteTable1",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "elb", "eu-west-1a"]),
    ),
))

ELBRouteTable2 = t.add_resource(RouteTable(
    "ELBRouteTable2",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "elb", "eu-west-1b"]),
    ),
))

ELBRouteTable3 = t.add_resource(RouteTable(
    "ELBRouteTable3",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "elb", "eu-west-1c"]),
    ),
))

ELBRouteTableAssociation1 = t.add_resource(SubnetRouteTableAssociation(
    "ELBRouteTableAssociation1",
    SubnetId=Ref("ELBSubnet1"),
    RouteTableId=Ref("ELBRouteTable1"),
))

ELBRouteTableAssociation2 = t.add_resource(SubnetRouteTableAssociation(
    "ELBRouteTableAssociation2",
    SubnetId=Ref("ELBSubnet2"),
    RouteTableId=Ref("ELBRouteTable2"),
))

ELBRouteTableAssociation3 = t.add_resource(SubnetRouteTableAssociation(
    "ELBRouteTableAssociation3",
    SubnetId=Ref("ELBSubnet3"),
    RouteTableId=Ref("ELBRouteTable3"),
))

ELBSubnet1 = t.add_resource(Subnet(
    "ELBSubnet1",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1a",
    CidrBlock="10." + str(environment_index) + ".32.0/20",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "elb", "eu-west-1a"]),
    ),
))

ELBSubnet2 = t.add_resource(Subnet(
    "ELBSubnet2",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1b",
    CidrBlock="10." + str(environment_index) + ".96.0/20",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "elb", "eu-west-1b"]),
    ),
))

ELBSubnet3 = t.add_resource(Subnet(
    "ELBSubnet3",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1c",
    CidrBlock="10." + str(environment_index) + ".160.0/20",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "elb", "eu-west-1c"]),
    ),
))

ELBRoute1 = t.add_resource(Route(
    "ELBRoute1",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("ELBRouteTable1"),
    DependsOn=["InternetGatewayAttachment"],
))

ELBRoute2 = t.add_resource(Route(
    "ELBRoute2",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("ELBRouteTable2"),
    DependsOn=["InternetGatewayAttachment"],
))

ELBRoute3 = t.add_resource(Route(
    "ELBRoute3",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("ELBRouteTable3"),
    DependsOn=["InternetGatewayAttachment"],
))

AppSubnet1 = t.add_resource(Subnet(
    "AppSubnet1",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1a",
    CidrBlock="10." + str(environment_index) + ".0.0/19",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "app", "eu-west-1a"]),
    ),
))

AppSubnet2 = t.add_resource(Subnet(
    "AppSubnet2",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1b",
    CidrBlock="10." + str(environment_index) + ".64.0/19",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "app", "eu-west-1b"]),
    ),
))

AppSubnet3 = t.add_resource(Subnet(
    "AppSubnet3",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1c",
    CidrBlock="10." + str(environment_index) + ".128.0/19",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "app", "eu-west-1c"]),
    ),
))

AppRouteTableAssociation1 = t.add_resource(SubnetRouteTableAssociation(
    "AppRouteTableAssociation1",
    SubnetId=Ref("AppSubnet1"),
    RouteTableId=Ref("AppRouteTable1"),
))

AppRouteTableAssociation2 = t.add_resource(SubnetRouteTableAssociation(
    "AppRouteTableAssociation2",
    SubnetId=Ref("AppSubnet2"),
    RouteTableId=Ref("AppRouteTable2"),
))

AppRouteTableAssociation3 = t.add_resource(SubnetRouteTableAssociation(
    "AppRouteTableAssociation3",
    SubnetId=Ref("AppSubnet3"),
    RouteTableId=Ref("AppRouteTable3"),
))

AppRouteTable1 = t.add_resource(RouteTable(
    "AppRouteTable1",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "app", "eu-west-1a"]),
    ),
))

AppRouteTable2 = t.add_resource(RouteTable(
    "AppRouteTable2",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "app", "eu-west-1b"]),
    ),
))

AppRouteTable3 = t.add_resource(RouteTable(
    "AppRouteTable3",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "app", "eu-west-1c"]),
    ),
))

AppRoute1 = t.add_resource(Route(
    "AppRoute1",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("AppRouteTable1"),
    DependsOn=["InternetGatewayAttachment"],
))

AppRoute2 = t.add_resource(Route(
    "AppRoute2",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("AppRouteTable2"),
    DependsOn=["InternetGatewayAttachment"],
))

AppRoute3 = t.add_resource(Route(
    "AppRoute3",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("AppRouteTable3"),
    DependsOn=["InternetGatewayAttachment"],
))

DBSubnet1 = t.add_resource(Subnet(
    "DBSubnet1",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1a",
    CidrBlock="10." + str(environment_index) + ".48.0/20",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "db", "eu-west-1a"]),
    ),
))

DBSubnet2 = t.add_resource(Subnet(
    "DBSubnet2",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1b",
    CidrBlock="10." + str(environment_index) + ".112.0/20",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "db", "eu-west-1b"]),
    ),
))

DBSubnet3 = t.add_resource(Subnet(
    "DBSubnet3",
    VpcId=Ref("VPC"),
    AvailabilityZone="eu-west-1c",
    CidrBlock="10." + str(environment_index) + ".176.0/20",
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "db", "eu-west-1c"]),
    ),
))

DBRouteTable1 = t.add_resource(RouteTable(
    "DBRouteTable1",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "db", "eu-west-1a"]),
    ),
))

DBRouteTable2 = t.add_resource(RouteTable(
    "DBRouteTable2",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "db", "eu-west-1b"]),
    ),
))

DBRouteTable3 = t.add_resource(RouteTable(
    "DBRouteTable3",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join("-", [Ref("AWS::StackName"), "db", "eu-west-1c"]),
    ),
))

DBRouteTableAssociation1 = t.add_resource(SubnetRouteTableAssociation(
    "DBRouteTableAssociation1",
    SubnetId=Ref("DBSubnet1"),
    RouteTableId=Ref("DBRouteTable1"),
))

DBRouteTableAssociation2 = t.add_resource(SubnetRouteTableAssociation(
    "DBRouteTableAssociation2",
    SubnetId=Ref("DBSubnet2"),
    RouteTableId=Ref("DBRouteTable2"),
))

DBRouteTableAssociation3 = t.add_resource(SubnetRouteTableAssociation(
    "DBRouteTableAssociation3",
    SubnetId=Ref("DBSubnet3"),
    RouteTableId=Ref("DBRouteTable3"),
))

ElastiCacheSubnetGroup = t.add_resource(SubnetGroup(
    "ElastiCacheSubnetGroup",
    SubnetIds=[Ref("DBSubnet1"), Ref("DBSubnet2"), Ref("DBSubnet3")],
    Description=Ref("AWS::StackName"),
))

RDSSubnetGroup = t.add_resource(DBSubnetGroup(
    "RDSSubnetGroup",
    SubnetIds=[Ref("DBSubnet1"), Ref("DBSubnet2"), Ref("DBSubnet3")],
    DBSubnetGroupDescription=Ref("AWS::StackName"),
))

VPC = t.add_resource(VPC(
    "VPC",
    InstanceTenancy="default",
    EnableDnsSupport=True,
    CidrBlock="10." + str(environment_index) + ".0.0/16",
    EnableDnsHostnames=True,
    Tags=Tags(
        Name=Ref("AWS::StackName"),
    ),
))

InternetGatewayAttachment = t.add_resource(VPCGatewayAttachment(
    "InternetGatewayAttachment",
    VpcId=Ref("VPC"),
    InternetGatewayId=Ref("InternetGateway"),
))

InternetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(
        Name=Ref("AWS::StackName"),
    ),
))

t.add_output(Output("VPC", Value=Ref("VPC"), Description="VPC ID"))
t.add_output(
    Output("ELBSubnets", Value=Join(", ", [Ref("ELBSubnet1"), Ref("ELBSubnet2"), Ref("ELBSubnet3")]),
           Description="ELB Subnets"))
t.add_output(
    Output("AppSubnets", Value=Join(", ", [Ref("AppSubnet1"), Ref("AppSubnet2"), Ref("AppSubnet3")]),
           Description="Application subnets"))
t.add_output(
    Output("DBSubnets", Value=Join(", ", [Ref("DBSubnet1"), Ref("DBSubnet2"), Ref("DBSubnet3")]),
           Description="DB Subnets"))
t.add_output(
    Output("InternetGateway", Value=Ref("InternetGateway"),
           Description="Internet Gateway id"))


print(t.to_json())
