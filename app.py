import os
import re
import sqlite3
from routes import routes
from mimes import get_mime
from views import View
from views import NotFoundView


def load(file_name):
    f = open(file_name, encoding='utf-8')
    data = f.read()
    f.close()
    return data

def app(environ, start_response):
    """
    (dict, callable( status: str,
                     headers: list[(header_name: str, header_value: str)]))
                  -> body: iterable of strings_
    """
    url = environ['REQUEST_URI']
    view = None
    
    for key in routes.keys():
        if re.match(key, url) is not None:
            view = routes[key](url)
            break
    
    if view is None:
        view = NotFoundView(url)
    
    resp = view.response(environ, start_response)
    return resp