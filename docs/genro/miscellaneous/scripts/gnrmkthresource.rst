.. _gnrmkthresource:

===============
gnrmkthresource
===============

    *Last page update*: |today|
    
    gnrmkthresource is used to create automatically the :ref:`th` resources from :ref:`database
    tables <table>`. To use it, place yourself inside the package and write::
    
        gnrmkthresource [projectName:]packageName.tableName [Optional suffixes]
        
    where:
    
    * ``projectName`` is the name of the :ref:`project` and it is optional,
      as you can see from the square brackets ``[]``
    * ``packageName`` is the name of the :ref:`package <packages>`
    * ``tableName`` is the name of the :ref:`database table <table>` through which you want
      to create the TableHandler resources
      
    **Optional suffixes:**
    
    * ``-f``: force the resource creation also if destination file exists
    * ``-n``: output file name, the file will be, will work only if single table is passed
    * ``-o``: output file path will override -n/--name and automatic file will be placed at
      the ``resources/tables/tablename`` path; this will work only if a single table is passed
    * ``-i``: output file name, the file will be; this will work only if a single table is passed