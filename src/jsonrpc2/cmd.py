#
import sys
from jsonrpc2 import JsonRpcApplication
from wsgiref.simple_server import make_server

def main(host='', port=8080):
    """
    """
    app = JsonRpcApplication()

    for m in sys.argv[1:]:
        __import__(m)
        mod = sys.modules[m]
        app.rpc.add_module(mod)
    print 'runserver %s:%d' % (host, port)
    httpd = make_server(host, port, app)
    httpd.serve_forever()

if __name__ == '__main__':
    main()

