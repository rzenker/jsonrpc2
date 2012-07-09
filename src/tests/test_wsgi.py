#
from webtest import TestApp
from nose import with_setup
from nose.tools import *
from jsonrpc2 import JsonRpcApplication
from functools import wraps
import sys
try:
    import json
except ImportError:
    import simplejson as json
    sys.moduels['json'] = json


def with_app(test_func):
    app = JsonRpcApplication()
    app.rpc['hello'] = lambda x : {"message":"hello %s" % x}
    app = TestApp(app)

    @wraps(test_func)
    def dec():
        return test_func(app)
    return dec

@with_app
def test_failure(app):
    params = json.dumps({'jsonrpc':'2.0', 
        'method':'hello', 
        'params':"a", 
        'id':'hello'})
    res = app.post('/', params=params,
            extra_environ={
                "CONTENT_TYPE":'application/json',
                })
    print res.body
    eq_(res.body, 
            '{"jsonrpc": "2.0", '
            '"id": "hello", '
            '"error": {"message": "Invalid Params", "code": -32602}}')

