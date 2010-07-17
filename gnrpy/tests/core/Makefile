COVER_OPTS=--cover-report=html

tests:
	py.test *.py $(COVER_OPTS) --cover=gnr.core

bag:
	py.test gnrbag_test.py $(COVER_OPTS) --cover=gnr.core.gnrbag --cover=gnr.core.gnrbagxml

date:
	py.test	gnrdate_test.py $(COVER_OPTS) --cover=gnr.core.gnrdate

string:
	py.test gnrstring_test.py $(COVER_OPTS) --cover=gnr.core.gnrstring

locale:
	py.test locale_test.py $(COVER_OPTS) --cover=gnr.core.gnrlocale

resolver:
	py.test resolver_test.py $(COVER_OPTS) --cover=gnr.core
