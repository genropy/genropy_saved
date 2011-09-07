from gnr.core.gnrbag import Bag
b=Bag('/Users/fporcari/sviluppo/genro/resources/common/css_icons/retina/gray/16')
pars={}
r=[]
pars['size']=16
r.append("/* @group size%(size)s */"%pars)
r.append("""
.iconbox{
	height:16px;
	width: 18px;
	opacity:1;
	cursor: pointer;
	padding:2px;
}
.dijitButtonHover .iconbox, .iconbox:hover{
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