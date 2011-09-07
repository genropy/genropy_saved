from gnr.core.gnrbag import Bag
b=Bag('/Users/fporcari/sviluppo/genro/resources/common/css_icons/retina/gray/16')
pars={}
r=[]
s = 16
pars['size']=s
pars['height']=s+2
pars['width']=s+6
r.append("/* @group size%(size)s */"%pars)
r.append("""
.iconbox{
	height:18px;
	width: 22px;
	cursor: pointer;
	border-radius:2px;
	background-color:#ddd !important;
	margin-top:1px;
	margin-bottom:1px;
	border:1px solid silver;
}
.slotbar_toolbar .dijitButtonHover .iconbox, .slotbar_toolbar .iconbox:hover{
	background-color:#bbb !important;	
}""" %pars)
r.append("")
for name in b['#0'].digest('#a.file_name'):
    pars['name']=name
    r.append("""
.%(name)s{
	background: url(%(size)s/%(name)s.png) no-repeat center center;
}"""%pars)
r.append("/* @end */\n\n")

print '\n'.join(r)