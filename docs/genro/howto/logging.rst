====================
 Logging in GenroPy
====================

**NOTA:** This function is being implemented, it is not yet available but it will be available soon.

Logging in Python
*****************

To write in the log, you have to import the :mod:`logging` module::

    import logging

And obtain the logger you're interesed in::

    log = logging.getLogger('gnr.core.gnrdate') # we're in gnr.core.gnrdate
    log.warn('messaggio')


Configuring logging in GenroPy
******************************

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
