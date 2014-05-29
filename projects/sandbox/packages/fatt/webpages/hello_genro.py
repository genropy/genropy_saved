# -*- coding: UTF-8 -*-
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    def main_root(self,root,**kwargs):
        root.div('hello genro')
        box = root.div(datapath='test',position='relative',height='100%',
                        connect_onclick=""" var stopped = $1.target.sourceNode.getRelativeData(".stopped");
                                            var status = !stopped || false;
                                            $1.target.sourceNode.setRelativeData(".stopped",status);
                                            $1.target.sourceNode.setRelativeData(".color",status?'red':'black');
                                            """)

        for prov in self.db.table('glbl.provincia').query().fetch():
            r = Bag(dict(prov))
            box.data('.%s' %prov['sigla'],r)
            provincia_box = box.div(datapath='.%s' %prov['sigla'],border='1px solid silver',
                                    padding='10px',position='absolute',top='^.top',
                                    left='^.left' ,rounded='^.rounded',font_size='^.font_size',
                                    transition='1s all linear',cursor='pointer')
            provincia_box.span('^.nome',color='^.color')
            provincia_box.dataController("""if(stopped){
                    return;
                }
                SET .left = Math.floor(Math.random()*1000)+'px';
                SET .top = Math.floor(Math.random()*1000)+'px';
                SET .font_size = 10+Math.floor(Math.random()*10)+'px';
                SET .rounded = Math.floor(Math.random()*15);
                                """,_timing=2,stopped='^.stopped')

