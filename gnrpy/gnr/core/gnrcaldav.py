from datetime import datetime
import caldav
from caldav.elements import dav, cdav
from gnr.core.gnrbag import Bag,VObjectBag
from gnr.core.gnrlang import getUuid
def test():
    return CalDavConnection(user='giovanni.porcari@softwell.it',password='toporaton',host='p04-caldav.icloud.com',root='/9403090/calendars/')
def test1():
    return CalDavConnection(user='gpo@localhost',password='',host='localhost',port=5232,root='/gpo/calendard',protocol='http')
    
def testcal():
    s=test()
    personale=s.calendars['Personale']
    events= personale.events()
    e0=events[0]
    e0.load()
    data=e0.data
    return data
def dt(dt):
    if isinstance(dt,datetime):
        return dt.strftime('%Y%m%dT%H%M%SZ')
    return dt
class CalDavConnection(object):
    def __init__(self,host=None,user=None,password=None,root=None,port=443,protocol='https'):
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.root=root or '/'
        self.protocol=protocol
        self.url='%s://%s:%s@%s:%s%s' %(self.protocol,self.user,self.password,self.host,self.port,self.root)
        
    @property
    def client(self):
        if not hasattr(self,'_client'):
            self._client=caldav.DAVClient(self.url)
        return self._client
        
    @property
    def principal(self):
        if not hasattr(self,'_principal'):
            self._principal=caldav.Principal(self.client, self.url)
        return self._principal
        
    @property
    def calendars(self):
        if not hasattr(self,'_calendars'):
            calendars=self.principal.calendars()
            self._calendars={}
            for calendar in calendars:
                p=calendar.get_properties([dav.DisplayName(),])
                if p:
                    calname=p[dav.DisplayName().tag]
                    self._calendars[calname]=calendar
        return self._calendars
        
    def createEvent(self,uid=None,dtstamp=None,dtstart=None,dtend=None,summary=None,calendar=None):
        tpl = """BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:%(prodid)s\r\nBEGIN:VEVENT\r\nUID:%(uid)s\r\nDTSTAMP:%(dtstamp)s\r\nDTSTART:%(dtstart)s\r\nDTEND:%(dtend)s\r\nSUMMARY:%(summary)s\r\nEND:VEVENT\r\nEND:VCALENDAR"""
        calendar=self.calendars.get(calendar)
        assert calendar, 'Missing calendar'
        data=tpl%dict(uid=uid or getUuid(),dtstamp=dt(dtstamp or datetime.now()),dtstart=dt(dtstart),dtend=dt(dtend),summary=summary,prodid='VCALENDAR genropy')
        event = caldav.Event(self.client, data = data, parent = calendar).save()
    def eventsBag(self,calendarName):
        result=Bag()
        calendar=self.calendars.get(calendarName)
        if calendar:
            events=calendar.events()
            for event in events:
                event.load()
                data=VObjectBag(event.data)
                result.addItem('evento',data)
        return result
        
            



if __name__=='__main__':
    #data=testcal()
    #calbag=VObjectBag(data)
    #print calbag
    #c=CalDavConnection(user='giovanni.porcari@softwell.it',password='toporaton',host='p04-caldav.icloud.com',root='/9403090/calendars/')
    #c.createEvent(summary='Esempio di evento creato da genropy',dtstart='20121005T102000Z',dtend='20121005T122000Z',calendar='Personale')
    #b=VObjectBag('/Users/gpo/Desktop/vcard_test.vcf')
    #print b
    c=test1()
    calendars=c.principal.calendars()
    c0= calendars[0]
    print c0._get_properties([dav.DisplayName(),])
    print ss
    c.calendar.get_properties([dav.DisplayName(),])
    print c.calendars
   
    b=c.eventsBag('Promemoria')
    #print b
    for event in b.values():
        s=event['#0'].digest('#v',condition=lambda n: n.attr.get('vtag') in ('VTODO','VEVENT'))
    for event in s:
        print event
    
