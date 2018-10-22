
# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2013 Softwell. All rights reserved.

from gnr.lib.services.storage import StorageService,StorageNode
from gnr.web.gnrbaseclasses import BaseComponent
#from gnr.core.gnrlang import componentFactory
from smart_open import smart_open
import boto3
import botocore
import os
import tempfile
import mimetypes

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
        file = self.__dict__['file']
        a = getattr(file, name)
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
    def __init__(self, bucket=None, key=None, s3_session=None, mode=None):
        self.bucket = bucket
        self.key = key
        self.mode = mode or 'r'
        self.write_mode = ('w' in self.mode) or False
        self.read_mode = not self.write_mode
        self.file = None
        self.close_called = False
        self.session = s3_session
        self.s3 = self.session.client('s3')
        self.ext = os.path.splitext(self.key)[-1]

    def __enter__(self):
        self.fd,self.name = tempfile.mkstemp(suffix=self.ext)
        if self.read_mode:
            self.s3.download_file(self.bucket,self.key, self.name)
        return self.name

    def __exit__(self, exc, value, tb):
        if self.write_mode:
            self.s3.upload_file(self.name, self.bucket,self.key)
        os.unlink(self.name)

class Service(StorageService):

    def __init__(self, parent=None, bucket=None,
        base_path=None, aws_access_key_id=None,
        aws_secret_access_key=None, aws_session_token=None,
        region_name=None, url_expiration=None, **kwargs):
        self.parent = parent
        self.bucket = bucket
        self.base_path = base_path or ''
        self.aws_access_key_id=aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key
        self.aws_session_token=aws_session_token
        self.region_name=None
        self.url_expiration = url_expiration or 3600
    @property
    def location_identifier(self):
        return 's3/%s/%s' % (self.region_name, self.bucket)

    def internal_path(self, *args):
        out_list = [self.base_path]
        out_list.extend(args)
        outpath = '/'.join(out_list)
        return outpath.strip('/')

    def _parent_path(self, *args):
        internalpath = self.internal_path(*args)
        path_list = internalpath.split('/')

    def exists(self, *args):
        s3 = self._client
        internalpath = self.internal_path(*args)
        try:
            response = s3.head_object(
                    Bucket=self.bucket,
                    Key=internalpath)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise
        return True

    def makedirs(self, *args, **kwargs):
        pass

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

    def local_path(self, *args, **kwargs):
        mode = kwargs.get('mode', 'r')
        internalpath = self.internal_path(*args)
        return S3TemporaryFilename(bucket=self.bucket, key=internalpath,
            s3_session=self._session, mode=mode)

    def isdir(self, *args):
        internalpath = self.internal_path(*args)
        if internalpath =='':
            return True
        parent_path = '/'.join(internalpath.split('/')[:-1])
        s3 = self._client
        if parent_path and not parent_path.endswith('/'):
            parent_path='%s/'%parent_path
        response=s3.list_objects_v2(Bucket=self.bucket, Prefix=parent_path, Delimiter='/')
        common_prefixes = response.get('CommonPrefixes')
        dirnames = [c['Prefix'] for c in common_prefixes]
        if  not internalpath.endswith('/'):
            internalpath='%s/'%internalpath
        return internalpath in dirnames

    @property
    def _session(self):
        return boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_session_token=self.aws_session_token,
            aws_secret_access_key= self.aws_secret_access_key,
            region_name= self.region_name)

    def _s3_copy(self, source_bucket=None, source_key=None,
        dest_bucket=None, dest_key=None):
        source_pars = {'Bucket' : source_bucket,
                    'Key':source_key}
        self._client.copy_object(CopySource = source_pars,
            Bucket = dest_bucket,
            Key = dest_key)

    @property
    def _client(self):
        return self._session.client('s3')

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
        _content_disposition = kwargs.get('_content_disposition') or 'inline'
        internal_path = self.internal_path(*args)
        _content_type = mimetypes.guess_type(internal_path)[0]
        expiration = kwargs.pop('expiration', self.url_expiration)
        return self._client.generate_presigned_url('get_object',
            Params={'Bucket': self.bucket,'Key': internal_path,
                'ResponseContentDisposition':_content_disposition,
                'ResponseContentType':_content_type},
            ExpiresIn=expiration)

    def upload_url(self, *args, **kwargs):
        internal_path = self.internal_path(*args)
        expiration = kwargs.pop('expiration', self.url_expiration)
        return self._client.generate_presigned_url('put_object',
            Params={'Bucket': self.bucket,'Key': internal_path},
            ExpiresIn=expiration)

    def open(self, *args, **kwargs):
        return smart_open("s3://%s/%s"%(self.bucket,self.internal_path(*args)),
            s3_session=self._session, **kwargs)


    def duplicateNode(self, sourceNode=None, destNode=None): # will work only in the same bucket
        self._s3_copy(source_bucket=sourceNode.bucket,
            source_key=sourceNode.internal_path,
            dest_bucket=destNode.bucket, dest_key=destNode.bucket)

    def renameNode(self, sourceNode=None, destNode=None):
        self._s3_copy(source_bucket=sourceNode.bucket,
            source_key=sourceNode.internal_path,
            dest_bucket=destNode.bucket, dest_key=destNode.bucket)
        self.delete(sourceNode.path)

    def serve(self, path, environ, start_response, download=False, download_name=None, **kwargs):
        if download or download_name:
            download_name = download_name or self.base_name
            content_disposition = "attachment; filename=%s" % download_name
        else:
            content_disposition = "inline"
        url = self.url(path, _content_disposition=content_disposition)
        if url:
            return self.parent.redirect(environ, start_response, location=url)

    def listdir(self, path, **kwargs):
        def strip_prefix(inpath, prefix=None):
            prefix = prefix or self.base_path
            return inpath.replace(prefix,'',1).strip('/')
        s3 = self._client
        dirpath = self.internal_path(path)
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
            if key == dirpath:
                continue
            out.append(StorageNode(parent=self.parent,
                path=strip_prefix(key), service=self))
        return out

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.bucket',lbl='Bucket')
        fb.textbox(value='^.base_path',lbl='Base path')
        fb.textbox(value='^.aws_access_key_id',lbl='Aws Access Key Id')
        fb.textbox(value='^.aws_secret_access_key',lbl='Aws Secret Access Key')
        fb.textbox(value='^.region_name',lbl='Region Name')