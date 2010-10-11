# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
import os

class DropUploader(BaseComponent):    
    def dropUploader(self,pane,ext='',**kwargs):
        pane.div(drop_types='Files',drop_ext=ext,
                 drop_action="""console.log(files);drop_uploader.send_files(files)""",
                 width='100px',height='50px',background_color='#c7ff9a')
        
        
    def file_saver(self,files=None, dest_path=None, static_handler='site'):
        if not files or not dest_path:
            return
        uploaded_files=[]
        static_handler = self.site.getStatic(static_handler)
        dest_dir = static_handler.path(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        for fileHandle in files:
            f=fileHandle.file
            content=f.read()
            filename=fileHandle.filename
            file_path = static_handler.path(dest_path,filename)
            file_url = static_handler.url(dest_path,filename)
            with file(file_path, 'wb') as outfile:
                outfile.write(content)
            uploaded_files.append(dict(url=file_url, path=file_path))
        return uploaded_files

    def rpc_upload(self,user_file=None,**kwargs):
        uploaded_files=self.file_saver(user_file, dest_path='uploaded_files')
        print uploaded_files
        return 'uploaded'