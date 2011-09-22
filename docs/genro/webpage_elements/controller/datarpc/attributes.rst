.. _controllers_attributes:

=================
common attributes
=================

    *Last page update*: |today|
    
    Let's see all the controllers' commons attributes:
    
    * *_init*: Boolean; if True, the controller is executed when the line containing *_init* is read.
      Default value is ``False``
      
      **example**::
      
          #!/usr/bin/env pythonw
          # -*- coding: UTF-8 -*-

          import datetime

          class GnrCustomWebPage(object):
              def main(self, root, **kwargs):
                  hour = root.div(font_size='20pt',border='3px solid yellow',
                                  padding='10px',margin_top='5px')
                  hour.span('^demo.hour')
                  root.dataRpc('demo.hour','getTime',_fired='^updateTime',_init=True)
                  hour.button('Update', fire='updateTime', margin='20px')
                  
              def rpc_getTime(self):
                  return self.toText(datetime.datetime.now(), format='HH:mm:ss')
                  
      The *_init* attribute allows to launch the rpc called ``getTime`` as soon as the line
      containing the :ref:`datarpc` is read
      
    * *_onStart*: Boolean; if True, the controller is executed only after that all the line codes are read.
      Default value is ``False``
      
      **Example**::

          class GnrCustomWebPage(object):
              def main(self, root, **kwargs):
                  root.dataController("console.log('Page loaded!')", _onStart=True)
                  # other line codes...

      We put a ``dataController`` to control if the page has been succesfully read: with ``_onStart=True``
      the line including the ``dataController`` will be executed only AFTER that the compiler have read
      all the line codes
      
    * *_timing*: number (seconds); the controller will be triggered every "x" seconds, where "x" is the
      number defined in this attribute
      
      **Example**::
      
          #!/usr/bin/env pythonw
          # -*- coding: UTF-8 -*-

          import datetime

          class GnrCustomWebPage(object):
              def main(self, root, **kwargs):
                  root.dataRpc('demo.autoHour', 'getTime', _timing='1', _onStart=True)
                  hour = root.div('^demo.autoHour', font_size='20pt', padding='20px', margin_top='5px')

              def rpc_getTime(self):
                  return self.toText(datetime.datetime.now(), format='HH:mm:ss')
                  