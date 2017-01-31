#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrbag import Bag

try:
    import pandas as pd 
    import numpy as np
except:
    pd = False
    np = False

class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.parent = parent

    def dataframe(self,data=None):
        df = pd.DataFrame(data) 
        return df

    def saveDataframe(self,df,path):
        df.to_pickle(self.parent.getStaticPath(path,autocreate=-1))

    def loadDataframe(self,path):
        df = pd.read_pickle(self.parent.getStaticPath(path,autocreate=-1))
        return df

    def dataframeInfo(self,df):
        result = Bag()
        result.setItem('values',Bag(),caption='Values')
        for col in df.columns:
            colelem = df[col]
            if pd.types.common.is_numeric_dtype(colelem):
                result.setItem('values.%s' %col,None,caption=col)
            elif pd.types.common.is_datetimelike(colelem): #alternativa pd.types.common.is_datetime64_dtype(colelem):
                continue
                #years = Bag()
                #result.setItem(col,years,caption=col)
                #for y in colelem.dt.year.unique():
                #    months = Bag()
                #    result.setItem(str(y),months,caption=y)
                #    for m in colelem.dt.to_period('m').unique():
                #        months.setItem(str(m),None,caption=str(m))
            else:
                for i,e in enumerate(colelem.unique()):
                    if e:
                        result.setItem('%s.r_%s' %(col,i),None,caption=e)
        return result




