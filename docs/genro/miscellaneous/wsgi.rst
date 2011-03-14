.. _genro_wsgi:

====
WSGI
====

    WSGI (*Web Server Gateway Interface*) is a standard for interfacing with Python web frameworks webservers. It also allows you to compose various web components together through a system of middlewares (similar concept, but not compatible with similar components in Django). A WSGI_ site contains links to many useful resources (frameworks, middlewares, servers).
    
    .. _WSGI: http://wsgi.org/wsgi
    
    WSGI application defines a function that takes a Web request and returns the answer. WSGI middleware is simply an application that calls another, as in the pattern Decorator_.
    WSGI standard defines a standard format for the request (which can be decorated with additional information when processing the various middlewares) and response (which can also be asynchronous).

    .. _Decorator: http://en.wikipedia.org/wiki/Decorator_pattern
    
    GenroPy Beaker_ using middleware for session management and weberror management Traceback (including the useful ability to open a python interpreter at the point where the error occurs). GenroPy uses Paste_ WebOb_ during development and with standalone servers.

    .. _Beaker: http://beaker.groovie.org/
    .. _Paste: http://pythonpaste.org/
    .. _WebOb: http://pythonpaste.org/webob/reference.html
    
    We report here the WSGI declaration (you can find it in the :ref:`sites_root` file, within the :ref:`genro_sites_index` folder of every Genro :ref:`genro_structure_mainproject`)::
    
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

Apache WSGI
===========

    To use WSGI with apache, you must install and configure the module ``mod_wsgi``::
        
        <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www
        WSGIDaemonProcess gnr user=genro group=genro python-eggs=/tmp threads=25
        SetEnv PROCESS_GROUP gnr
        WSGIProcessGroup %{ENV:PROCESS_GROUP}
        # modify the following line to point your site
        WSGIScriptAlias / /home/genro/progetti/mmusic/sites/provarci/root.py
        #WSGIRestrictProcess gnr
        <Directory /home/genro/progetti/mmusic/sites/provarci>
        Options Indexes FollowSymLinks
        AllowOverride All
        Order allow,deny
        Allow from all
        </Directory>
        </VirtualHost>