from gnr.services import GnrBaseServiceType
from gnr.core.gnrbag import Bag

class SysServiceType(GnrBaseServiceType):
    def getConfiguration(self,service_name):
        service_record = self.site.db.table('sys.service').record(service_type=self.service_type,
                                                            service_name=service_name,ignoreMissing=True).output('dict')
        if not service_record:
            return super(SysServiceType,self).getConfiguration(service_name)
        conf =  Bag(service_record['parameters'])
        conf['implementation'] = service_record['implementation']
        return conf.asDict()
    
    def configurations(self):
        l = super(SysServiceType,self).configurations()
        dbservices = self.site.db.table('sys.service').query(where='$service_type=:st',st=self.service_type).fetch()
        l += [dict(implementation=r['implementation'],service_name=r['service_name'],service_type=r['service_type']) for r in dbservices]
        return l

BaseServiceType = SysServiceType