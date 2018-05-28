# encoding: utf-8
def config(root,application=None):
    biz = root.branch(u"!!Business intelligence")
    biz.thpage(u"!!Dashboards management", table="biz.dashboard",tags="admin")
    biz.branch('!!All dashboards',dashboard=True)
