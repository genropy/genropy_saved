#from builtins import object
import tempfile
import boto3
import os
from smart_open import smart_open

class BaseCloudService(object):
    def __init__(self):
        pass
    
    def open(self, path=None, mode='r'):
        pass


class S3File(object):
    def __init__(self, mode='rb', bucket=None, key=None, 
        aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
        self.bucket = bucket
        self.key = key
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.mode = mode
        self.write_mode = ('w' in mode) or False
        self.read_mode = not self.write_mode
        self.file = None
        self.close_called = False
        self.s3 = boto3.client('s3', aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key, 
            region_name=self.region_name)
        
   
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


    def close(self):
        if not self.close_called:
            self.close_called = True
            try:
                self.file.close()
            finally:
                os.unlink(self.name)

    def __enter__(self):
        self.file.__enter__()
        if self.read_mode:
            self.s3.download_fileobj(self.bucket,self.key, self.file)
            self.file.seek(0)
        return self

    def __exit__(self, exc, value, tb):
        if self.write_mode:
            self.file.seek(0)
            self.s3.upload_fileobj(self.file, self.bucket,self.key)
        result = self.file.__exit__(exc, value, tb)
        self.close()
        return result

class S3StorageManager(BaseCloudService):

    def __init__(self, aws_access_key_id=None,
        aws_secret_access_key=None, aws_session_token=None,
        region_name=None, parent=None):
        self.aws_access_key_id=aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key
        self.aws_session_token=aws_session_token
        self.region_name=None

    def url(self, bucket=None, key=None, expiration=3600):
        s3 = boto3.client('s3', aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key= self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name= self.region_name)
        return s3.generate_presigned_url('get_object', 
            Params={'Bucket': bucket,'Key': key}, 
            ExpiresIn=expiration)

    def open(self, *args, **kwargs):
        bucket = args[0]
        key = '/'.join(args[1:])
        return smart_open("s3://%s/%s"%(bucket,key),
            s3_session=boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_session_token=self.aws_session_token,
            aws_secret_access_key= self.aws_secret_access_key,
            region_name= self.region_name)
            )