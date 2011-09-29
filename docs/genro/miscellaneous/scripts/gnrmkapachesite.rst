.. _gnrmkapachesite:

===============
gnrmkapachesite
===============

    *Last page update*: |today|
    
    add???
    
    CLIPBOARD::
    
        gnrmkapache will output an apache site configuration file.
        example usage:
        gnrmkapachesite genro www.genro.org > genro_site
        will write the correct apache configuration for 'genro' site in genro_site
        then copy genro_site to /etc/apache2/sites-available:
        sudo cp genro_site /etc/apache2/sites-available
        then enable it:
        sudo a2ensite genro_site
        and finally restart apache:
        sudo apache2ctl restart