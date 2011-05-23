.. _packages_main:

===========
``main.py``
===========

    .. image:: ../../images/projects/packages_main.png
    
    ::
    
        #!/usr/bin/env python
        # encoding: utf-8
        from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
        
        class Package(GnrDboPackage):
            def config_attributes(self):
                return dict(comment='agenda package',sqlschema='agenda',
                            name_short='Agenda', name_long='Agenda', name_full='Agenda')
                            
            def config_db(self, pkg):
                pass
                
            def loginUrl(self):
                return 'agenda/login'
                
        class Table(GnrDboTable):
            pass