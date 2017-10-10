import socket  # Networking support
import signal  # Signal support (server shutdown on signal receive)
import time    # Current time
import configparser as ConfigParser
import thread
import os
import ServConnect
import logging as log

class Server:
    """ Class describing a simple HTTP server objects."""
    
    def __init__(self, port = 8099):
        """ Constructor """
        self.config = ConfigParser.RawConfigParser()
        self.config.read("config.cfg");
        self.host = self.config.get("server", "host")   # <-- works on all avaivable network interface
        self.port = self.config.getint("server", "port")
        self.www_dir = self.config.get("server", "www_dir")
        """config.get("server", "www_dir") # Directory where webpage files are stored"""
        """self.pathDefinition()"""

        
    def activate_server(self):
        """ Attempts to aquire the socket and launch the server """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            log.info("Launching HTTP server on ", self.host, ":",self.port)
            self.socket.bind((self.host, self.port))
        except Exception as e:
            log.error("ERROR: Failed to acquire sockets for ports ", self.port, " and 8080. ")
            log.error("Try running the Server in a privileged user mode.", e)
            self.shutdown()
            import sys
            sys.exit(1)
        log.info ("Server successfully acquired the socket with port:", self.port)
        log.info ("Press Ctrl+C to shut down the server and exit.")
        self._wait_for_connections()
    
    def shutdown(self):
        """ Shut down the server """
        try:
            log.info("Shutting down the server")
            s.socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            log.error("Warning: could not shut down the socket. Maybe it was already closed?",e)
    
    def _gen_headers(self,  code, content_type=None, content_length=-1):
        """ Generates HTTP response Headers. Ommits the first line! """
        # determine response code
        h = ''
        if (code == 200):
            h = 'HTTP/1.1 200 OK\n'
        elif(code == 404):
            h = 'HTTP/1.1 404 Not Found\n'
        # write further headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date +'\n'
        h += 'Server: Simple-Python-HTTP-Server\n'
        if content_type != None:
            h += 'Content-Type: '+ content_type
        if content_length > -1:
            h += 'Content-Length: '+ str(content_length)
        h += 'Connection: close\n\n'  # signal that the conection wil be closed after complting the request
        return h
    
    def _wait_for_connections(self):
        """ Main loop awaiting connections """
        while True:
            log.info("Awaiting New connection")
            self.socket.listen(20) # maximum number of queued connections
            thread.start_new_thread(self.server_receive, (self.socket.accept()))

        
    def server_receive(self, conn, addr):
        log.info("Got connection from:", addr)
        data = conn.recv(1024) #receive data from client
        string = bytes.decode(data) #decode it to string
        #determine request method  (HEAD and GET are supported)
        request_method, url = "", ""
        log.info("query string:", string);
        try:
            request_method = string.split(' ')[0]
            url = string.split(' ')[1]
        except Exception as e:
            log.error ("Warning, file not found. Serving response code 404\n", e)
        log.info("url:", url);
        log.info ("Method: ", request_method)
        log.info ("Request body: ", string)
        if os.path.isfile(self.www_dir+ url):
            log.info("is file:", url)
            thread.start_new_thread(self.fileHandler, 
                                    (conn, addr, request_method, string));
        else:
            try:
                log.info("check handler:", self.config.get("server", "host"))
                section = self.pathDefinition(url)
                log.info("section match:", section)
                if self.config.get(section, "handler") != None:
                    log.info("in handler")
                    handler = None
                    exec( "from "+ self.config.get(section, "package") + 
                          " import "+ self.config.get(section, "file"))
                    exec("handler = "+ self.config.get(section, "file")+
                         "."+self.config.get(section, "handler")+"()\n")
                    thread.start_new_thread(handler.service, (self, 
                        ServConnect.Request(self, string, addr, request_method, url), 
                        ServConnect.Response(self, conn)))
            except Exception as e:
                log.info("Warning, file not found. Serving response code 404\n", e)
                response_headers = self._gen_headers( 404)
                if (request_method == 'GET'):
                    response_content = b"<html><body><p>Error 404: File not found </p><p>Python HTTP server</p></body></html>"
                server_response =  response_headers.encode() # return headers for GET and HEAD
                if (request_method == 'GET'):
                    server_response +=  response_content  # return additional conten for GET only
                conn.send(server_response)
                log.info("Closing connection with client")
                conn.close()
                #eval()
            #thread.start_new_thread(servhandle, args);
        #if string[0:3] == 'GET':
        
    def pathDefinition(self, url):
        c = 0
        for each_section in self.config.sections():
            if each_section.startswith("/"):
                if len(url) < len(each_section):
                    continue
                c = 0
                for i in range(len(each_section)):
                    if each_section[i] == url[i]:
                        c+=1
                    else: break
                if c == len(each_section):
                    return each_section
        return None
                    
    
    def fileHandler(self, conn, addr, request_method, stringData):
        string = stringData
        if (request_method == 'GET') | (request_method == 'HEAD'):
            #file_requested = string[4:]
            # split on space "GET /file.html" -into-> ('GET','file.html',...)
            file_requested = string.split(' ')
            file_requested = file_requested[1] # get 2nd element
            #Check for URL arguments. Disregard them
            file_requested = file_requested.split('?')[0]  # disregard anything after '?'
            if (file_requested == '/'):  # in case no file is specified by the browser
                file_requested = '/index.html' # load index.html by default
            file_requested = self.www_dir + file_requested
            log.info("Serving web page [",file_requested,"]")
            ## Load file content
            try:
                file_handler = open(file_requested,'rb')
                if (request_method == 'GET'):  #only read the file when GET
                    response_content = file_handler.read() # read file content
                file_handler.close()
                response_headers = self._gen_headers( 200)
            except Exception as e: #in case file was not found, generate 404 page
                log.error ("Warning, file not found. Serving response code 404\n", e)
                response_headers = self._gen_headers( 404)
                if (request_method == 'GET'):
                    response_content = b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"
            server_response =  response_headers.encode() # return headers for GET and HEAD
            if (request_method == 'GET'):
                server_response +=  response_content  # return additional conten for GET only
            conn.send(server_response)
            log.info("Closing connection with client")
            conn.close()
        else:
            log.info("Unknown HTTP request method:", request_method)        


def graceful_shutdown(sig, dummy):
    """ This function shuts down the server. It's triggered
    by SIGINT signal """
    s.shutdown() #shut down the server
    import sys
    sys.exit(1)

##########################################################
# shut down on ctrl+c
signal.signal(signal.SIGINT, graceful_shutdown)
log.info("Starting web server")
s = Server(8099)  # construct server object
s.activate_server() # aquire the socket


