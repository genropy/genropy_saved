from __future__ import print_function
from builtins import map
#from builtins import object
import boto3
import json
import inspect
import botocore
import sys


InstanceTypes=['t1.micro','t2.nano','t2.micro','t2.small','t2.medium',
 't2.large','t2.xlarge','t2.2xlarge','t3.nano','t3.micro','t3.small',
 't3.medium','t3.large','t3.xlarge','t3.2xlarge','m1.small','m1.medium',
 'm1.large','m1.xlarge','m3.medium','m3.large','m3.xlarge','m3.2xlarge',
 'm4.large','m4.xlarge','m4.2xlarge','m4.4xlarge','m4.10xlarge','m4.16xlarge',
 'm2.xlarge','m2.2xlarge','m2.4xlarge','cr1.8xlarge','r3.large','r3.xlarge',
 'r3.2xlarge','r3.4xlarge','r3.8xlarge','r4.large','r4.xlarge','r4.2xlarge',
 'r4.4xlarge','r4.8xlarge','r4.16xlarge','r5.large','r5.xlarge','r5.2xlarge',
 'r5.4xlarge','r5.8xlarge','r5.12xlarge','r5.16xlarge','r5.24xlarge',
 'r5.metal','r5d.large','r5d.xlarge','r5d.2xlarge','r5d.4xlarge','r5d.8xlarge',
 'r5d.12xlarge','r5d.16xlarge','r5d.24xlarge','r5d.metal','x1.16xlarge',
 'x1.32xlarge','x1e.xlarge','x1e.2xlarge','x1e.4xlarge','x1e.8xlarge',
 'x1e.16xlarge','x1e.32xlarge','i2.xlarge','i2.2xlarge','i2.4xlarge',
 'i2.8xlarge','i3.large','i3.xlarge','i3.2xlarge','i3.4xlarge','i3.8xlarge',
 'i3.16xlarge','i3.metal','hi1.4xlarge','hs1.8xlarge','c1.medium','c1.xlarge',
 'c3.large','c3.xlarge','c3.2xlarge','c3.4xlarge','c3.8xlarge','c4.large',
 'c4.xlarge','c4.2xlarge','c4.4xlarge','c4.8xlarge','c5.large','c5.xlarge',
 'c5.2xlarge','c5.4xlarge','c5.9xlarge','c5.18xlarge','c5d.large','c5d.xlarge',
 'c5d.2xlarge','c5d.4xlarge','c5d.9xlarge','c5d.18xlarge','cc1.4xlarge',
 'cc2.8xlarge','g2.2xlarge','g2.8xlarge','g3.4xlarge','g3.8xlarge','g3.16xlarge',
 'cg1.4xlarge','p2.xlarge','p2.8xlarge','p2.16xlarge','p3.2xlarge','p3.8xlarge',
 'p3.16xlarge','d2.xlarge','d2.2xlarge','d2.4xlarge','d2.8xlarge','f1.2xlarge',
 'f1.16xlarge','m5.large','m5.xlarge','m5.2xlarge','m5.4xlarge','m5.12xlarge',
 'm5.24xlarge','m5d.large','m5d.xlarge','m5d.2xlarge','m5d.4xlarge','m5d.12xlarge',
 'm5d.24xlarge','h1.2xlarge','h1.4xlarge','h1.8xlarge','h1.16xlarge','z1d.large',
 'z1d.xlarge','z1d.2xlarge','z1d.3xlarge','z1d.6xlarge','z1d.12xlarge']

UserDataTemplate ="""
#cloud-config
repo_update: true
repo_upgrade: all



runcmd:
- file_system_id_01=%(file_system_id)s
- efs_directory=/home/ubuntu/pod

- mkdir -p ${efs_directory}
- echo "${file_system_id_01}:/pods/%(pod_name)s ${efs_directory} efs tls,_netdev" >> /etc/fstab
- mount -a -t efs defaults
"""

