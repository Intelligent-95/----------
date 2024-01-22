import json
import uuid
import sqlite3
import base64
from webob import Request
from mimes import get_mime
from webob.exc import HTTPFound
from urllib.parse import parse_qs
from collections import namedtuple
from template_engine import render_template

Response = namedtuple("Response", "status headers data") # Именнованный кортеж

class View:
    path = ''

    def __init__(self, url) -> None:
        self.url = url

    def response(self, environ, start_response):
        file_name = self.path + self.url
        headers = [('Content-type', get_mime(file_name))]
        try:
            data = self.read_file(file_name[1:])
            status = '200 OK'
        except FileNotFoundError:
            data = ''
            status = '404 Not found'
        start_response(status, headers)
        return [data.encode('utf-8')]

    def read_file(self, file_name):
        print(file_name)
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()

class TemplateView(View):
    template = ''

    def __init__(self, url) -> None:
        super().__init__(url)
        self.url = '/' + self.template

    def response(self, environ, start_response):
        # Обновление данных о случайном товаре
        self.get_random_product()

        file_name = self.path + self.url
        headers = [('Content-type', get_mime(file_name))]
        try:
            data = self.read_file(file_name[1:])
            status = '200 OK'
        except FileNotFoundError:
            data = ''
            status = '404 Not found'
        start_response(status, headers)
        return [data.encode('utf-8')]

    def read_file(self, file_name):
        print(file_name)
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()

    def get_random_product(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT product_name, description, price, photo, category FROM Products ORDER BY RANDOM() LIMIT 1")
        product = cursor.fetchone()

        cursor.close()
        conn.close()

        photo_data = product[3]
        photo_base64 = base64.b64encode(photo_data).decode('utf-8')

        data = {
            'product_name': product[0],
            'description': product[1],
            'price': product[2],
            'photo': f"data:image/jpeg;base64,{photo_base64}",
            'category': product[4]
        }

        with open('templates/index.html', 'r', encoding='utf-8') as file:
            html_template = file.read()

        rendered_html = render_template(html_template, **data)

        with open('templates/main_index.html', 'w', encoding='utf-8') as file:
            file.write(rendered_html)
    

class IndexView(TemplateView):
    template = 'templates/main_index.html'

class ProductView(TemplateView):
    template = 'templates/product.html'

    def get_product_info(self, product_id):
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT product_name, description, price, photo, category FROM Products WHERE product_id=?", (product_id,))
            product_info = cursor.fetchone()
            conn.close()
            return product_info
        except sqlite3.Error as e:
            print("Error fetching product info:", e)
            return None

    def response(self, environ, start_response):
        request = Request(environ)
        path_info = request.path_info

        if path_info == '/get_product_info':
            query_params = parse_qs(environ['QUERY_STRING'])
            product_id = query_params.get('product_id', [None])[0]

            if product_id:
                product_info = self.get_product_info(product_id)

                if product_info:
                    status = '200 OK'
                    headers = [('Content-type', 'application/json')]
                    response_data = json.dumps({
                        'product_name': product_info[0],
                        'description': product_info[1],
                        'price': product_info[2],
                        'photo': f"data:image/jpeg;base64,{base64.b64encode(product_info[3]).decode('utf-8')}",
                        'category': product_info[4]
                    })
                else:
                    status = '404 Not Found'
                    headers = [('Content-type', 'application/json')]
                    response_data = json.dumps({'error': 'Product not found'})
            else:
                status = '400 Bad Request'
                headers = [('Content-type', 'application/json')]
                response_data = json.dumps({'error': 'Missing product_id parameter'})
        else:
            return super().response(environ, start_response)

        start_response(status, headers)
        return [response_data.encode('utf-8')]

        
class NotFoundView(TemplateView):
    pass
    

class AuthorizationView(TemplateView):
    template = 'templates/authorization.html'


class AddView(TemplateView):
    template = 'templates/add.html'

    def response(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            request = Request(environ)
            post_data = request.POST
            self.handle_post_data(post_data)
            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            data = json.dumps({'redirect': '/'})
            start_response(status, headers)
            return [data.encode('utf-8')]
        
        else:
            return super().response(environ, start_response)

    def handle_post_data(self, post_data):
        product_name = post_data.get('product_name', '')
        description = post_data.get('description', '')
        price = post_data.get('price', '')
        photo = post_data.get('photo', None)
        category = post_data.get('category', '')

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Products (product_name, description, price, photo, category) VALUES (?, ?, ?, ?, ?)',
                (product_name, description, price, photo.file.read(), category)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error while handling post data: {e}")


    def get_user_id_from_cookies(self, environ):
        request = Request(environ)
        user_id_cookie = request.cookies.get('user_id')
        return user_id_cookie

class RegistrationView(TemplateView):
    template = 'templates/registration.html'

    def response(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            request = Request(environ)
            post_data = parse_qs(request.body.decode('utf-8'))
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]
            name = post_data.get('name', [''])[0]
            sex = post_data.get('sex', [''])[0]
            age = post_data.get('age', [''])[0]

            print(f"Received username: {username}, password: {password}, name: {name}, sex: {sex}, age: {age}")

            if username and password and name and sex and age:
                success = self.register_user(username, password, name, sex, age)
                if success:
                    status = '200 OK'
                    headers = [('Content-type', 'application/json')]
                    data = json.dumps({'redirect': '/login', 'message': 'User registered successfully'})
                else:
                    status = '400 Bad Request'
                    headers = [('Content-type', 'application/json')]
                    data = json.dumps({'error': 'Username already exists'})
            else:
                status = '400 Bad Request'
                headers = [('Content-type', 'application/json')]
                data = json.dumps({'error': 'Invalid username or password'})

            start_response(status, headers)
            return [data.encode('utf-8')]
        else:

            return super().response(environ, start_response)



    def register_user(self, name, age, sex, username, password):
        print(f"Received username reg_us: {username}, password: {password}")
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        user_id = uuid.uuid4().hex

        cursor.execute('SELECT * FROM Users WHERE login=?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return False  # Пользователь с таким именем уже существует

        cursor.execute('INSERT INTO Users (login, password, user_id, name, sex, age) VALUES (?, ?, ?, ?, ?, ?)', (username, password, user_id, name, sex, age))
        conn.commit()
        conn.close()
        return True  # Пользователь успешно зарегистрирован

    def get_post_data(self, request, key):
        try:
            data = request.POST.get(key, '')
            #print(f"Received data for {key}: {data}") 
            return data
        except Exception as e:
            print(f"Error while extracting {key}: {e}")
            return None


class LoginView(TemplateView):
    template = 'templates/login.html'

    def response(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            request = Request(environ)
            post_data = parse_qs(request.body.decode('utf-8'))
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]
            print(f"log in: {username}, password: {password}")    
            if username and password:
                user_id = self.authenticate_user(username, password)
                if user_id:
                    status = '200 OK'
                    headers = [('Content-type', 'application/json')]
                    data = json.dumps({'redirect': '/', 'user_id': str(user_id[0])})  
                    start_response(status, headers)
                    return [data.encode('utf-8')]
                else:
                    status = '401 Unauthorized'
                    headers = [('Content-type', 'application/json')]
                    data = json.dumps({'error': 'Invalid username or password'})
                    start_response(status, headers)
                    return [data.encode('utf-8')]
            else:
                status = '400 Bad Request'
                headers = [('Content-type', 'application/json')]
                data = json.dumps({'error': 'Invalid username or password'})
                start_response(status, headers)
                return [data.encode('utf-8')]
        else:
            return super().response(environ, start_response)

    def authenticate_user(self, username, password):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        print(f"Received username: {username}, password: {password}")
        
        cursor.execute('SELECT user_id FROM Users WHERE login=? AND password=?', (username, password))
        user_id = cursor.fetchone()
        conn.close()
        
        print("Authenticated user_id:", user_id)  

        return user_id


    def get_post_data(self, request):
        try:
            data = request.POST
            return data
        except Exception as e:
            print(f"Error while extracting POST data: {e}")
            return None

