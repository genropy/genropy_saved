# -*- coding: UTF-8 -*-

from gnr.core.gnrbag import Bag
from gnr.web.gnrheadlesspage import GnrHeadlessPage as page_factory

class GnrCustomWebPage(object):
    skip_connection=True


    # BEGIN base externalcall handlers
    def rootPage(self,*args, **kwargs):
        request_method = self.request.method
        service = None
        print kwargs

        service_name = kwargs.pop('service_name', None)
        if service_name:
            service = self.site.getService(service_name)
        print service
        if service:
            if not getattr(service, 'public', None):
                return self.site.not_found_exception
            result = service(**kwargs)
            if hasattr(service, 'content_type'):
                self.response.content_type = service.content_type
            else:
                self.response.content_type = 'text/plain'
                
            print 'result', result
            return result
        else:
            return self.site.not_found_exception
        
    

        