class BaseAwsService(object):
    def __init__(self, aws_access_key_id=None,
        aws_secret_access_key=None, aws_session_token=None,
        region_name=None, parent=None):
        self.aws_access_key_id=aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key
        self.aws_session_token=aws_session_token
        self.region_name=None
        self.parent = parent
        self.services = dict()

    @property
    def client(self):
        return self.get_client(self.service_label)

    @property
    def resource(self):
        return self.get_resource(self.service_label)

    def service(self, service_label=None, region_name=None):
        region_name = region_name or self.region_name
        if self.parent:
            return self.parent.service(service_label=service_label, 
                region_name=region_name)
        if not (service_label, region_name) in self.services:
            service_class = service_classes.get(service_label)
            if service_class:
                service_instance = service_class(
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key= self.aws_secret_access_key,
                    aws_session_token= self.aws_session_token,
                    region_name=  region_name,
                    parent = self)
            else:
                service_instance = None
            self.services[(service_label, region_name)] = service_instance
        return self.services[(service_label, region_name)] 


    def regions(self, service_name=None, region_name=None):
        service_name = service_name or 'ec2'
        return self.session(region_name=region_name).get_available_regions(service_name)

    def get_client(self,service,region_name=None):
        return self.session(region_name=region_name).client(service)

    def get_resource(self, resource,region_name=None):
        return self.session(region_name=region_name).resource(resource)

    def session(self,region_name=None):
        return boto3.Session(aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key= self.aws_secret_access_key,
                            aws_session_token= self.aws_session_token,
                            region_name= region_name or self.region_name)

    def get_entity_dict(self, entity):
        pass

    @property
    def EC2(self):
        return self.service('ec2')

    @property
    def IAM(self):
        return self.service('iam')
    @property
    def S3(self):
        return self.service('s3')

    @property
    def Route53(self):
        return self.service('route53')
    
    @property
    def ELBV2(self):
        return self.service('elbv2')

    @property
    def SQS(self):
        return self.service('sqs')

class SQSManager(BaseAwsService):
    service_label = 'sqs'

    def create_queue(self, queue_name):
        sqs = self.resource
        sqs.create_queue(QueueName=queue_name, Attributes={'DelaySeconds': '5'})

    def queue_by_name(self, queue_name):
        try:
            return self.resource.get_queue_by_name(QueueName=queue_name)
        except botocore.exceptions.ClientError as e:
            if not e.response['Error']['Code']=='AWS.SimpleQueueService.NonExistentQueue':
                raise


    def queue_arn_by_name(self, queue_name):
        queue = self.queue_by_name(queue_name)
        if queue:
            return queue.attributes.get('QueueArn')
        
    def queue_url_by_name(self, queue_name):
        queue = self.queue_by_name(queue_name)
        if queue:
            return queue.url

    def get_sqs_policy(self, queue_name=None, full_access=None):
        queue_arn = self.queue_arn_by_name(queue_name)
        policy = { 'Version' : '2012-10-17'}
        if full_access:
            action = ["sqs:*"]
        else:
            action = [
                "sqs:DeleteMessage",
                "sqs:GetQueueUrl",
                "sqs:ListDeadLetterSourceQueues",
                "sqs:ReceiveMessage",
                "sqs:GetQueueAttributes",
                "sqs:ListQueueTags"
            ]
        policy['Statement'] = [{'Sid' : 'AwsQueueAllow%s'%queue_name, 
                'Effect': 'Allow', 'Action': action, 
                'Resource': queue_arn}]
        return json.dumps(policy, indent=2)

class EC2Manager(BaseAwsService):
    service_label = 'ec2'
    def tags_to_dict(self, tags=None):
        tags = tags or []
        return dict([(t['Key'].lower(),t['Value']) for t in tags])
        
    def instance_description_to_dict(self, instance):
        tags = self.tags_to_dict(instance.tags)
        return dict(
            instance_id = instance.instance_id,
            image_id = instance.image_id,
            instance_type = instance.instance_type,
            name = tags.get('name') or instance.instance_id,
            key_name = instance.key_name,
            private_dns_name = instance.private_dns_name,
            private_ip_address = instance.private_ip_address,
            public_dns_name = instance.public_dns_name,
            public_ip_address = instance.public_ip_address,
            vpc_id = instance.vpc_id,
            subnet_id = instance.subnet_id,
            tags = tags)
    

    def get_instances(self):
        ec2 = self.resource
        idd=self.instance_description_to_dict
        instances = list(map(idd,ec2.instances.all()))
        return dict([(i['name'],i) for i in instances])

    def get_key_pairs(self):
        ec2 = self.resource
        return dict([k.key_name, k.key_fingerprint] for k in ec2.key_pairs.all())

    def get_images(self, owners=None):
        ec2 = self.resource
        owners = owners or ['self']
        images = ec2.images.filter(Owners=owners)
        return dict([(i.name, i.image_id) for i in images])
    
    def get_vpcs(self, only_named=True):
        def vpc_dict(vpc):
            tags = self.tags_to_dict(vpc.tags)
            vpc_id = vpc.id
            name = tags.get('name') or vpc_id
            return dict(tags=tags, id=vpc_id, name=name)
        ec2 = self.resource
        if only_named:
            vpcs = ec2.vpcs.filter(Filters=[{'Name':'tag:Name', 'Values':['*']}])
        else:
            vpcs = ec2.vpcs.all()
        return [vpc_dict(v) for v in vpcs]


    def create_ec2_instance(self, image_id=None, subnet_id=None,
        key_name=None, user_data=None, instance_type=None, security_group_ids=None,
        instance_name=None, file_system_id=None):
        ec2 = self.resource
        instance_type=instance_type or 't3.small'
        key_name = key_name or 'image_genro'
        security_group_ids = security_group_ids or ['sg-07ffd42fa49e3691e']
        subnet_id = subnet_id or 'subnet-0d06bca1c5768c354'
        tags=[{'ResourceType': 'instance',
            'Tags': [{'Key': 'Name','Value': instance_name}]
            }]
        user_data = user_data or UserDataTemplate %dict(file_system_id=file_system_id,
            pod_name=instance_name)
        ec2_parameters=dict(
            ImageId=image_id,
            MinCount=1, MaxCount=1,
            SubnetId=subnet_id,
            DisableApiTermination=True,
            InstanceInitiatedShutdownBehavior='stop',
            KeyName=key_name,
            UserData=user_data,
            InstanceType=instance_type,
            SecurityGroupIds=security_group_ids,
            TagSpecifications=tags
        )
        #ec2_parameters['DryRun']=True
        instances = ec2.create_instances(**ec2_parameters)
        return instances[0].instance_id

