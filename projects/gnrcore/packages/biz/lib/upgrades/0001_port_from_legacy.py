# encoding: utf-8

def main(db):
    print 'biz 0001 port from legacy ',db.dbname
    sql = """
        INSERT INTO biz.biz_dashboard (dashboard_key,pkgid,code,description,widget,data)
        (SELECT dashboard_key,pkgid,code,description,widget,data
        FROM adm.adm_dashboard
        WHERE dashboard_key IS NOT NULL) ;
    """
    db.execute(sql)
