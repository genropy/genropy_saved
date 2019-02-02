#!/usr/bin/env python
# encoding: utf-8

from builtins import object
from gnrpkg.adm.decorators import checklist

class Table(object):
   @checklist(name='Import dati')
   def verifica_caricamento_dati(self):
       """Verifica importazione dati: vai nelle preferenze di glbl"""