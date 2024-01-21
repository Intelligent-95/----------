from views import *

routes = {
    '/static/': View,
    '/$': IndexView,
    '/add': AddView,
    '/login': LoginView,
    '/registration': RegistrationView,
    '/product': ProductView
}

def route(url):
    """
    Преобразовывает URL в путь к файлу в соответствии с определенными маршрутами.
    """
    for key in routes.keys():
        if url.startswith(key):
            return routes[key] + url[len(key):]
        return url