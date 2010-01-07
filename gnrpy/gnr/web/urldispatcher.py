from gnr.core.gnrlang import gnrImport
from time import time
import os.path
from webob import Request,Response,exc

def load_controller(string,function='index'):
    module_string = string.lstrip('/').split('/')
    module_path = os.path.join(*module_string)
    module_dotted='.'.join(module_string)
    imported = gnrImport(module_path,importAs=str(module_path.replace('/','_')))
    func = None
    if imported:
        func = getattr(imported, function)
    return func

def reqargs(req):
    #return dict(getattr(req,req.method))
    return dict(req.params)

class Dispatcher(object):
    
    def __init__(self,this_script,home_uri='/',debug=False,gnrwebapp=None):
        self.this_script = os.path.realpath(this_script)
        self.base_dir = os.path.dirname(self.this_script)
        self.site_path = os.path.dirname(self.base_dir)
        self.home_uri=home_uri
        self.debug=debug
        self.gnrwebapp=gnrwebapp

    
    def __call__(self, environ, start_response):
        t=time()
        req = Request(environ)
        resp = Response()
        info=req.path_info
        if not info: info='/index.py'
        if info[-4:]=='.py/': info=info[:-1]
        if info[-1]=='/': info+="index.py"
        if info == 'index.py' or info=='':
            return self.index(environ, start_response)
        elif '.py' in info:
            if info[-3:]=='.py':
                info=info[:-3]
                function='index'
            else:
                info,function=info.split('.py/',1)
                if function=='': function='index'
            try:
                func=load_controller(info,function)
            except ImportError:
                raise exc.HTTPNotFound('404 Not Found')
            try:
                wsgipars=dict(sitepath=self.site_path,home_uri=self.home_uri,response=resp,
                            debug=self.debug,gnrwebapp=self.gnrwebapp)
                result = func(req,wsgipars=wsgipars, **reqargs(req))
            except exc.HTTPException, e:
                return e(environ, start_response)    
            if isinstance(result, unicode):
                resp.content_type='text/plain'
                resp.unicode_body=result
            elif isinstance(result, basestring):
                resp.body=result
            elif isinstance(result, Response):
                resp=result
            totaltime = time()-t
            resp.headers['X-GnrTime'] = str(totaltime)
            return resp(environ, start_response)
        else:
            raise exc.HTTPNotFound()
            
    def index(self, environ, start_response):
        req = Request(environ)
        try:
            resp = GnrWebPage(req, GnrIndexWebPage, self.this_script, home_uri=self.home_uri, debug=self.debug, **reqargs(req)).index()
        except exc.HTTPException, e:
            resp = e
        if isinstance(resp, basestring):
            resp = Response(body=resp)
        return resp(environ, start_response)

