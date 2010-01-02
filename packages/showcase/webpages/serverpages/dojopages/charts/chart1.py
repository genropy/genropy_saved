#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrhtmlpage import GnrHtmlDojoPage as page_factory


class GnrCustomWebPage(object):
    dojoversion='13'
    theme='soria'

    def main(self, body, name='World'):
        body.script("""var makeChart=function(){
                            dojo.require("dojox.charting.widget.Chart2D");
                            var chart = new dojox.charting.Chart2D("mychart");
                            chart.addPlot("bmi" ,{type: "Lines",markers:true,shadows:{dx: 3, dy: 3, dw: 1},color:"#003366"});
                            chart.addSeries("BMI", [40,50,70,60,60,80,70],{plot: "bmi", stroke: {color:"pink"}});
                            chart.render();
                            };
                       dojo.addOnLoad(makeChart);""")
        bc=body.borderContainer(height='500px',width='600px',margin='10px',background_color='red')
        bc.contentPane(region='top',height='5ex',splitter='true',background_color='lime')
        bc.contentPane(region='left',width='15em',splitter='true',background_color='gray')
        pane=bc.contentPane(region='center',padding='5px')
        pane.div(id="mychart", width='100%' , height='100%')
        pane.div( id="mychart_legend")




