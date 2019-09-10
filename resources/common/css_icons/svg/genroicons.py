from gnr.core.gnrbag import Bag
import os
import shutil

fpath = '/Users/fporcari/sviluppo/genro/resources/common/css_icons/svg'

for f in os.listdir(fpath):
	oldpath = os.path.join(fpath,f)
	if '16' in f:
		newpath = os.path.join(fpath,'16',f.replace('_16x16','').lower())
		if not os.path.isdir(oldpath):
			shutil.move(oldpath,newpath)

for s in (16,):
	b=Bag(os.path.join(fpath,str(s)))
	pars={}
	r=[]
	pars['size']=s
	pars['height']=s+2
	pars['width']=s+6
	r.append("/* @group size%(size)s */"%pars)
	for name in b['#0'].digest('#a.file_name'):
		pars['name']=name
		r.append("""
	.%(name)s{
		background: url(%(size)s/%(name)s.svg) no-repeat center center;
	}"""%pars)
	r.append("/* @end */\n\n")
	print '\n'.join(r)