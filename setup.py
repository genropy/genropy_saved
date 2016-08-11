from setuptools import find_packages, setup



setup(
    name='Genropy',
    version='3.14159', # will increment Pi precision in every release :)
    url='http://www.genropy.org/',
    author='Genropy',
    author_email='info@genropy.org',
    description=('An insanely fast way to create Single Page Applications in python'),
    license='LGPL',
    packages=find_packages('gnrpy'),
    package_dir = {'':'gnrpy'},
    include_package_data=True,
    scripts=['scripts/gnrdbsetup', 'scripts/gnrmkinstance', 'scripts/gnrmkthresource','scripts/gnrmksite','scripts/gnrxml2py', 'scripts/gnrheartbeat', 'scripts/gnrmkpackage',
                 'scripts/gnrwsgiserve','scripts/gnruwsgiserve', 'scripts/gnrmkapachesite','scripts/gnrdaemon', 'scripts/gnrsql2py',
                 'scripts/gnrsendmail', 'scripts/gnrsitelocalize', 'scripts/gnrdbsetupparallel', 'scripts/gnrtrdaemon', 'scripts/gnrsync4d', 'scripts/gnrmkproject', 'scripts/gnrdbstruct', 'scripts/gnrdbgraph',
                 'scripts/gnrwsgi', 'scripts/gnruwsgi', 'scripts/gnrasync','scripts/gnrlocalizer', 'scripts/gnrvassal', 'scripts/gnrsite'],
    install_requires=['python-dateutil==1.5', 'paste', 'mako', 'webob', 'weberror', 'pytz',
					  'babel', 'httplib2',	'selectors34',	'serpent', 'pyro4'],
    extras_require=dict(
                postgres=['psycopg2'],
                pg8000=['pg8000'],
                sqlite=['pysqlite'],
                xls=['xlwt', 'xlrd'],
                debugger=['redbaron']
                ),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Genropy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: LGPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


