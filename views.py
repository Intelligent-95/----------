import json
import time
import uuid
import sqlite3
import base64
import random
from webob import Request
from mimes import get_mime
from webob.exc import HTTPFound
from urllib.parse import parse_qs
from collections import namedtuple
from db import registration, log_in, md5sum
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


    def get_random_product():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT product_name, description, price, photo, category FROM Products ORDER BY RANDOM() LIMIT 1")
        product = cursor.fetchone()

        cursor.close()
        conn.close()

        return product

    random_item = get_random_product()

    photo_data = random_item[3] 
    photo_base64 = base64.b64encode(photo_data).decode('utf-8')

    data = {
        'product_name': random_item[0],
        'description': random_item[1],
        'price': random_item[2],
        'photo': f"data:image/jpeg;base64,{photo_base64}",  
        'category': random_item[4]
    }



    with open('templates/index.html', 'r', encoding='utf-8') as file:
        html_template = file.read()


    rendered_html = render_template(html_template, **data)


    with open('templates/main_index.html', 'w', encoding='utf-8') as file:
        file.write(rendered_html)
    

class IndexView(TemplateView):
    template = 'templates/main_index.html'


class NotFoundView(TemplateView):
    pass
    

class AuthorizationView(TemplateView):
    template = 'templates/authorization.html'

class AddView(TemplateView):
    template = 'templates/add.html'

    def post(self, environ, start_response):
        print("Received POST request to AddView")  
        data = self.get_post_data(environ)
        print("Received data:", data)  

        product_name = data.get('product_name', '')
        description = data.get('description', '')
        price = data.get('price', '')
        category = data.get('category', '')
        photo = data.get('photo', None)

        # Изменено: Получение user_id из cookies
        user_id = self.get_user_id_from_cookies(environ)

        if product_name and description and price and category and photo and user_id:
            print("All required fields present")  
            photo_data = base64.b64decode(photo.split(",")[1])

            # Изменено: Используем user_id вместо случайного пользователя
            self.add_product_to_database(product_name, description, price, category, photo_data, user_id)

            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            response_data = json.dumps({'message': 'Product added successfully'})
        else:
            status = '400 Bad Request'
            headers = [('Content-type', 'application/json')]
            response_data = json.dumps({'error': 'Missing required fields'})
            

        start_response(status, headers)
        return [response_data.encode('utf-8')]


        return super().response(environ, start_response)

    def add_product_to_database(self, product_name, description, price, category, photo_data, user_id):
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute('INSERT INTO Products (product_name, description, price, user_id, photo, category) VALUES (?, ?, ?, ?, ?, ?)',
                           (product_name, description, price, user_id, photo_data, category))

            conn.commit()
            print("Product added successfully!")
        except sqlite3.Error as e:
            print("Error", e)
        finally:
            cursor.close()
            conn.close()

    def get_user_id_from_cookies(self, environ):
        request = Request(environ)
        user_id_cookie = request.cookies.get('user_id')
        return user_id_cookie



class RegistrationView(TemplateView):
    template = 'templates/registration.html'

    def response(self, environ, start_response):
        request = Request(environ)
        if request.method == 'POST':
            post_data = request.POST
            name = post_data.get('name', '')
            age = post_data.get('age', '')
            sex = post_data.get('sex', '')
            username = post_data.get('username', '')
            password = post_data.get('password', '')
            print(f"Received username reg_us: {username}, password: {password}, {name}, {age}, {sex}")
            if name and age and sex and username and password:
                success = self.register_user(name, age, sex, username, password)
                if success:
                    status = '200 OK'
                    headers = [('Content-type', 'application/json')]
                    data = json.dumps({'message': 'User registered successfully'})
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

        return super().response(environ, start_response)


    def register_user(self, name, age, sex, username, password):
        print(f"Received username reg_us: {username}, password: {password}")
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Генерируем уникальный идентификатор пользователя
        user_id = uuid.uuid4().hex

        # Проверяем, есть ли уже пользователь с таким именем
        cursor.execute('SELECT * FROM Users WHERE login=?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return False  # Пользователь с таким именем уже существует

        # Если пользователь не найден, регистрируем нового
        cursor.execute('INSERT INTO Users (login, password, user_id, name, sex, age) VALUES (?, ?, ?, ?, ?, ?)', 
                        (username, password, user_id, name, sex, age))
        conn.commit()
        conn.close()
        return True  # Пользователь успешно зарегистрирован

    def get_post_data(self, request, key):
        try:
            data = request.POST.get(key, '')
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
                    # Вместо редиректа возвращаем JSON с информацией о редиректе
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
        
        # Проверяем, существует ли пользователь с таким именем и паролем
        cursor.execute('SELECT user_id FROM Users WHERE login=? AND password=?', (username, password))
        user_id = cursor.fetchone()
        conn.close()

        # Если пользователь существует, возвращаем его ID, иначе None
        print("Authenticated user_id:", user_id)  

        return user_id


    def get_post_data(self, request):
        try:
            data = request.POST
            return data
        except Exception as e:
            print(f"Error while extracting POST data: {e}")
            return None



class GetUserIdView(View):

    # Функция для получения user_id из базы данных по имени пользователя
    def fetch_user_id_from_database(self, username):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        # Используем параметризованный запрос для предотвращения SQL-инъекций
        cursor.execute("SELECT user_id FROM Users WHERE login=?", (username,))
        
        user_id = cursor.fetchone()

        cursor.close()
        connection.close()

        return user_id[0] if user_id else None

    def response(self, environ, start_response):
        headers = [
            ('Content-type', 'application/json'),
            ('Access-Control-Allow-Origin', 'http://localhost:8000'),  
            ('Access-Control-Allow-Credentials', 'true'), 
            ]

        request = Request(environ)

        user_id_cookie = request.cookies.get('user_id')

        if user_id_cookie:
            user_id = user_id_cookie
        else:
            user_id = None

        print("Response from /get_user_id:", {"user_id": user_id})

        if user_id is None:
            print("User ID is None. Cannot fetch messages.")
            status = '200 OK'
            data = json.dumps({'user_id': None})
            start_response(status, headers)
            return [data.encode('utf-8')]
        else:
            print(f"Fetching messages for user_id: {user_id}")

            fetched_user_id = self.fetch_user_id_from_database(user_id)

            if fetched_user_id is not None:
                user_id = fetched_user_id

            print("Fetched user_id:", user_id)

            status = '200 OK'
            data = json.dumps({'user_id': str(user_id)})  
            start_response(status, headers + [('Set-Cookie', f'user_id={user_id}; Path=/')])
            return [data.encode('utf-8')]