.. _automap:

===============
``automap.xml``
===============
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/sites/automap.png
    
    The ``automap.xml`` file is automatically created on execution of the :ref:`gnrwsgiserve` script.
    
    This XML file contains tags with all the :ref:`packages` of the :ref:`project` to which this
    file belongs to.
    
    In particular, the external file structure is::
    
        <?xml version='1.0' encoding='UTF-8'?>
        <GenRoBag></GenRoBag>
        
    Inside the ``<GenRoBag>`` tag you will find all the packages of your projects (even the
    :ref:`imported packages <instanceconfig_packages>`) and their :ref:`webpages <webpage>`;
    
    the syntax used is::
    
        <packageName name="!!fullPackageName"><packageName/>
        
    where:
    
    * ``packageName`` is the name of the :ref:`package <packages>`
    * ``fullPackageName`` is the name of the full package; the ``!!`` character allows to define
      multiple languages: for more information, check the :ref:`languages` section
      
    Inside the ``<packageName>`` tag you will find both the folders than the files of your
    :ref:`project`. The syntax is::
    
        <Name path="parentFolderName" pkg="polimed" name="!!Archivi">
        
    where:
      
    * ``Name`` is the name of the parent folder (of the webpage or of the folder), so for the
      webpages the "path" attribute is always specified, while for the folders it is specified
      if and only if the folder is a subfolder of another folder of the packages folder
      
    **Example**:
    
    Let's see the complete content of an ``automap.xml`` file of a package called "inv"
    (abbreviation of "invoice"). Inside the package there is a folder called ``archives``.
    Inside the ``archives`` folder there is the ``money`` webpage::
    
        <?xml version='1.0' encoding='UTF-8'?>
        <GenRoBag>
            <inv name="!!invoice">
                <archives pkg="invoice" name="!!Archives">
                <money path="archives/money.py" pkg="invoice" name="!!Money"></money>
            </inv>
        </GenRoBag>