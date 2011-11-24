.. _webpage_build_phase:

============================
The build phase of a webpage
============================

    *Last page update*: |today|
    
    In the construction of the pages, first GenroPy loads the browser (client) with its Javascript engine
    (the Genro engine). Then the javascript engine immediately requests the server to build the recipe for
    the DOM. This recipe is returned to the client in a :ref:`bag`. This is the page description
    and content of the original datastore form of bags. At this point, the JS can make calls to the python
    code to further buildings on the page.
    
    In practice, GenroPy behaves in this way:
    
    #. The client makes the HTTP request page ``foo`` through :ref:`wsgi` site::
    
        client ----------- HTTP ----------> server (wsgisite)
        
    #. GenroPy sends a standard blank page, which contains practically only the engine ``gnrjs``::
    
        client <----- javascript engine --- server (wsgisite)
        
    #. The JavaScript engine calls the server page content, that is a server side Python function called the
       ``main`` of ``WebPage`` ::
    
        js engine ------- ready ----------> server
        
    #. The server sends a description of the page content in high level in terms of widgets, and content of
       the :ref:`datastore` in the form of bags::
        
        page js <-------- bags ------------ page python
        
    #. From then on, the communication proceeds primarily doing updates to the datastore (or user interface)
       using the functions rpc::
    
        page js <- dataRpc() or remote() -> page python
        
    Genro creates a :ref:`bag` using genropy syntax and this ``Bag`` is sent as
    XML to the client. In the client the :ref:`we` will be stored
    in the struct bag (??? find a name for the struct Bag!), while data elements will
    be placed in the :ref:`datastore`
    
    When the XML arrives and the two bags are created a builder is started that will use the struct bag to
    create html and dojo elements. The builder will also 'link' data bag with the related widgets using the
    '^' syntax [#]_.
    
    Data bag is really dynamic and you can work on data basically in three ways:
    
    * data that are passed in the first call (main)
    * data that are entered from the user
    * data that are exchanged with server using rpc commands
    
    Another ways to work on data are:
    
    * user data entries
    * javascript (client) scripts
    * python (server) scripts
    
    In Genro, to use a script you have to use data and controllers:
    
    * client-side controllers: :ref:`datacontroller`, :ref:`dataformula`,
      :ref:`datascript` (deprecated).
    * server-side controllers: :ref:`datarecord`, :ref:`datarpc`,
      :ref:`dataselection`, :ref:`data`.
    
    For an introduction to the controllers, please check :ref:`controllers_intro`
    
**Footnotes**:

.. [#] For more information on the circumflex accent, please check :ref:`datastore_syntax`.
