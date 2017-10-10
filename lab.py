'''
Created on Aug 16, 2017

@author: Administrator
'''
"""
import thread
import configparser as ConfigParser

config = ConfigParser.RawConfigParser()
config.read("config.cfg");
print(config.get("server", "host"))
print(config.getint("server", "port"))
print(config.get("server", "www_dir"))
print(config.get("/arduino/temperature", "package"))
print(config.get("/arduino/temperature", "handler"))
thread.start_new_thread(function, args);
"""
request_method = "GET"
request_url = "/arduino/sensor?xxx=1010&yyy=200"

def get_parameter(key):
    if request_method == "GET":
        hp = request_url.index("?")
        if hp > -1:
            hsp = request_url.split("?")
            ps = hsp[1].split("&")
            if len(ps) > 0:
                for i in range(len(ps)):
                    parm = ps[i].split("=")
                    if parm[0] == key:
                        return parm[1]
    else:
        if request_method == "POST":
            pass                
    return None

val = get_parameter("yyy")
print("key:", val)