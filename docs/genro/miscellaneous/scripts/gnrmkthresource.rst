.. _gnrmkthresource:

===============
gnrmkthresource
===============

    *Last page update*: |today|
    
    gnrmkthresource is used to create the :ref:`th` resources automatically from :ref:`packages_model`
    
    * the first parameter is a :ref:`table` name; use the following syntax::
    
        package_name.table_name
        
    where:
    
    * ``package_name`` is the name of the :ref:`package <packages>`
      and may be in the form::
      
        project_name:package_name
        
    * ``table_name`` is the name of your :ref:`database table <table>`
    
    **Optional suffixes:**
    
    CLIPBOARD::
    
        "-f", "--force", dest="force", action='store_true', default=False,
        help="force the resource creation also if destination file exists"
        "-n", "--name", dest="name", 
        help="output file name, the file will be, will work only if single table is passed"
        
        "-o", "--output", dest="output",
        help="""output file path will override -n/--name and automatic file placement in resources/tables/tablename, 
                will work only if single table is passed"""
        "-i", "--indent", dest="indent", default=4,
         help="output file name, the file will be, will work only if single table is passed"
         
    **Examples**
    
        add???::
        
            MyBook:packages niso$ cd packageName
            packageName niso$ gnrmkthresource packageName.modelName -n th_modelName
    