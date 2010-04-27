#-*- coding: UTF-8 -*-

from gnr.web.gnrhtmlpage import GnrHtmlPage as page_factory


class GnrCustomWebPage(object):
    #theme = ''
    def main(self, body):
        self.page_head(self.builder.head)
        self.page_body(self.builder.body)

    def page_head(self,head):
        head.meta(content="text/html; charset=UTF-8")
        head.meta(http_equiv="Content-Language" ,content="it")
        head.meta(name="OWNER",content="Centro medico Euriclea")
        head.meta(name="AUTHOR", content="Paolo Camera,Matteo Gaiani")
        head.meta(name="Description", content="GenroMed software")
        head.meta(name="keywords", content="software, gestionale, medico")
        head.title('GenroMed')
        head.style('@import "%s";'%self.getResourceUri('genromed.css'),type="text/css")

    def page_body(self,body):
        container = body.div(id='container')
        self.page_header(container.div(id='header'))
        self.page_content(container.div(id='content'))
        self.page_footer(container.div(id='footer'))

    def page_header(self,content):
        content.div('titolo')
        content.div('subtitolo',id='subtitolo')

    def page_content(self,content):
        """
        Un <b>wiki</b> è un <a href="http://ffffdf">sito Web</a> (o comunque una collezione di <a href="http://www.apppld.com">documenti ipertestuali</a>
        che viene aggiornato dai suoi utilizzatori e i cui contenuti sono sviluppati in <a href="http://ffkdlfkdlfd.com">collaborazione </a>
        da tutti coloro che vi hanno accesso. <b>La modifica</b> dei contenuti è aperta, nel senso che il testo può essere modificato da tutti gli utenti (a volte soltanto se registrati, altre volte anche anonimi) procedendo non solo per aggiunte, ma anche cambiando e cancellando ciò che hanno scritto gli autori precedenti.
        Ogni modifica è registrata in una cronologia che permette in caso di necessità di riportare il testo alla versione precedente; lo scopo è quello di condividere, scambiare, immagazzinare e ottimizzare la conoscenza in modo collaborativo. Il termine wiki indica anche il
        <a href="eeek.ddddk..ffff">software collaborativo</a> utilizzato <a href="www.dddo.ccom"> etimologia</a> per creare il sito web e il server.<br/>
        Wiki, in base alla sua <a href="www.dddo.ccom"> etimologia</a>, è anche un modo di essere."""
        
        div1 = content.div(_class="para")
        div1.span("Un ")
        div1.b("wiki")
        div1.span(u"è un ")
        div1.a("sito Web", href='http://ffffdf')
        div1.span(" (o comunque una collezione di ")
        div1.a("documenti ipertestuali", href='http://www.apppld.com')
        div1.span(" che viene aggiornato dai suoi utilizzatori e i cui contenuti sono sviluppati in ")
        div1.a('collaborazione ', href='http://ffkdlfkdlfd.com')
        div1.span(""" da tutti coloro che vi hanno accesso. """)
        div1.b("La modifica")
        div1.span(""" dei contenuti è aperta, nel senso che il testo può essere modificato da tutti gli utenti (a volte soltanto se registrati, altre volte anche anonimi) procedendo non solo per aggiunte, ma anche cambiando e cancellando ciò che hanno scritto gli autori precedenti.
        Ogni modifica è registrata in una cronologia che permette in caso di necessità di riportare il testo alla versione precedente; lo scopo è quello di condividere, scambiare, immagazzinare e ottimizzare la conoscenza in modo collaborativo. Il termine wiki indica anche il""")
        div1.a('software collaborativo', href='eeek.ddddk..ffff')
        div1.span('utilizzato ')
        div1.a(" etimologia", href='www.dddo.ccom')
        div1.span('per creare il sito web e il server.')
        div1.br()
        div1.span("Wiki, in base alla sua")
        div1.a(" etimologia", href='www.dddo.ccom')
        div1.span(", è anche un modo di essere.")
        
    def page_footer(self,content):
        content.a('Softwell',href='www.softwell.it')
        # tag 'a' non funzionava, ho modificato core/gnrhtml.py aggiungendo 'a' in lista html_autocontent_NS
        content.span('Tutti i diritti riversati nel fiume.')