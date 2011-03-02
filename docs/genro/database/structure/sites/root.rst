.. _sites_root:

===========
``root.py``
===========

    In this file you have to put the WSGI declaration.
    
    If you follow the steps of the :ref:`sites_autofill` section, you will find the following WSGI declaration, that contains all the necessary to handle the WSGI::
    
        #!/usr/bin/env python2.6
        import sys
        sys.stdout = sys.stderr
        from gnr.web.gnrwsgisite import GnrWsgiSite
        site = GnrWsgiSite(__file__)
        
        def application(environ,start_response):
            return site(environ,start_response)
        
        if __name__ == '__main__':
            from gnr.web.server import NewServer
            server=NewServer(__file__)
            server.run()
            
    For more information on WSGI, please check the Genro :ref:`genro_wsgi` documentation page.