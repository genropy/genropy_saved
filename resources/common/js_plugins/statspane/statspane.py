# -*- coding: UTF-8 -*-

# chartmanager.py
# Created by Francesco Porcari on 2017-01-01.
# Copyright (c) 2017 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
#from gnr.core.gnrdecorator import public_method
#from gnr.core.gnrbag import Bag,AnalyzingBag
#import os

class StatsPane(BaseComponent):
    py_requires='js_plugins/chartjs/chartjs:ChartPane'
    js_requires='js_plugins/stats/stats'
    css_requires='js_plugins/stats/stats'



    #def stats_get_selection(self, selectionName,extra_columns=None):
    #    if extra_columns:
    #        cust_selectionName = '%s_cust' % selectionName
    #        if not os.path.exists(self.pageLocalDocument(cust_selectionName)):
    #            return self.stats_create_custom_selection(selectionName, cust_selectionName,extra_columns=extra_columns)
    #        else:
    #            selectionName = cust_selectionName
    #    return self.unfreezeSelection(self.tblobj, selectionName)

    #def stats_create_custom_selection(self, selectionName, cust_selectionName,extra_columns=None):
    #    pkeys = self.unfreezeSelection(self.tblobj, selectionName).output('pkeylist')
    #    query = self.tblobj.query(columns=extra_columns,
    #                              where='t0.%s IN :pkeys' % self.tblobj.pkey,
    #                              pkeys=pkeys, addPkeyColumn=True,excludeDraft=False,ignorePartition=True)
    #    return query.selection()



    #@public_method
    #def stats_totalize(self, selectionName=None, group_by=None, sum_cols=None, keep_cols=None,
    #                       collect_cols=None, distinct_cols=None, key_col=None, captionCb=None,
    #                       tot_mode=None,extra_columns=None, **kwargs):
    #    print 'totalizing'
    #    selection = self.stats_get_selection(selectionName,extra_columns=extra_columns)
    #    analyzer = AnalyzingBag()
    #    self.btc.batch_create(batch_id='%s_%s' % (selectionName, self.getUuid()),
    #                          title='Stats',
    #                          delay=.8,
    #                          note='Stats',userBatch=False)
    #    group_by = group_by or self.stats_group_by(tot_mode)
    #    sum_cols = sum_cols or self.stats_sum_cols(tot_mode)
    #    keep_cols = keep_cols or self.stats_keep_cols(tot_mode)
    #    collect_cols = collect_cols or self.stats_collect_cols(tot_mode)
    #    distinct_cols = distinct_cols or self.stats_distinct_cols(tot_mode)
    #    key_col = key_col or self.stats_key_col(tot_mode)
    #    captionCb = captionCb or self.stats_captionCb(tot_mode)
    #    if isinstance(group_by, basestring):
    #        group_by = group_by.split(',')
    #    if isinstance(sum_cols, basestring):
    #        sum_cols = sum_cols.split(',')
    #    if isinstance(keep_cols, basestring):
    #        keep_cols = keep_cols.split(',')
    #    if isinstance(collect_cols, basestring):
    #        collect_cols = collect_cols.split(',')
    #    if isinstance(distinct_cols, basestring):
    #        distinct_cols = distinct_cols.split(',')

    #    def date_converter(mode):
    #        datefield, formatmode = mode.split(':')
    #        return lambda r: toText(r[datefield], format=formatmode, locale=self.locale)
    #        
    #    for k, x in enumerate(group_by):
    #        if isinstance(x, basestring):
    #            if x.startswith('#DATE='):
    #                group_by[k] = date_converter(x[6:])
    #            else:
    #                group_by[k] = x.replace('@', '_').replace('.', '_')
    #    if keep_cols:
    #        keep_cols = [x.replace('@', '_').replace('.', '_') for x in keep_cols]
    #    if distinct_cols:
    #        distinct_cols = [x.replace('@', '_').replace('.', '_') for x in distinct_cols]
    #    result = Bag()
    #    analyzer.analyze(selection,group_by=group_by, sum=sum_cols, keep=keep_cols,
    #                        collect=collect_cols, distinct=distinct_cols,
    #                        key=key_col, captionCb=captionCb)
    #    selection.analyzeBag = analyzer
    #    self.freezeSelection(selection, selectionName)
    #    result.setItem('data', analyzer, caption=self.stats_modes_dict()[tot_mode])
    #    return result