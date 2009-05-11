import logging

class GnrLogger(object):
    def __init__(self, path):
        self.path = path
        self.pylog = logging.getLogger(path)
        
    def info(self, msg, *args, **kwargs):
        self.pylog.info(msg,*args,**kwargs)
        
    def debug(self, msg, *args, **kwargs):
        self.pylog.debug(msg,*args,**kwargs)
        
    def warning(self, msg, *args, **kwargs):
        self.pylog.warning(msg,*args,**kwargs)
        
    def error(self,msg,*args,**kwargs):
        self.pylog.error(msg,*args,**kwargs)
        
    def critical(self,msg,*args,**kwargs):
        self.pylog.critical(msg,*args,**kwargs)
        
    def addHandler(self, hdlr):
        self.pylog.addHandler(hdlr)
        
    def setLevel(self, level):
        self.pylog.setLevel(level)

class GnrLog(object):
    def __init__(self):
        from gnr.core.gnrbag import Bag
        self.loggerbag = Bag()
    
    def getLogger(self, path, **kwargs):
        logger = GnrLogger(path)
        self.loggerbag.setItem(path, logger, **kwargs)
        return logger   
        
    FATAL = logging.FATAL
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET
    
gnrlogging = GnrLog()
