.. _frameindex:

==========
FrameIndex
==========
    
    *Last page update*: |today|
    
    .. note:: summary of the component requirements:
              
              * It is NOT a :ref:`components_standard`, so you have to import the correct
                package in your :ref:`instances_instanceconfig` file (more information on the
                importation of a package in the :ref:`instanceconfig_packages` documentation
                section).
                
                For the FrameIndex the package to be imported is the ``adm`` package.
                The syntax is::
                
                    <gnrcore:adm/>
                    
              * It is an :ref:`components_active`. Its :ref:`webpages_py_requires` is::
                
                  py_requires='frameindex'
                  
    add???