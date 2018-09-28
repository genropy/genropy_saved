
# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2013 Softwell. All rights reserved.

from gnr.lib.services.storage import StorageService
from gnr.web.gnrbaseclasses import BaseComponent
#from gnr.core.gnrlang import componentFactory
from smart_open import smart_open
import boto3
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


class Service(StorageService):

    def __init__(self, parent=None, bucket=None, 
        base_path=None, aws_access_key_id=None,
        aws_secret_access_key=None, aws_session_token=None,
        region_name=None, url_expiration=None, **kwargs):
        self.parent = parent
        self.bucket = bucket
        self.base_path = base_path
        self.aws_access_key_id=aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key
        self.aws_session_token=aws_session_token
        self.region_name=None
        self.url_expiration = url_expiration or 3600
    @property
    def location_identifier(self):
        return 's3/%s/%s' % (self.region_name, self.bucket)

    def internal_path(self, path):
        return '%s/%s'% (self.base_path, path)

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

    def delete(self, path):
        self._client.delete_object(Bucket=self.bucket, Key=self.internal_path(path))

    def url(self, path, _content_disposition=None, **kwargs):
        _content_disposition = _content_disposition or 'inline'
        _content_type = mimetypes.guess_type(path)[0]
        expiration = kwargs.pop('expiration', self.url_expiration)
        return self._client.generate_presigned_url('get_object', 
            Params={'Bucket': self.bucket,'Key': self.internal_path(path),
                'ResponseContentDisposition':_content_disposition,
                'ResponseContentType':_content_type}, 
            ExpiresIn=expiration)

    def open(self, path, mode=None,  **kwargs):
        return smart_open("s3://%s/%s"%(self.bucket,self.internal_path(path)),
            s3_session=self._session, mode=mode)


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



class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.bucket',lbl='Bucket')
        fb.textbox(value='^.base_path',lbl='Base path')
        fb.textbox(value='^.aws_access_key_id',lbl='Aws Access Key Id')
        fb.textbox(value='^.aws_secret_access_key',lbl='Aws Secret Access Key')
        fb.textbox(value='^.region_name',lbl='Region Name')