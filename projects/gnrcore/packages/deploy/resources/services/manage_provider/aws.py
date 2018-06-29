#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService

from gnr.core.gnrlang import GnrException
from gnr.core.gnrbag import Bag
import re
awsManage=True

try:
    import boto3
except:
    awsManage = False

class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.parent = parent
        if not awsManage:
            raise GnrException('Missing awsManage. hint: pip install boto3')



    def ec2_instances(self):
        ec2 = boto3.client('ec2')
        response = ec2.describe_instances()
        b=Bag()
        b.fromJson(response)
        result = Bag()
        for v in b['Reservations'].values():
            instances = v['Instances']
            reservation_id = v['ReservationId']
            groups = v['Groups']
            owner_id = v['OwnerId']
            for inst in instances.values():
                self.setInstanceBag(result, inst)
        return result

    def setInstanceBag(self, result, rawbag):
        instance_id = rawbag['InstanceId']
        #attrs=dict([(k,v) for k,v in rawbag.items()])

        result.setItem(instance_id, rawbag)