
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2013 Softwell. All rights reserved.

from builtins import object
from gnr.lib.services.storage import StorageService,StorageNode,StorageResolver
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
#from gnr.core.gnrlang import componentFactory
import boto3
import botocore
import os
import tempfile
import mimetypes
from datetime import datetime
import warnings
import six
if six.PY3:
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")


class S3LocalFile(object):
    def __init__(self, mode='rb', bucket=None, key=None, s3_session=None):
        self.bucket = bucket
        self.key = key
        self.mode = mode
        self.write_mode = ('w' in mode) or False
        self.read_mode = not self.write_mode
        self.file = None
        self.close_called = False
        self.session = s3_session
        self.s3 = self.session.client('s3')

    def __getattr__(self, name):
        local_file = self.__dict__['file']
        a = getattr(local_file, name)
        if not issubclass(type(a), type(0)):
            setattr(self, name, a)
        return a

    def __del__(self):
        self.close()

    def open(self):
        self.fd,self.name = tempfile.mkstemp()
        self.file = os.fdopen(self.fd, 'w+b')


    def close(self, exit_args=False,):
        if not self.close_called:
            self.close_called = True
            if self.write_mode:
                self.file.seek(0)
                self.s3.upload_fileobj(self.file, self.bucket,self.key)
            try:
                result = None
                if exit_args:
                    result = self.file.__exit__(*exit_args)
                self.file.close()
            except Exception as e:
                import traceback
                traceback.print_exc()
            finally:
                os.unlink(self.name)
            return result

    def __enter__(self):
        self.file.__enter__()
        if self.read_mode:
            self.s3.download_fileobj(self.bucket,self.key, self.file)
            self.file.seek(0)
        return self

    def __exit__(self, exc, value, tb):
        return self.close(exit_args=(exc, value, tb))

class S3TemporaryFilename(object):
    def __init__(self, bucket=None, key=None, s3_session=None, mode=None, keep=False):
        self.bucket = bucket
        self.key = key
        self.mode = mode or 'r'
        self.write_mode = ('w' in self.mode) or False
        self.read_mode = not self.write_mode
        self.file = None
        self.close_called = False
        self.session = s3_session
        self.s3 = self.session.client('s3',config= boto3.session.Config(signature_version='s3v4'))
        self.ext = os.path.splitext(self.key)[-1]
        self.keep = keep

    def __enter__(self):
        self.fd,self.name = tempfile.mkstemp(suffix=self.ext)
        try:
            self.s3.download_file(self.bucket,self.key, self.name)
            self.enter_mtime = os.stat(self.name).st_mtime
        except botocore.exceptions.ClientError as e:
            self.enter_mtime = None
        return self.name

    def __exit__(self, exc, value, tb):
        if os.stat(self.name).st_mtime != self.enter_mtime:
            self.s3.upload_file(self.name, self.bucket,self.key)
        if not self.keep:
            os.unlink(self.name)

