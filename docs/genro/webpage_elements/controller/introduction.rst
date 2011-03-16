.. _genro_controllers_intro:

===============================
Introduction to the controllers
===============================

    * :ref:`controllers_def`
    * :ref:`controllers_client`, :ref:`controllers_server`
    * :ref:`controllers_attributes`
    * :ref:`controllers_examples`
    
.. _controllers_def:

Definition
==========

    The Genro controllers receive inputs and initiate a response by making calls on model objects.

    We emphasize that all the controllers can be attached to every Genro object.

    .. note:: we recommend you to read :ref:`genro_webpage` before reading this paragraph.

    The controllers can be divided in two groups:
    
    * the :ref:`controllers_client`
    * the :ref:`controllers_server`

.. _controllers_client:

client-side controllers
=======================

    The client-side controllers work on the client through Javascript; they are:

    * :ref:`genro_datacontroller`
    * :ref:`genro_dataformula`
    * :ref:`genro_datascript` (*deprecated*)

.. _controllers_server:

server-side controllers
=======================

    The server-side controllers work on the server thorugh Python; they are:

    * :ref:`genro_datarecord`
    * :ref:`genro_datarpc`
    * :ref:`genro_dataselection`

.. _controllers_attributes:

commons attributes
=================

    Let's see all the controllers' commons attributes:
    
    * *_init*: Boolean; if True, the controller is executed when the line containing *_init* is read. Default value is ``False``. For more information, check the :ref:`controllers_init` example.
    * *_onStart*: Boolean; if True, the controller is executed only after that all the line codes are read. Default value is ``False``. For more information, check the :ref:`controllers_onStart` example.
    * *_timing*: number (seconds); the controller will be triggered every "x" seconds, where "x" is the number defined in this attribute. For more information, check the :ref:`controllers_timing` example.

.. _controllers_examples:

Examples
========

.. _controllers_init:

``init``
========
    
    An example of the *_init* attribute::
        
        #!/usr/bin/env pythonw
        # -*- coding: UTF-8 -*-
        
        import datetime
        
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                hour = root.div(font_size='20pt', border='3px solid yellow', padding='10px', margin_top='5px')
                hour.span('^demo.hour')
                root.dataRpc('demo.hour', 'getTime', _fired='^updateTime', _init=True)
                hour.button('Update', fire='updateTime', margin='20px')
                
            def rpc_getTime(self):
                return self.toText(datetime.datetime.now(), format='HH:mm:ss')
                
    The *_init* attribute allows to launch the rpc called ``getTime`` as soon as the line containing the :ref:`genro_datarpc` is read.
    
.. _controllers_onStart:

``onStart``
===========
    
    An example of the *_onStart* attribute::
    
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                root.dataController("console.log('Page loaded!')", _onStart=True)
                # other line codes...
                
    We put a ``dataController`` to control if the page has been succesfully read: with ``_onStart=True`` the line including the ``dataController`` will be executed only AFTER that the compiler have read all the line codes.

.. _controllers_timing:

``timing``
==========

    An example of the *_timing* attribute::
    
        #!/usr/bin/env pythonw
        # -*- coding: UTF-8 -*-
        
        import datetime
        
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                root.dataRpc('demo.autoHour', 'getTime', _timing='1', _onStart=True)
                hour = root.div('^demo.autoHour', font_size='20pt', padding='20px', margin_top='5px')
                
            def rpc_getTime(self):
                return self.toText(datetime.datetime.now(), format='HH:mm:ss')
                