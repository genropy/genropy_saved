import os
import re

from datetime import datetime
from gnr.core import gnrstring
from gnr.core.gnrbag import Bag,DirectoryResolver,BagResolver
from gnr.lib.services import GnrBaseService


class StorageService(GnrBaseService):
    def open(self,**kwargs):
        pass

    def url(self,*args):
        pass