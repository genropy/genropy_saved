import sys, os

try:
    from gnr.core import gnrhome

    _PLATFORM_DEFAULT_PATH = gnrhome.PATH
except:
    if sys.platform == 'win32':
        _PLATFORM_DEFAULT_PATH = 'C:\genro'
    else:
        _PLATFORM_DEFAULT_PATH = '/usr/local/genro'

_GNRHOME = os.path.split(os.environ.get('GNRHOME', _PLATFORM_DEFAULT_PATH))
GNRHOME = os.path.join(*_GNRHOME)
_GNRINSTANCES = (os.environ.get('GNRINSTANCES') and os.path.split(os.environ.get('GNRINSTANCES'))) or (
_GNRHOME + ('data', 'instances'))
GNRINSTANCES = os.path.join(*_GNRINSTANCES)
_GNRPACKAGES = (os.environ.get('GNRPACKAGES') and os.path.split(os.environ.get('GNRPACKAGES'))) or (
_GNRHOME + ('packages',))
GNRPACKAGES = os.path.join(*_GNRPACKAGES)
_GNRSITES = (os.environ.get('GNRSITES') and os.path.split(os.environ.get('GNRSITES'))) or (_GNRHOME + ('data', 'sites'))
GNRSITES = os.path.join(*_GNRSITES)
