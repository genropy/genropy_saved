=========================================================================================
:mod:`gnr.core.gnrhtml` -- Server-side HTML generations (web pages and printable reports)
=========================================================================================

	.. module:: gnr.core.gnrbag

	Usually in GenroPy the pages are built on the client side: the page structure is transfered as a :class:`Bag`; after that, the Genro's Javascript tools take care to build the DOM and all the necessary :ref:`genro_widgets`. So, you have the complete control of the page, and you can modify the page itself simply modifying the ``Bag`` that constructs the page.

	You can build the page completely server side. It is useful to index pages for search engines and, above all, to make the :ref:`???ref for the print!`

	In a server side page you can use all the Dojo widgets, but without Genro additions and without Genro extensions (e.g. the :ref:`genro_dbselect` doesn't work)

.. automodule:: gnr.core.gnrhtml
	:members: