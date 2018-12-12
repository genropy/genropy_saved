
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2013 Softwell. All rights reserved.

from gnr.lib.services.queue import QueueService
from gnr.web.gnrbaseclasses import BaseComponent
#from gnr.core.gnrlang import componentFactory
import boto3
import botocore


class Service(QueueService):

    def __init__(self, parent=None, queue_name=None,
        aws_access_key_id=None, aws_secret_access_key=None,
        aws_session_token=None, region_name=None, 
        **kwargs):
        self.parent = parent
        self.queue_name = queue_name
        self.aws_access_key_id=aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key
        self.aws_session_token=aws_session_token
        self.region_name=region_name

    @property
    def sqs_resource(self):
        return self._session.resource('sqs')

    @property
    def queue(self):
        try:
            return self.sqs_resource.get_queue_by_name(QueueName=self.queue_name)
        except botocore.exceptions.ClientError as e:
            if not e.response['Error']['Code']=='AWS.SimpleQueueService.NonExistentQueue':
                raise



    @property
    def _session(self):
        return boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_session_token=self.aws_session_token,
            aws_secret_access_key= self.aws_secret_access_key,
            region_name= self.region_name)

    def run(self, running):
        queue = self.queue
        while running.value:

            time.sleep(2)
            print 'ciao'
    
    def handle_messagges(self, message):

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.bucket',lbl='Bucket')
        fb.textbox(value='^.base_path',lbl='Base path')
        fb.textbox(value='^.aws_access_key_id',lbl='Aws Access Key Id')
        fb.textbox(value='^.aws_secret_access_key',lbl='Aws Secret Access Key')
        fb.textbox(value='^.region_name',lbl='Region Name')