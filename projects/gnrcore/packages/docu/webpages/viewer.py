# -*- coding: UTF-8 -*-
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self,root,**kwargs):
        root.attributes.update(overflow='hidden')
        language = self.locale.split('-')[0]
        doctable = self.db.table('docu.documentation')
        record = doctable.record(hierarchical_name='/'.join(self._call_args)).output('record')
        docbag = Bag(record['docbag'])
        rst = docbag['%s.rst' %language] or docbag['en.rst'] or docbag['it.rst'] or 'To do...'
        rsttable = doctable.dfAsRstTable(record['id'])
        if rsttable:
            rst = '%s\n\n%s' %(rst,rsttable) 
        contentHtml = self.site.getService('rst2html')(rst)
        bc = root.borderContainer(datapath='main')
        pane = bc.contentPane(region='right',width='50%',splitter=True,
                                  overflow='hidden',
                                  border_left='1px solid #3A4D65')
        self.rstText(bc.contentPane(region='center',overflow='hidden'),contentHtml=contentHtml)
        bc.dataController("bc.setRegionVisible('right',localIframeUrl!=null)",
                bc=bc.js_widget,localIframeUrl='^.localIframeUrl',_onBuilt=True)
        pane.data('.record',record)
        pane.dataFormula('.localIframeUrl','sourcebag.len()==1?sourcebag.getItem("_base_.url"):null',
                    sourcebag='^.record.sourcebag')
        pane.dataController("""
                        var l = url.split(':');
                        var urlToSet;
                        if(l[0]=='version'){
                            var versionRow = data.getItem(l[1]);
                            if(versionRow){
                                urlToSet = versionRow.getItem('url');
                            }else{
                                urlToSet = null;
                            }

                        }else{
                            urlToSet = l[1];
                        }
                        SET .localIframeUrl = urlToSet;
                        """,
                        subscribe_setInLocalIframe=True,
                        data='=.record.sourcebag')
        pane.iframe(src='^.localIframeUrl',src__source_viewer=True,height='100%',width='100%',border=0)

    def rstText(self,pane,contentHtml=None):
        iframe = pane.div(_class='scroll-wrapper').htmliframe(height='100%',width='100%',border=0)
        js_script_url = self.site.getStaticUrl('rsrc:common','localiframe.js',nocache=True)
        pane.dataController("""
            var cw = iframe.contentWindow;
            var s = cw.document.createElement("script");
            s.type = "text/javascript";
            s.src = '%s';
            cw.document.getElementsByTagName("head")[0].appendChild(s);
            var cw_body = cw.document.body;
            if(genro.isMobile){
                cw_body.classList.add('touchDevice');
            }
            cw_body.classList.add('bodySize_'+genro.deviceScreenSize);
            cw_body.innerHTML = contentHtml;
            """ %js_script_url,iframe=iframe.js_domNode,contentHtml=contentHtml,_onStart=True)
