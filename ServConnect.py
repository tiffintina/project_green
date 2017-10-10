import os
'''
Created on Aug 17, 2017

@author: Administrator
'''
class Request:
    def __init__(self, server, data, client_address, request_method, request_url):
        self.server = server
        self.data = data
        self.client_address = client_address
        self.request_method = request_method
        self.request_url = request_url
    
    def get_method(self):
        return self.request_method;
    
    def get_url(self):
        return self.request_url
     
    def get_server_config(self):
        return self.server.config;
    
    def get_input_stream(self):
        return self.data
    
    def get_path(self,index):
        pth = os.path.split(self.request_url)
        if len(pth) > 0:
            return pth[index]
        else:
            return None
    
    def get_home_dir(self):
        return self.server.www_dir
    
    def get_host(self):
        return self.server.host
    
    def get_port(self):
        return self.server.port
    
    def get_parameter(self, key):
        if self.request_method == "GET":
            hp = self.request_url.index("?")
            if hp > -1:
                hsp = self.request_url.split("?")
                ps = hsp[1].split("&")
                if len(ps) > 0:
                    for i in range(len(ps)):
                        parm = ps[i].split("=")
                        if parm[0] == key:
                            return parm[1]
        else:
            if self.request_method == "POST":
                pass
        return None
    
    def get_client_address(self):
        return self.client_address
    
    
class Response:
    def __init__(self, server, conn):
        self.server = server
        self.conn = conn
        self.response_headers = ''
        self.response_content = ''
        
    def write(self, string):
        self.response_content += string
    
    def set_header(self, code, content_type, content_length=-1):
        self.response_headers = self.server._gen_headers(code, content_type+'\n', content_length)
        
    def flush(self):
        server_response =  self.response_headers.encode()
        server_response +=  self.response_content
        self.conn.send(server_response) 
    
    def close(self):
        self.conn.close()