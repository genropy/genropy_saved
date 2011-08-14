from gnr.core.gnrbasetask import GnrBaseTask, testTask

class Main(GnrBaseTask):
    
    def do(self, parameters=None):
        print parameters
        
        

if __name__=='__main__':
    testTask('testgarden','task.task')