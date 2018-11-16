from gnrpkg.sys.services.cloudmanager import CloudManager
from gnr.utils.awsmanager import AWSManager
from gnr.web.gnrbaseclasses import BaseComponent

class Service(CloudManager):

    def __init__(self, parent, aws_access_key_id=None,
        aws_secret_access_key=None,
        region_name=None):
        self.parent=parent
        self.aws_manager = AWSManager(aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name)

    def regions(self, service_name=None, region_name=None):
        return self.aws_manager.regions(service_name=service_name, region_name=region_name)

    def get_instances(self):
        return self.aws_manager.EC2.get_instances()

    def create_user(self, username=None):
        return self.aws_manager.IAM.create_user(username=username)

    def delete_user(self, username=None):
        return self.aws_manager.IAM.delete_user(username=username)

    def get_user(self, username=None):
        return self.aws_manager.IAM.get_user(username=username)

    def put_user_policy(self, username=None, policyname=None, policydocument=None):
        return self.aws_manager.IAM.put_user_policy(username=username, policyname=policyname,
            policydocument=policydocument)

    def get_usernames(self):
        return self.aws_manager.IAM.get_usernames()

    def create_user_key_pair(self, username=None):
        return self.aws_manager.IAM.create_user_key_pair(username=username)

    def get_s3_policy(self, bucket=None, folder=None):
        return self.aws_manager.S3.get_s3_policy(bucket=bucket, folder=folder)

    def create_s3_for_user(self, username=None, bucket=None, region=None):
        return self.aws_manager.S3.create_s3_for_user(username=username,
            bucket=bucket, region=region)

    def allow_s3_folder_for_user(self, username=None, bucket=None, folder=None):
        return self.aws_manager.S3.allow_s3_folder_for_user(username=username,
            bucket=bucket, folder=folder)

class ServiceParameters(BaseComponent):
    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.aws_access_key_id',lbl='Aws Access Key Id')
        fb.textbox(value='^.aws_secret_access_key',lbl='Aws Secret Access Key')
        fb.textbox(value='^.region_name',lbl='Region Name')