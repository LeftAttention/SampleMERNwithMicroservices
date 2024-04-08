import boto3
import os
from dotenv import load_dotenv
import base64

load_dotenv()

region = os.getenv('AWS_REGION')
frontend_ecr = os.getenv('FRONTEND_ECR')
vpc_cidr_block = os.getenv('VPC_CIDR_BLOCK')
subnet_cidr_blocks = os.getenv('SUBNET_CIDR_BLOCKS').split(',')
security_group = os.getenv('SECURITY_GROUP')
asg_name = os.getenv('ASG_NAME')
instance_type = os.getenv('INSTANCE_TYPE')
launch_template = os.getenv('LAUNCH_TEMPLATE')
lambda_function = os.getenv('LAMBDA_FUNCTION')
lambda_arn = os.getenv('LAMBDA_ARN')
ami_id = os.getenv('AMI_ID')
key_name = os.getenv('KEY_NAME')
vpc_id = os.getenv('VPC_ID')
subnet_ids = os.getenv('SUBNET_IDS')

ec2 = boto3.resource('ec2', region_name=region)
autoscaling = boto3.client('autoscaling', region_name=region)
lambda_client = boto3.client('lambda', region_name=region)
elb = boto3.client('elbv2', region_name=region)

vpc = ec2.create_vpc(CidrBlock=vpc_cidr_block)
vpc.wait_until_available()

subnets = []
for cidr_block in subnet_cidr_blocks:
    subnet = vpc.create_subnet(CidrBlock=cidr_block)
    subnets.append(subnet)

sg = ec2.create_security_group(
    GroupName=security_group,
    Description='Security group for backend ASG',
    VpcId=vpc.id
)

sg.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=80,
    ToPort=80
)


# Create the Launch template

def read_script(file_path):
    with open(file_path, 'r') as file:
        script = file.read()
    return script

user_data = read_script("userdata.sh")

launch_template = ec2.create_launch_template(
    LaunchTemplateName=launch_template,
    VersionDescription='v1',
    LaunchTemplateData={
        'ImageId': ami_id,  
        'InstanceType': instance_type,
        'KeyName': key_name,
        'SecurityGroupIds': security_group,
        'UserData': user_data.encode('base64'),
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'BackendInstance'}]
            }
        ]
    }
)


autoscaling.create_auto_scaling_group(
    AutoScalingGroupName=asg_name,
    InstanceType=instance_type,
    MinSize=1,
    MaxSize=3,
    LaunchTemplate={
        'LaunchTemplateName': launch_template,
    },
    VPCZoneIdentifier=','.join([subnet.id for subnet in subnets])
)

with open('iac_lambda_function.zip', 'rb') as f:
    zipped_code = f.read()

lambda_client.create_function(
    FunctionName=lambda_function,
    Runtime='python3.8',
    Role=lambda_arn,
    Handler='lambda_function.lambda_handler',
    Code={'ZipFile': zipped_code},
)



sg = ec2.create_security_group(
    GroupName='ALBSecurityGroup',
    Description='Security group for ALB',
    VpcId=vpc_id
)
security_group_id = sg['GroupId']

ec2.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {'IpProtocol': 'tcp',
         'FromPort': 80,
         'ToPort': 80,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ]
)

response = elb.create_load_balancer(
    Name='MyBackendALB',
    Subnets=subnet_ids,
    SecurityGroups=[security_group_id],
    Scheme='internet-facing',
    Type='application',
    IpAddressType='ipv4'
)

load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']

# Create a target group
target_group = elb.create_target_group(
    Name='MyBackendTargetGroup',
    Protocol='HTTP',
    Port=80,
    VpcId=vpc_id,
    HealthCheckProtocol='HTTP',
    HealthCheckPath='/health',
    HealthCheckPort='80',
    TargetType='instance'
)

target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']

elb.create_listener(
    LoadBalancerArn=load_balancer_arn,
    Protocol='HTTP',
    Port=80,
    DefaultActions=[{
        'Type': 'forward',
        'TargetGroupArn': target_group_arn
    }]
)

frontend_user_data = f"""#!/bin/bash
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo docker pull {frontend_ecr}
sudo docker run -d -p 80:80 {frontend_ecr}
"""

frontend_instance = ec2.create_instances(
    ImageId=ami_id,
    MinCount=1,
    MaxCount=1,
    InstanceType=instance_type,
    KeyName=key_name,
    SecurityGroupIds=[security_group_id],
    SubnetId=subnet_ids,
    UserData=base64.b64encode(user_data.encode()).decode('utf-8'),
    TagSpecifications=[{
        'ResourceType': 'instance',
        'Tags': [{'Key': 'Name', 'Value': 'FrontendInstance'}]
    }]
)

sns = boto3.client('sns')
deployment_success_topic = sns.create_topic(Name='deployment-success')
deployment_failure_topic = sns.create_topic(Name='deployment-failure')


success_arn = os.getenv('SNS_SUCCESS_ARN')
failure_arn = os.getenv('SNS_FAILURE_ARN')

def lambda_handler(event, context):
    sns = boto3.client('sns')
    message = event.get('message')
    status = event.get('status')

    topic_arn = 'arn:aws:sns:region:account-id:deployment-success' if status == 'success' else 'arn:aws:sns:region:account-id:deployment-failure'

    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject='Deployment Notification'
    )

    return response

ses = boto3.client('ses')

def send_email(subject, message, recipient):
    response = ses.send_email(
        Source='kaibalya.bhuyan@leftattention.com',
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': message}}
        }
    )
    return response