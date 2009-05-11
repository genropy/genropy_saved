from gnr.web.gnrwebpage import GnrWebPage,GnrIndexWebPage

def index(req,**kwargs):
    return GnrWebPage(req, GnrIndexWebPage, __file__, **kwargs).index()
