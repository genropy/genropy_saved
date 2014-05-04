#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import shutil
import sys

EXCLUDED_EXTS = ['.pyc', '.pyo', '.php', '.jar']

INCLUDED_PATHS = [
 'dojo_libs/dojo_11/dojo',
 'gnrjs',
 'gnrpy',
 'LICENSE',
 'projects/gnr_it',
 'projects/gnrcore',
 'README.rst',
 'resources/common',
 'resources/js_libs/ckeditor',
 'scripts',
 'webtools'
 ]


EXCLUDED_PATHS = [
'resources/js_libs/ckeditor/_samples',
'resources/js_libs/ckeditor/_source',
'gnrpy/gnrpy.egg-info',
'gnrpy/unused',
'gnrpy/gnr/core/build',
'gnrpy/gnr/xtnd',
'gnrpy/gnr/pdf',
'gnrpy/gnr/devel',
#'gnrpy/gnr/utils',
'projects/gnrcore/packages/website',
'projects/gnrcore/packages/uke',
'projects/gnrcore/packages/qfrm',
'projects/gnrcore/packages/gnrdevel',
]

def mkdirhier(dirpath=None):
	splitted_path = dirpath.split(os.path.sep)[1:]
	current = dirpath[:3] if sys.platform == 'win32' else dirpath[0]
	for directory in splitted_path:
		
		current = os.path.join(current, directory)
		if not os.path.exists(current):
			os.mkdir(current)


def do_clean_export(genropy_path = None):
	def make_relative_filename(in_file=None):
		return in_file.replace(genropy_path, '')[1:]
	out_path = os.path.join(os.path.dirname(genropy_path),'genropy_clean')
	if os.path.exists(out_path):
		print 'Deleting previous export'
		shutil.rmtree(out_path)
	os.mkdir(out_path)
	def make_out_file_path(*args):
		return os.path.join(out_path,*args)
	walk_gen = os.walk(genropy_path)
	included_paths = [os.path.join(genropy_path, *(p.split('/'))) for p in INCLUDED_PATHS]
	def is_included(path):
		for included_path in included_paths:
			dirpath = path
			while len(dirpath)>1:
				if dirpath==included_path:
					return True
				dirpath = os.path.dirname(dirpath)

	excluded_paths = [os.path.join(genropy_path, *(p.split('/'))) for p in EXCLUDED_PATHS]
	for dirpath, dirnames, filenames in walk_gen:

		for dirname in list(dirnames):
			if os.path.join(dirpath,dirname) in excluded_paths:
				print 'Will skip: ',dirname
				dirnames.pop(dirnames.index(dirname))
		if os.path.basename(dirpath)[0] not in ('.') and is_included(dirpath):
			out_dir = make_out_file_path(make_relative_filename(dirpath))
			mkdirhier(out_dir)
			#print 'Copying included path: %s to %s'%(dirpath, out_dir) 
			for filename in filenames:
				if os.path.splitext(filename)[-1].lower() not in EXCLUDED_EXTS and not filename[0]=='.':
					out_file_path = os.path.join(out_dir, filename)
					in_file_path = os.path.join(dirpath, filename)
					shutil.copy2(in_file_path, out_file_path)
			


if __name__ == '__main__':
	do_clean_export(genropy_path = os.getcwd())