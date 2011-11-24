.. _remote:

======
remote
======

    *Last page update*: |today|
    
    * :ref:`remote_def`
    * :ref:`remote_syntax`
    * :ref:`remote_examples`:
    
        * :ref:`remote_examples_simple`

.. _remote_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.remote
    
    The remote method allow to build remotely any element of a :ref:`webpage`, like a
    a :ref:`contentpane`, a :ref:`tabcontainer`, a :ref:`form`, and so on.
    
.. _remote_syntax:

syntax
======

    **remote call**::
    
      remote(method='STRING', [**kwargs])
    
    where:
    
    * ``STRING`` is the name of the remote method declaration, without its ``remote_`` prefix
    
    **remote method declaration**::
    
      def remote_STRING(self, [**kwargs]):
      
    where:
    
    * ``STRING`` is the name you gave to the *method* attribute in the remote call
    
.. _remote_examples:

examples
========

.. _remote_examples_simple:

simple example
--------------

    * `remote [basic] <http://localhost:8080/remote/1>`_
    * **Introduction**: an example with the basic usage of the remote method
    
      * In line 16 we call the remote; ``tabs`` is the name of the method
      * In line 18 we define the remote method, as ``remote_tabs``, that is ``remote_``
        plus the ``tabs`` defined in line 16
      * Lines 19, 20 and 21 build some tabContainers remotely (that is, on server)
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **controllers**: :ref:`remote`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`bordercontainer`, :ref:`contentpane`, :ref:`data`,
                  :ref:`numberspinner`
                  
    * **Code**::
    
         1    # -*- coding: UTF-8 -*-
         2    """remote"""
         3
         4    class GnrCustomWebPage(object):
         5        py_requires = "gnrcomponents/testhandler:TestHandlerFull"
         6
         7        def test_1_remote(self, pane):
         8            """Basic remote"""
         9            bc = pane.borderContainer(height='300px')
        10            fb = bc.contentPane(region='top', height='30px').formbuilder(cols=2)
        11            fb.numberspinner(value='^.numtabs', lbl='Number of tabs', min=0, max=20)
        12            bc.data('.numtabs', 0)
        13            fb.div('Move focus out of the NumberSpinner to update tabs (max tab numbers set to 20)',
        14                   font_size='.9em', text_align='justify', margin='10px')
        15            tc = bc.tabContainer(region='center')
        16            tc.remote('tabs', numtabs='^.numtabs')
        17            
        18        def remote_tabs(self, tc, numtabs):
        19            for i in range(numtabs):
        20                tab = tc.contentPane(title='Tab %d' % i, position='absolute', margin='60px')
        21                tab.div('This is tab n.%d' % i)
        