from gnr.core.gnrbag import Bag
b=Bag('/Users/fporcari/sviluppo/genro/resources/common/css_icons/retina/gray/16')
pars={}
r=[]
for size in ('16','24','48','64'):
    pars['size']=size
    r.append("/* @group size%(size)s */"%pars)
    r.append("""
.icon_%(size)s,.slotBar_%(size)s .iconbox{
	height:%(size)spx;
	width: %(size)spx;
	opacity: .7;
	cursor: pointer;
}
.slotBar_%(size)s .dijitButtonHover .iconbox , .dijitButtonHover .icon_%(size)s, .icon_%(size)s:hover{
    opacity:1;
}""" %pars)
    r.append("")
    for name in b['#0'].digest('#a.file_name'):
        pars['name']=name
        r.append("""
.%(name)s_%(size)s, .slotBar_%(size)s .%(name)s{
	background: url(%(size)s/%(name)s.png) no-repeat center center;
}"""%pars)
    r.append("/* @end */\n\n")

print '\n'.join(r)