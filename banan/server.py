import sys, os, signal, fcntl, time
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

class Server(HTTPServer, object):    

    PID_FILE = '/tmp/banan.pid.lock'

    def __init__(self):
        pass

    def close(self, *a, **kw):
        super(Server, self).shutdown()
        super(Server, self).server_close()
        os.unlink(Server.PID_FILE)

    def start(self):

        try:
            super(Server, self).__init__(('127.0.0.1', 8000), SimpleHTTPRequestHandler)
            print('starting server ...')
            
            Server.create_daemon()
            Server.get_pid()
            self.serve_forever()

        except IOError:
            print('server is alreay running ...')

        except KeyboardInterrupt:
            self.shutdown()
 
    def restart(self):
        Server.stop()
        time.sleep(1)
        self.start()


    @staticmethod
    def create_daemon():

        pid = os.fork()
        if pid == 0:
            os.setsid()
        else:
            os._exit(0) # exit parent

    @staticmethod
    def get_pid():
        lock = open(Server.PID_FILE, 'w')
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        lock.write(str(os.getpid()))
        lock.flush()
        fcntl.flock(lock, fcntl.LOCK_UN)

    @staticmethod
    def stop():
        try:
            pid = open(Server.PID_FILE, 'r').readline()
            if pid:
                print('stopping process %s ...' % pid)
                os.kill(int(pid), signal.SIGINT)
        except IOError:
            print('server not running ...')
        except OSError: # process died
            os.unlink(Server.PID_FILE)