class IAMManager(BaseAwsService):
    service_label = 'iam'

    def create_user(self, username=None):
        iam = self.resource
        user = iam.User(username)
        if not user in iam.users.all():
            user.create()

    def delete_user(self, username=None):
        iam = self.resource
        user = iam.User(username)
        if not user in iam.users.all():
            user.delete()

    def get_user(self, username=None):
        return self.resource.User(username)

    def put_user_policy(self, username=None, policyname=None, policydocument=None):
        self.client.put_user_policy(UserName=username,
                PolicyName=policyname, PolicyDocument=policydocument)

    def get_usernames(self):
        iam = self.resource
        return [u.name for u in iam.users.all()]
    
    def create_user_key_pair(self, username=None):
        iam = self.resource
        user = iam.User(username)
        key_pair = user.create_access_key_pair()
        return dict(access_key_id=key_pair.access_key_id,secret_access_key=key_pair.secret_access_key)

class S3Manager(BaseAwsService):
    service_label = 's3'

    def get_s3_policy(self, bucket=None, folder=None):
        if folder:
            fullpath = '%s/%s' % (bucket, folder)
        else:
            fullpath = bucket
        policy = { 'Version' : '2012-10-17'}
        policy['Statement'] = [{'Sid' : 'AwsIamUserPython', 
                'Effect': 'Allow', 'Action': 's3:*', 
                'Resource': ['arn:aws:s3:::%s'%bucket,
                    'arn:aws:s3:::%s/*'%fullpath]}]
        return json.dumps(policy, indent=2)


    def create_s3_for_user(self, username=None, bucket=None, region=None):
        s3 = self.resource
        region = region or 'eu-central-1'
        bucket = bucket or username
        s3.create_bucket(Bucket=bucket, 
            CreateBucketConfiguration={
                'LocationConstraint': region})
        #user = self.IAM.get_user(username)
        access_policy = self.get_s3_policy(bucket=bucket)
        self.IAM.put_user_policy(username=username, 
            policyname='s3-%s-%s'%(username, bucket),
            policydocument=access_policy)

    def allow_s3_folder_for_user(self, username=None, bucket=None, folder=None):
        #user = self.IAM.get_user(username)
        access_policy = self.get_s3_policy(bucket=bucket, folder=folder)
        self.IAM.put_user_policy(username=username, 
            policyname='s3-%s-%s-%s'%(username, bucket, folder),
            policydocument=access_policy)

