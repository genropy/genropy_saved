import os
import sys
from gnr.app.gnrdeploy import initgenropy


if __name__ == '__main__':
    import sys
    gnrdaemon_password=sys.argv[1] if len(sys.argv)>1 else None
    initgenropy(gnrpy_path=os.path.dirname(os.path.realpath(__file__)),gnrdaemon_password=gnrdaemon_password)