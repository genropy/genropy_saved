Logging in GenroPy
==================

**NOTA:** questa funzione è in fase d'implementazione.

Logging in Python
*****************

Per scrivere nel log, importare il modulo :mod:`logging`::

    import logging

Ottenere il logger che interessa::

    log = logging.getLogger('gnr.core.gnrdate') # siamo nel modulo gnrdate
    log.warn('messaggio')


Configurazione in envinronment, site_config o instance_config
*************************************************************

Formato::

    <logging>
        <logger name="" level="NOTSET" handler="stdlog" />
        <logger name="paste" level="WARN" handler="stdlog" />

        <logger name="gnr" level="NOTSET" handler="stdlog">
            <logger name="core.gnrdate" level="DEBUG">
            </logger>
        </logger>

        <formatter name="fmt" format="(asctime)s - %(levelname)s - %(message)s" />
        <handler name="stdlog" class="ConsoleLogger" colorize="True" formatter="fmt"/>
    </logging>