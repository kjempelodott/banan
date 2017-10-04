import sys, os, signal, fcntl, time, re, socket, traceback
from datetime import date, datetime
from posixpath import splitext
from shutil import copyfileobj
from json import loads, JSONEncoder
from uuid import uuid4

from io import BytesIO
from socketserver import TCPServer
from http.server import BaseHTTPRequestHandler

from banan.logger import *
from banan.db import TransactionsDB
from banan.config import Config


class HTTPRequestHandler(BaseHTTPRequestHandler, object):
   
    DB = TransactionsDB(Config())

    TYPES = { '.js'   : ('text/javascript'  , 'handle_static' ),
              '.css'  : ('text/css'         , 'handle_static' ),
              '.html' : ('text/html'        , 'handle_static' ),
              '.json' : ('application/json' , 'send_json'     )}


    def do_POST(self):

        try:
            self.content_type = 'application/json'
            query = {}
            if 'Content-Type' in self.headers:            
                assert('x-www-form-urlencoded' in self.headers['Content-Type'])
                data = self.rfile.read(int(self.headers['Content-Length'])).decode()
                query = loads(data)
            self.send_json(**query)
        except Exception as e:
            self.send_response(400)
            ERROR(str(e))
            traceback.print_tb(sys.exc_info()[2])

    def do_GET(self):
        if self.path == '/':
            self.path = '/banan/template/layout.html'
        try:
            ext = splitext(self.path)[-1]
            self.content_type, _callback = HTTPRequestHandler.TYPES[ext]
            getattr(self, _callback)()
        except Exception as e:
           self.send_response(404)
           ERROR(str(e))
           traceback.print_tb(sys.exc_info()[2])
   
    def handle_static(self):
        f = open('.' + self.path, 'rb')
        fs = os.fstat(f.fileno())
        self.send_response(200)
        self.send_header('Content-Type', self.content_type)
        self.send_header('Content-Length', str(fs.st_size))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()
        copyfileobj(f, self.wfile)
        f.close()
        
    def send_json(self, **kw):
        valid, data = False, {}
        if self.path == '/labels.json':
            valid, data = True, list(HTTPRequestHandler.DB.config.labels.keys())
        else:
            valid, data = HTTPRequestHandler.DB.assemble_data(**kw)

        encoded_data = JSONEncoder().encode(data).encode()
        json_stream = BytesIO(encoded_data)

        if valid:
            self.send_response(200)
            self.send_header('Content-Type', self.content_type);
            self.send_header('Content-Length', len(encoded_data))
            self.end_headers()
            copyfileobj(json_stream, self.wfile)
        else:
            self.send_response(400)
            self.end_headers()
            self.log_error(data)

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
            print('starting server ...')
            super().__init__(('localhost', 8000), HTTPRequestHandler)
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
