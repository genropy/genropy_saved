#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent
import json
class componentsGrafico(BaseComponent):
    def plotGrafico(self, center, **kwargs): 
        dati_da_graficare = json.loads(kwargs['dati_da_graficare']) if kwargs.get('dati_da_graficare', False) else []

        labels = []
        for label in json.loads(kwargs['labels']) if kwargs.get('labels', False) else []:
            labels.append(str(label))
    
        elenco_parametri = []

        if dati_da_graficare == [] and labels == []:
            elenco_parametri = json.loads(kwargs['elenco_parametri'].replace('__#a','à').replace('__#e','è').replace('__#i','ì').replace('__#o','ò').replace('__#u','ù'))

        self.builder.head.style("""
            body,html{
                height:100%;
                margin:0;
            }
        """+"::HTML", type="text/css")
        center.div(id='chart', style='width:95%;height:90%;')
    
        center.div(id='legenda')

        center.script("""
              var dati_da_graficare = %(dati_da_graficare)s;
              var labels = %(labels)s;

              dynamicFormHandler.plotGraficoDojo(dati_da_graficare, labels);

        """% {'dati_da_graficare':dati_da_graficare, 'labels':labels})



