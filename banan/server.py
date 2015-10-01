import sys, os, signal, fcntl, time
from posixpath import splitext
from shutil import copyfileobj
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class HTTPRequestHandler(BaseHTTPRequestHandler, object):
   
    TYPES = { '.js'   : ('text/javascript' , 'send_static' ),
              '.css'  : ('text/css'        , 'send_static' ),
              '.html' : ('text/html'       , 'send_html'   )}

    def get_type(self):

        ext = splitext(self.path)[-1]
        if not ext in HTTPRequestHandler.TYPES:
            ext = '.html'
        return HTTPRequestHandler.TYPES[ext]

    def do_GET(self):

        _type, _callback = self.get_type()
        self.send_response(200)
        self.send_header('Content-type', _type)
        getattr(self, _callback)()
        
    def send_static(self):

        path = '.' + self.path
        if os.path.exists(path):
            self.send_data(path)

    def send_html(self):

        path = 'banan/template/layout.html'
        self.send_data(path)

    def send_data(self, path):

        f = open(path, 'rb')
        fs = os.fstat(f.fileno())
        self.send_header('Content-Length', str(fs.st_size))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))

        self.end_headers()

        copyfileobj(f, self.wfile)
        f.close()


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
            super(Server, self).__init__(('127.0.0.1', 8000), HTTPRequestHandler)
            print('starting server ...')
            
            Server.create_daemon()
            Server.write_pid()
            self.serve_forever()

        except IOError:
            print('server is alreay running (%s) ...' % Server.read_pid())

        except KeyboardInterrupt:
            self.shutdown()
 
    def restart(self):
        Server.stop()
        time.sleep(1)
        self.start()


    @staticmethod
    def create_daemon():

        pid = os.fork()
        if pid == 0: # todo: pipe output somewhere
            os.setsid()
        else:
            os._exit(0) # exit parent

    @staticmethod
    def write_pid():
        lock = open(Server.PID_FILE, 'w')
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        lock.write(str(os.getpid()))
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()

    @staticmethod
    def read_pid():
        return open(Server.PID_FILE, 'r').readline()

    @staticmethod
    def stop():
        try:
            pid = Server.read_pid()
            if pid:
                print('stopping process %s ...' % pid)
                os.kill(int(pid), signal.SIGINT)
        except IOError:
            print('server not running ...')
        except OSError: # process died
            os.unlink(Server.PID_FILE)
