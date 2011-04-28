# -*- coding: UTF-8 -*-
# 
"""base_chart"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'

    def test_1_basic(self, pane):
        """Basic button"""
        mychart = pane.chart()
        mychart.plot("default", plot_type="Areas")
        mychart.plot("default", plot_type="StackedAreas", plot_lines=True, plot_areas=True, plot_markers=False);
        mychart.plot("default", plot_type="StackedLines", plot_tension="S", plot_shadows_dx=2, plot_shadows_dy=2);
        mychart.plot("default", plot_type="Bars", plot_gap=5, plot_minBarSize=3, plot_maxBarSize=20);
  
             