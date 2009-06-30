#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
import time

from processing import Process

from popen2 import popen2

from gnr.web.gnrwebpage import GnrWebPage

class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=1)
        fb.button('DO', fire='^do')
        fb.button('DO TEST', fire='^dotest')
        
        fb.dataRpc('result', 'Test',  pdfmode='^dotest', _POST=True)
        fb.dataRpc('result', 'processTest',  pdfmode='^do', _POST=True)
        fb.dataController("alert(result);", result='^result')
        self.thermoDialog(root, thermoid='build_pdf', title='Generazione PDF', thermolines=2, fired='^do')

    def rpc_processTest(self, **kwargs):
        self.app.setThermo('build_pdf', 0, 'Preparo elaborazione' , 10, command='init')
        p = Process(target=self.testOtherProcess, args=(self.pageLocalDocument('testOtherProcess'),), name='pippo')
        p.start()
        #p.join()
        #return p.getExitCode()
        
    def rpc_Test(self, **kwargs):
        self.testOtherProcess(self.pageLocalDocument('testOtherProcess'))
        return 'ok'
        
    def testOtherProcess(self, fpath, **kwargs):
        n = 10
        for x in xrange(n):
            self.app.setThermo('build_pdf', x, 'Elaboro')
            time.sleep(1)
            fname = '%s.%s' % (fpath, str(time.time()))
            f = open(fname, 'w')
            f.write('ciao')
            f.close()
        self.app.setThermo('build_pdf', command='end')
        popen2('lpr %s' % fname)

        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

