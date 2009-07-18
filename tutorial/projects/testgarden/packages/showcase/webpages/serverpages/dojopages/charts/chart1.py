#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrhtmlpage import GnrHtmlDojoPage as page_factory


class GnrCustomWebPage(object):
    dojoversion='13'
    theme='soria'

    def main(self, body, name='World'):

        bc=body.borderContainer(height='500px',width='600px',margin='10px',background_color='red')
        bc.contentPane(region='top',height='5ex',splitter='true',background_color='lime')
        bc.contentPane(region='left',width='15em',splitter='true',background_color='gray')
        pane=bc.contentPane(region='center',padding='5px')
        pane.div(id="mychart", width='100%' , height='100%')
        pane.div( id="mychart_legend")
        pane.script(self.chartScript(chartId='mychart'))
        #pane.script("dojo.addOnLoad('makeChart')")
        pane.script("""dojo.addOnLoad('function(){alert("PPPP")};')""")
    def chartScript(self,plots=None,**kwargs):
        script="""
            dojo.require("dojox.charting.widget.Chart2D");
            var makeChart = function(){
                    alert('making chart')
                    var chart = new dojox.charting.Chart2D("%(chartId)s");
                    chart.addPlot("bmi" ,{type: "Lines",markers:true,shadows:{dx: 3, dy: 3, dw: 3},color:"#003366"});
                    chart.addPlot("weight", {type: "Lines",markers:true,shadows: {dx: 3, dy: 3, dw: 3}});
                    chart.addPlot("min_warning_bmi", {type: "Lines"});
                    chart.addPlot("max_warning_bmi", {type: "Lines"});

                    chart.addAxis("x", {labels:${x_labels},from:${start_pos},to:${end_pos}});
                    chart.addAxis("y", {vertical: true,from:5,to:150});
                    var bmi = ${bmi_series};
                    var weight = ${weight_series};
                    chart.addSeries("BMI", bmi,{plot: "bmi", stroke: {color:"darkgreen"}});
                    chart.addSeries("Min. Warning BMI", [{x:${start_pos} , y:20}, {x:${end_pos}, y: 20}],
                                    {plot: "min_warning_bmi", stroke: {color:"red"}});
                    chart.addSeries("Max Warning BMI", [{x:${start_pos} , y:35}, {x:${end_pos}, y: 35}],
                                    {plot: "max_warning_bmi", stroke: {color:"red"}});

                    chart.addSeries("Weight", weight,
                            {plot: "weight", stroke: {color:"darkblue"}});

                    chart.render();
                    var legend = new dojox.charting.widget.Legend({chart: chart}, "legend");
        """ % kwargs
        return script


