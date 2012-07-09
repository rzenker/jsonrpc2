# -*- coding:utf-8 -*-
import sys
import logging
from jsonrpc2 import JsonRpcApplication

def make_app(global_conf, **app_conf):
    conf = global_conf.copy()
    conf.update(app_conf)

    application = JsonRpcApplication()

    for modname in [m.strip() for m in conf.get('modules', '').split()]:
        logging.debug("register %s" % modname)
        __import__(modname)
        mod = sys.modules[modname]
        application.rpc.addModule(mod)

    
    return application
