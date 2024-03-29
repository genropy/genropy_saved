.. _wsgi:

====
WSGI
====
    
    *Last page update*: |today|
    
    WSGI (*Web Server Gateway Interface*) is a standard for interfacing with Python web frameworks webservers.
    It also allows you to compose various web components together through a system of middlewares (similar
    concept, but not compatible with similar components in Django). A WSGI site (http://wsgi.org/wsgi)
    contains links to many useful resources (frameworks, middlewares, servers).
    
    WSGI application defines a function that takes a Web request and returns the answer. WSGI middleware
    is simply an application that calls another, as in the pattern Decorator
    (http://en.wikipedia.org/wiki/Decorator_pattern). WSGI standard defines a standard format for the
    request (which can be decorated with additional information when processing the various middlewares)
    and response (which can also be asynchronous).
    
    GenroPy Beaker (http://beaker.groovie.org/) using middleware for session management and weberror
    management Traceback (including the useful ability to open a python interpreter at the point where
    the error occurs). GenroPy uses Paste (http://pythonpaste.org/) WebOb
    (http://pythonpaste.org/webob/reference.html) during development and with standalone servers.
    
    We report here the WSGI declaration (you can find it in the :ref:`sites_root` file, within the
    :ref:`sites` folder of every Genro :ref:`project`)::
    
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