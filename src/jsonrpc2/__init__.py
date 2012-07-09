# -*- coding:utf-8 -*-

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
http://groups.google.com/group/json-rpc/web/json-rpc-2-0

errors:

code 	message 	meaning
-32700 	Parse error 	Invalid JSON was received by the server.
An error occurred on the server while parsing the JSON text.
-32600 	Invalid Request 	The JSON sent is not a valid Request object.
-32601 	Method not found 	The method does not exist / is not available.
-32602 	Invalid params 	Invalid method parameter(s).
-32603 	Internal error 	Internal JSON-RPC error.
-32099 to -32000 	Server error 	Reserved for implementation-defined server-errors.

"""
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
errors = {}
errors[PARSE_ERROR] = "Parse Error"
errors[INVALID_REQUEST] = "Invalid Request"
errors[METHOD_NOT_FOUND] = "Method Not Found"
errors[INVALID_PARAMS] = "Invalid Params"
errors[INTERNAL_ERROR] = "Internal Error"
import sys
try:
    import json
except ImportError:
    try:
        import django.utils.simplejson as json
        sys.modules['json'] = json
    except ImportError:
        import simplejson as json
        sys.modules['json'] = json

import itertools

class JsonRpcException(Exception):
    """
    >>> exc = JsonRpcException(1, INVALID_REQUEST)
    >>> str(exc)
    '{"jsonrpc": "2.0", "id": 1, "error": {"message": "Invalid Request", "code": -32600}}'

    """

    def __init__(self, rpc_id, code, data=None):
        self.rpc_id = rpc_id
        self.code = code
        self.data = data
    
    @property
    def message(self):
        return errors[self.code]

    def as_dict(self):
        if self.data:
            return {'jsonrpc':'2.0',
                'id': self.rpc_id,
                'error':{'code': self.code,
                        'message':self.message,
                        'data':self.data}}
        else:
            return {'jsonrpc':'2.0',
                'id': self.rpc_id,
                'error':{'code': self.code,
                        'message':self.message}}

    def __str__(self):
        return json.dumps(self.as_dict())

class JsonRpcBase(object):
    def __init__(self, methods=None):
        if methods is not None:
            self.methods = methods
        else:
            self.methods = {}

    def load_method(self, method):
        import sys
        module_name, func_name = method.split(':', 1)
        __import__(module_name)
        method = getattr(sys.modules[module_name], func_name)
        return method

    def process(self, data, extra_vars):

        if data.get('jsonrpc') != "2.0":
            raise JsonRpcException(data.get('id'), INVALID_REQUEST)

        if 'method' not in data:
            raise JsonRpcException(data.get('id'), INVALID_REQUEST)
        
        methodname = data['method']
        if not isinstance(methodname, basestring):
            raise JsonRpcException(data.get('id'), INVALID_REQUEST)
            
        if methodname.startswith('_'):
            raise JsonRpcException(data.get('id'), METHOD_NOT_FOUND)


        if methodname not in self.methods:
            raise JsonRpcException(data.get('id'), METHOD_NOT_FOUND)


        method = self.methods[methodname]
        if isinstance(method, basestring):
            method = self.load_method(method)

        try:
            params = data.get('params', [])
            if isinstance(params, list):
                result = method(*params, **extra_vars)
            elif isinstance(params, dict):
                kwargs = dict([(str(k), v) for k, v in params.iteritems()])
                kwargs.update(extra_vars)
                result = method(**kwargs)
            else:
                raise JsonRpcException(data.get('id'), INVALID_PARAMS)
            resdata = None
            if data.get('id'):

                resdata = {
                    'jsonrpc':'2.0',
                    'id':data.get('id'),
                    'result':result,
                    }
            return resdata
        except JsonRpcException, e:
            raise e
        except Exception, e:
            raise JsonRpcException(data.get('id'), INTERNAL_ERROR, data=str(e))

    def _call(self, data, extra_vars):
        try:
            return self.process(data, extra_vars)
        except JsonRpcException, e:
            return e.as_dict()

    def __call__(self, data, **extra_vars):
        if isinstance(data, dict):
            resdata = self._call(data, extra_vars)
        elif isinstance(data, list):
            if len([x for x in data if not isinstance(x, dict)]):
                resdata = {'jsonrpc':'2.0',
                            'id':None,
                            'error':{'code':INVALID_REQUEST,
                                    'message':errors[INVALID_REQUEST]}}
            else:
                resdata = [d for d in (self._call(d, extra_vars) for d in data) if d is not None]
            
        return resdata

    def __getitem__(self, key):
        return self.methods[key]

    def __setitem__(self, key, value):
        self.methods[key] = value

    def __delitem__(self, key):
        del self.methods[key]


class JsonRpc(JsonRpcBase):
    def __init__(self, methods=None):
        super(JsonRpc, self).__init__(methods)

    def add_module(self, mod):
        name = mod.__name__
        for k, v in ((k, v) for k, v in mod.__dict__.iteritems() if not k.startswith('_') and callable(v)):
            self.methods[name + '.' + k] = v

    addModule = add_module

import logging
import sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
class JsonRpcApplication(object):
    def __init__(self, rpcs=None):
        self.rpc = JsonRpc(rpcs)


    def __call__(self, environ, start_response):
        logging.debug("jsonrpc")
        logging.debug("check method")
        if environ['REQUEST_METHOD'] != "POST":
            start_response('405 Method Not Allowed',
                    [('Content-type', 'text/plain')])
            return ["405 Method Not Allowed"]

        logging.debug("check content-type")
        if environ['CONTENT_TYPE'].split(';', 1)[0] != 'application/json':
            start_response('400 Bad Request',
                    [('Content-type', 'text/plain')])
            return ["Content-type must by application/json"]

        content_length = -1
        if "CONTENT_LENGTH" in environ:
            content_length = int(environ["CONTENT_LENGTH"])
        try:
            body = environ['wsgi.input'].read(content_length)
            data = json.loads(body)
            resdata = self.rpc(data) 
            logging.debug("response %s" % json.dumps(resdata))
        except ValueError, e:
            resdata = {'jsonrpc':'2.0',
                       'id':None,
                       'error':{'code':PARSE_ERROR,
                                'message':errors[PARSE_ERROR]}}

        start_response('200 OK',
                [('Content-type', 'application/json')])


        if resdata:
            return [json.dumps(resdata)]
        return []



