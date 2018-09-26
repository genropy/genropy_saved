from gnr.core.services import GnrBaseServiceType

class SysBaseServiceType(GnrBaseServiceType):
    def __init__(self, site):
        self.site = site
        self.instances = {}

    def add(self, service_name=None):
        instance_config = self.getConfiguration(service_name)
        self.instances[service_name] = instance
        #service_name = service_name or self.service_name(service_handler_factory)
        #service_handler = service_handler_factory(self.site, **kwargs)
        #service_handler.service_name = service_name
        #self.services.setItem(service_name, service_handler, **kwargs)
        #return service_handler

    def getConfiguration(self,service_name):
        conf = self.site.config.getAttr('services.%s' %service_name)


    def get(self, service_type=None,service_name=None):
        service = self.services[service_name]
        if service is None:
            if ':' in service_name:
                service_name, resource = service_name.split(':')
            else:
                resource = service_name
            service_handler_factory = self.importServiceClass(service_type=service_name,resource=resource)
            if service_handler_factory:
                service = self.add(service_handler_factory,service_name=service_name)
        return service