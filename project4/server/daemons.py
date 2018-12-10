import aiocoap.resource as resource
import threading
import datetime
import aiocoap
import asyncio
import socket
import time
import sys
import os
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import paho.mqtt.client as mqtt
import threading
from multiprocessing import Process


class coap_handler(resource.Resource):
    def set_content(self, content):
        self.content = content

    async def render_put(self, request):
        self.set_content(request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)
    
def coaps():
    """
    Function for coap daemon
    """
    coap_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(coap_loop)
    root = resource.Site()
    root.add_resource(('.well-known', 'core'),resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('other', 'block'), coap_handler())
    asyncio.Task(aiocoap.Context.create_server_context(root))
    coap_loop = asyncio.get_event_loop()
    print ("coap daemon started!")
    coap_loop.run_forever()

def mqtts():
    """
    Function for mqtt daemon
    """
    app.connect("iot.eclipse.org",1883,60)
    app.on_connect = on_connect
    app.on_message = on_message
    print ("mqtt daemon started!")
    app.loop_forever()
    
def on_connect(app, userdata, flags, rc):
    app.subscribe(upload)

def on_message(app, userdata, msg):
    app.publish(download, msg.payload);

class Websocket_daemon(tornado.websocket.WebSocketHandler):
    def open(self):
        print('open connection')
      
    def on_message(self, message):
        self.write_message(message)
 
    def on_close(self):
        print('close connection')
 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([(r'/ws', Websocket_daemon),])
  
if __name__ == "__main__":
    upload = 'upload_mqtt'
    download = 'download_mqtt'
    p1 = Process(target=coaps)
    p1.start()
    app = mqtt.Client()
    p2 = Process(target=mqtts)
    p2.start()
    p1.join
    p2.join
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    ipaddress = socket.gethostbyname(socket.gethostname())
    print('Websocket Daemon started with ipaddress %s' % ipaddress)
    tornado.ioloop.IOLoop.instance().start()
