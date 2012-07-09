
# Copyright (c) 2010 Atsushi Odagiri
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
for the google appengine handler
"""
from jsonrpc2 import JsonRpc
import json

rpc = JsonRpc()

def register(namespace=None, name=None):
    def wrap(func):
        if name is None:
            name = func.__name__
        if nemspace is None:
            rpc.methods[name] = func
        else:
            rpc.methods[namespace + '.' + name] = func
        return func
    return wrap



class JsonRpcHandlerMixin(object):
    def post(self):
        try:
            body = environ['wsgi.input'].read(-1)
            data = json.loads(body)
            resdata = rpc(data) 
        except ValueError, e:
            resdata = {'jsonrpc':'2.0',
                       'id':None,
                       'error':{'code':PARSE_ERROR,
                                'message':errors[PARSE_ERROR]}}
        self.response.headers['Content-type'] = 'application/json'
        if resdata:
            self.response.out.write(json.dumps(resdata))


