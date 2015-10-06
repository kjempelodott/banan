import sys, os, signal, fcntl, time, re
from datetime import date, datetime
from posixpath import splitext
from shutil import copyfileobj
from json import JSONEncoder
from uuid import uuid4

from StringIO import StringIO
from SocketServer import TCPServer
from BaseHTTPServer import BaseHTTPRequestHandler

from config import Config
from db import TransactionsDB


class HTTPRequestHandler(BaseHTTPRequestHandler, object):
   
    DB = TransactionsDB(Config())

    TYPES = { '.js'   : ('text/javascript'  , 'handle_static' ),
              '.css'  : ('text/css'         , 'handle_static' ),
              '.html' : ('text/html'        , 'handle_static' ),
              '.json' : ('application/json' , 'send_json'     )}


    def do_POST(self):

#        try:
            self.content_type = 'application/json'
            query = {}

            if 'Content-Type' in self.headers:            
                assert(self.headers['Content-Type'].startswith('application/x-www-form-urlencoded'))
                data = self.rfile.read(int(self.headers['Content-Length']))
                query = dict(item.split('=', 1) for item in data.split('&'))

            self.send_json(**query)

#        except Exception as e:
#            self.send_response(400)
#            self.log_error(str(e))
            

    def do_GET(self):

        if self.path == '/':
            self.path = '/banan/template/layout.html'

        try:
            ext = splitext(self.path)[-1]
            self.content_type, _callback = HTTPRequestHandler.TYPES[ext]
            getattr(self, _callback)()
        except Exception as e:
           self.send_response(404)
           self.log_error(str(e))
   
    def sessionid(self):

        try:
            return re.findall('sessionid=([-\w]+)', self.headers['Cookie'])[0]
        except:
            return uuid4()
        
    def handle_static(self):

        f = open('.' + self.path, 'rb')
        fs = os.fstat(f.fileno())
        sessionid = self.sessionid()        
        
        self.send_response(200)
        self.send_header('Cookie', 'sessionid=%s' % sessionid)
        self.send_header('Content-Type', self.content_type)
        self.send_header('Content-Length', str(fs.st_size))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()
        
        copyfileobj(f, self.wfile)
        f.close()
        
    def send_json(self, **kw):

        sessionid = self.sessionid()
        json = HTTPRequestHandler.DB.get_flot_json(sessionid, **kw)
        json_stream = StringIO(JSONEncoder().encode(json))

        self.send_response(200) 
        self.send_header('Cookie', 'sessionid=%s' % sessionid)
        self.send_header('Content-Type', self.content_type);
        self.send_header('Content-Length', json_stream.len)
        self.end_headers()

        copyfileobj(json_stream, self.wfile)


class Server(TCPServer, object):    

    PID_FILE = '/tmp/banan.pid.lock'
    allow_reuse_address = 1 
 
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