class ELBV2Manager(BaseAwsService):
    service_label = 'elbv2'

    def get_load_balancers(self):
        def get_load_balancer_dict(l):
            r = dict(
                name = l['LoadBalancerName'],
                hosted_zone_id=l['CanonicalHostedZoneId'],
                dnsname=['DNSName'],
                loadbalancer_arn=l['LoadBalancerArn'])
            return r
        elbv2 = self.client
        load_balancers = elbv2.describe_load_balancers()['LoadBalancers']
        return dict([(l['LoadBalancerName'], get_load_balancer_dict(l)) for l in load_balancers])

    def get_load_balancer(self, load_balancer_name=None):
        return self.get_load_balancers().get(load_balancer_name)

    def get_listeners(self, load_balancer_name=None, loadbalancer_arn=None):
        def get_listener_dict(l):
            return dict(
                listener_arn=l['ListenerArn'],
                port=l['Port'],
                protocol=l['Protocol']
            )
        elbv2 = self.client
        if not loadbalancer_arn:
            load_balancer = self.get_load_balancer(load_balancer_name)
            if not load_balancer:
                return dict()
            loadbalancer_arn = load_balancer['loadbalancer_arn']
        target_groups = elbv2.describe_listeners(LoadBalancerArn=loadbalancer_arn)['Listeners']
        return dict([(l['Port'], get_listener_dict(l)) for l in target_groups])

    def get_listener(self, load_balancer_name=None, port=None):
        return self.get_listeners(load_balancer_name=load_balancer_name).get(port)

    def action_dict(self, action):
            return dict(
                order=action['Order'],
                targetgroup_arn=action['TargetGroupArn'],
                type=action['Type']
            )
    def contition_dict(self, condition):
            return dict(
                field=condition['Field'],
                values=condition['Values']
            )

    def rule_description_to_dict(self, rule=None):
        return dict(actions = list(map(self.action_dict, rule['Actions'])),
            conditions = list(map(self.contition_dict, rule['Conditions'])),
            rule_arn=rule['RuleArn'], isdefault=rule['IsDefault'],
            priority=rule['Priority'])



    def get_rules(self, load_balancer_name=None, port=None, listener_arn=None):
        elbv2 = self.client
        if not listener_arn:
            listener = self.get_listener(load_balancer_name=load_balancer_name, port=port)
            if not listener:
                return dict()
            listener_arn = listener['listener_arn']
        rules = elbv2.describe_rules(ListenerArn=listener_arn)['Rules']
        return [self.rule_description_to_dict(r) for r in rules]
        

    def get_target_groups(self):
        def get_target_group_dict(t):
            r = dict(
                targetgroup_arn=t['TargetGroupArn'],
                targetgroup_name=t['TargetGroupName'],
            )
        elbv2 = self.client
        target_groups = elbv2.describe_target_groups()['TargetGroups']
        return dict([(t['TargetGroupName'], t) for t in target_groups])

    def create_target_group(self, name=None, protocol=None, 
            port=None, healthcheck_protocol=None, vpc_id=None,
            healthcheck_port=None, healthcheck_path=None,
            healthcheck_interval=None, healthcheck_timeout=None, 
            healthy_threshold=None, unhealthy_threshold=None, target_type=None):
        elbv2 = self.client
        protocol = protocol or 'HTTP'
        healthcheck_protocol = healthcheck_protocol or 'HTTP'
        port = port or 443
        response = elbv2.create_target_group(
            Name=name, Protocol=protocol, Port=port, VpcId=vpc_id,
            HealthCheckProtocol=healthcheck_protocol,HealthCheckPort=healthcheck_port,
            HealthCheckPath=healthcheck_path, 
            HealthCheckIntervalSeconds=healthcheck_interval,
            HealthCheckTimeoutSeconds=healthcheck_timeout,
            HealthyThresholdCount=healthy_threshold, 
            UnhealthyThresholdCount=unhealthy_threshold,
            TargetType=target_type
        )
        targetgroup_arn = response['TargetGroupArn']
        return targetgroup_arn

    def register_target_instance(self, targetgroup_arn=None, instance_id=None):
        elbv2 = self.client
        elbv2.register_targets(TargetGroupArn=targetgroup_arn,
            Targets=[dict(Id=instance_id)])



class Route53Manager(BaseAwsService):
    service_label='route53'
    def get_hosted_zones(self):
        r53 = self.client
        hosted_zones = r53.list_hosted_zones()['HostedZones']
        return dict([(h.Name.lower().rstrip('.'), h.Id) for h in hosted_zones])

    def update_record(self, hosted_zone_id=None, name=None, 
        type=None, target=None, ttl=360):
        r53 = self.client
        parameters = {'Comment': 'add %s -> %s' % (name, target),
                    'Changes': [
                            {
                             'Action': 'UPSTERT',
                             'ResourceRecordSet': {
                                 'Name': name,
                                 'Type': type,
                                 'TTL': ttl,
                                 'ResourceRecords': [{'Value': target}]
                            }
                        }]
        }
        r53.client.change_resource_record_sets(**parameters)


class AWSManager(BaseAwsService):
    pass
    


service_classes = dict([(c.service_label,c) for c_name,c in inspect.getmembers(sys.modules[__name__],inspect.isclass) if hasattr(c,'service_label')])


def main():
    aws = AWSManager()
    #softwell_user = aws.IAM.create_user(username='user')
    #keypairs = aws.IAM.create_user_key_pair(username='user')
    #print keypairs
    bucket = aws.S3.create_s3_for_user(username='user', bucket='bkt-user')

    #print ec2.EC2.get_instances()
    #print aws.EC2.get_key_pairs()
    #print aws.EC2.get_images()
    #print aws.EC2.get_instances()
    #print aws.EC2.get_vpcs()

    #print aws.ELBV2.get_listeners(load_balancer_name='load-ld')
    print(aws.ELBV2.get_target_groups())
    #ec2.create_ec2_instance(image_id='ami-1112223333',
    #    instance_name='test-site', file_system_id='fs-44333929')

if __name__ == '__main__':
    main()