class Service(StorageService):

    def __init__(self, parent=None, bucket=None,
        base_path=None, aws_access_key_id=None,
        aws_secret_access_key=None, aws_session_token=None,
        region_name=None, url_expiration=None, **kwargs):
        self.parent = parent
        self.bucket = bucket
        self.base_path = (base_path or '').rstrip('/')
        self.aws_access_key_id=aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key
        self.aws_session_token=aws_session_token
        self.region_name=region_name
        self.url_expiration = url_expiration or 3600
    @property
    def location_identifier(self):
        return 's3/%s/%s' % (self.region_name, self.bucket)

    def internal_path(self, *args):
        out_list = [self.base_path]
        out_list.extend(args)
        outpath = '/'.join(out_list)
        return outpath.strip('/').replace('//','/')

    def _parent_path(self, *args):
        internalpath = self.internal_path(*args)
        path_list = internalpath.split('/')

    def isfile(self, *args):
        internalpath = self.internal_path(*args)
        if internalpath =='':
            return False
        return self._head_object(*args) is not False

    def _head_object(self,*args):
        try:
            return self._client.head_object(
                    Bucket=self.bucket,
                    Key=self.internal_path(*args))
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise

    def md5hash(self,*args):
        bucket = self._head_object(*args)
        if bucket:
            return bucket['ETag'][1:-1]

    def exists(self, *args):
        return self.isfile(*args) or self.isdir(*args)

    def makedirs(self, *args, **kwargs):
        pass

    def mkdir(self, *args, **kwargs):
        with self.open(*args+('.gnrdir',),mode='w') as dotfile:
            dotfile.write('.gnrdircontent')

    def mtime(self, *args):
        s3 = self._client
        internalpath = self.internal_path(*args)
        try:
            response = s3.head_object(
                    Bucket=self.bucket,
                    Key=internalpath)
            return response['Last-Modified']
        except botocore.exceptions.ClientError as e:
            return

    def size(self, *args):
        s3 = self._client
        internalpath = self.internal_path(*args)
        try:
            response = s3.head_object(
                    Bucket=self.bucket,
                    Key=internalpath)
            return response['ContentLength']
        except botocore.exceptions.ClientError as e:
            return

    def local_path(self, *args, **kwargs):
        mode = kwargs.get('mode', 'r')
        keep = kwargs.get('keep', False)
        internalpath = self.internal_path(*args)
        return S3TemporaryFilename(bucket=self.bucket, key=internalpath,
            s3_session=self._session, mode=mode, keep=keep)

    def isdir(self, *args):
        internalpath = self.internal_path(*args)
        if internalpath =='':
            return True
        parent_path = '/'.join(internalpath.split('/')[:-1])
        s3 = self._client
        if parent_path and not parent_path.endswith('/'):
            parent_path='%s/'%parent_path
        response=s3.list_objects_v2(Bucket=self.bucket, Prefix=parent_path, Delimiter='/')
        common_prefixes = response.get('CommonPrefixes') or []
        dirnames = [c['Prefix'] for c in common_prefixes]
        if  not internalpath.endswith('/'):
            internalpath='%s/'%internalpath
        return internalpath in dirnames

    @property
    def _session(self):
        if not hasattr(self, '_boto_session') or (hasattr(self,'_boto_session_ts') and (datetime.now()-self._boto_session_ts).seconds>120):
            self._boto_session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_session_token=self.aws_session_token,
                aws_secret_access_key= self.aws_secret_access_key,
                region_name= self.region_name)
            self._boto_session_ts = datetime.now()
        return self._boto_session

    def _s3_copy(self, source_bucket=None, source_key=None,
        dest_bucket=None, dest_key=None):
        source_pars = {'Bucket' : source_bucket,
                    'Key':source_key}
        self._client.copy_object(CopySource = source_pars,
            Bucket = dest_bucket,
            Key = dest_key)

    @property
    def _client(self):
        if not hasattr(self, '_boto_client') or (hasattr(self,'_boto_client_ts') and (datetime.now()-self._boto_client_ts).seconds>120):
            self._boto_client = self._session.client('s3', config= boto3.session.Config(signature_version='s3v4'))
            self._boto_client_ts = datetime.now()
        return self._boto_client

    def delete_file(self, *args):
        self._client.delete_object(Bucket=self.bucket, Key=self.internal_path(*args))

    def delete_dir(self, *args):
        prefix = self.internal_path(*args)
        client = self._client
        prefix = prefix.strip('/')+'/' if prefix else ''
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
        delete_us = dict(Objects=[])
        for item in pages.search('Contents'):
            delete_us['Objects'].append(dict(Key=item['Key']))

            # flush once aws limit reached
            if len(delete_us['Objects']) >= 1000:
                client.delete_objects(Bucket=self.bucket, Delete=delete_us)
                delete_us = dict(Objects=[])

        # flush rest
        if len(delete_us['Objects']):
            client.delete_objects(Bucket=self.bucket, Delete=delete_us)

    def url(self, *args , **kwargs):
        kwargs = kwargs or {}
        _content_disposition = kwargs.get('_content_disposition') or 'inline'
        _download = kwargs.get('_download')
        if _download:
            kwargs['_content_disposition'] = "attachment; filename=%s" % self.basename(*args)
        internal_path = self.internal_path(*args)
        _content_type = mimetypes.guess_type(internal_path)[0]
        expiration = kwargs.pop('expiration', self.url_expiration)
        params={'Bucket': self.bucket,'Key': internal_path,
                'ResponseContentDisposition':_content_disposition}
        if _content_type:
            params['ResponseContentType'] = _content_type
        return self._client.generate_presigned_url('get_object',
            Params=params,
            ExpiresIn=expiration)
    
    def internal_url(self, *args, **kwargs):
        kwargs = kwargs or {}
        kwargs['_download'] = True
        return super(Service, self).internal_url(*args, **kwargs)

    def upload_url(self, *args, **kwargs):
        internal_path = self.internal_path(*args)
        expiration = kwargs.pop('expiration', self.url_expiration)
        return self._client.generate_presigned_url('put_object',
            Params={'Bucket': self.bucket,'Key': internal_path},
            ExpiresIn=expiration)

    def open(self, *args, **kwargs):
        kwargs['mode'] = kwargs.get('mode', 'rb')
        from smart_open import open
        open.DEFAULT_BUFFER_SIZE = 1024 * 1024
        return open("s3://%s/%s"%(self.bucket,self.internal_path(*args)),
            transport_params={'session':self._session}, **kwargs)


    def duplicateNode(self, sourceNode=None, destNode=None): # will work only in the same bucket
        self._s3_copy(source_bucket=sourceNode.service.bucket,
            source_key=sourceNode.internal_path,
            dest_bucket=destNode.service.bucket, dest_key=destNode.internal_path)

    def renameNode(self, sourceNode=None, destNode=None):
        self._s3_copy(source_bucket=sourceNode.service.bucket,
            source_key=sourceNode.internal_path,
            dest_bucket=destNode.service.bucket, dest_key=destNode.internal_path)
        self.delete(sourceNode.path)
        return destNode

    def serve(self, path, environ, start_response, download=False, download_name=None, **kwargs):
        if download or download_name:
            download_name = download_name or self.basename(path)
            content_disposition = "attachment; filename=%s" % download_name
        else:
            content_disposition = "inline"
        url = self.url(path, _content_disposition=content_disposition)
        if url:
            return self.parent.redirect(environ, start_response, location=url,temporary=True)

    def children(self, *args, **kwargs):
        if not self.bucket:
            return []
        def strip_prefix(inpath, prefix=None):
            prefix = prefix or self.base_path
            return inpath.replace(prefix,'',1).strip('/')
        s3 = self._client
        dirpath = self.internal_path(*args)
        out = []
        if dirpath and not dirpath.endswith('/'):
            dirpath='%s/'%dirpath
        response=s3.list_objects_v2(Bucket=self.bucket, Prefix=dirpath, Delimiter='/')
        contents = response.get('Contents') or []
        common_prefixes = response.get('CommonPrefixes') or []
        for subdir in common_prefixes:
            subprefix = subdir['Prefix']
            if subprefix == dirpath:
                continue
            subpath = strip_prefix(subprefix)
            out.append(StorageNode(parent=self.parent,
                path=subpath,
                service=self))
        for rfile in contents:
            key = rfile['Key']
            if key == dirpath or key.endswith('.gnrdir'):
                continue
            out.append(StorageNode(parent=self.parent,
                path=strip_prefix(key), service=self))
        return out

class ServiceParameters(BaseComponent):
    py_requires = 'gnrcomponents/storagetree:StorageTree'
    def service_parameters(self,pane,datapath=None,**kwargs):
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(datapath=datapath)
        fb.textbox(value='^.bucket',lbl='Bucket')
        fb.textbox(value='^.base_path',lbl='Base path')
        fb.textbox(value='^.aws_access_key_id',lbl='Aws Access Key Id')
        fb.textbox(value='^.aws_secret_access_key',lbl='Aws Secret Access Key')
        fb.textbox(value='^.region_name',lbl='Region Name')
        bc.storageTreeFrame(frameCode='bucketStorage',storagepath='^#FORM.record.service_name?=#v+":"',
                                border='1px solid silver',margin='2px',rounded=4,
                                region='center',preview_region='right',
                                store__onBuilt=1,
                                preview_border_left='1px solid silver',preview_width='50%')
