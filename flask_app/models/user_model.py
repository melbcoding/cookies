from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app
from flask_app.models import cookie_order
import re
EMAIL_REGEX= re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX= re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)” + “(?=.*[-+_!@#$%^&*., ?]).+$')
from flask import flash
from flask_bcrypt import Bcrypt
bcrypt= Bcrypt(app)

class User:
    DB = "cookies_db"

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email= data['email']
        self.password=data['password']
        self.created_at= data['created_at']
        self.updated_at= data['updated_at']
        self.orders=[]

        
    @classmethod
    def get_all_users(cls):
        query= "SELECT * FROM users"
        results= connectToMySQL(cls.DB).query_db(query)
        print(f'getallusers() from model {results}')
        users_list= []
        for user in results:
            users_list.append(cls(user))
        return users_list
        
    @classmethod
    def get_all_users_with_orders(cls):
        query= "SELECT * FROM users JOIN cookies ON users.id= cookies.user_id; "
        results= connectToMySQL(cls.DB).query_db(query)
        print(results)
        users_list= []
        for row in results:
            
            cookie_data= {
                "id": row['cookies.id'],
                "user_id": row['user_id'],
                "name": row['name'],
                "cookie_type": row['cookie_type'],
                "num_boxes": row['num_boxes'],
                "created_at": row['cookies.created_at'],
                "updated_at": row['cookies.updated_at']
            }
            one_order = cookie_order.Cookie_order(cookie_data)

            user_data = {
                "id": row['id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at']
            }
            
            one_user= cls(user_data)
            one_user.orders.append(one_order)
            users_list.append(one_user)
        return users_list


    @classmethod
    def get_one_user(cls,data):
        query= "SELECT * FROM users WHERE id = %(id)s"
        results= connectToMySQL(cls.DB).query_db(query,data)
        print(results)
        one_user = cls(results[0])
        return one_user

    @classmethod
    def save_user(cls, form_data):
        hash_pword= bcrypt.generate_password_hash(form_data['password'])
        user_data={
            "first_name": form_data['first_name'],
            "last_name":form_data['last_name'],
            "email": form_data['email'],
            "password":hash_pword
        }
        query= "INSERT INTO users(first_name, last_name, email, password) VALUES(%(first_name)s, %(last_name)s, %(email)s,%(password)s);"
        return connectToMySQL(cls.DB).query_db(query,user_data)

    @classmethod
    def get_email(cls,data):
        query="SELECT * FROM users WHERE email=%(email)s;"
        result=connectToMySQL(cls.DB).query_db(query,data)
        print(result)
        if len(result)<1:
            return False
        one_user= cls(result[0])
        print(one_user.password)
        return one_user


    @staticmethod
    def validate_register(form_data):
        is_valid = True
        if len(form_data['first_name'])<2:
            flash("First Name must be atleast 2 characters")
            is_valid = False
        if len(form_data['last_name'])<2:
            flash("Last Name must be atleast 2 characters")
            is_valid = False
        if not EMAIL_REGEX.match(form_data['email']):
            flash("you must enter a valid email")
            is_valid = False
        if form_data['password'] != form_data['confpassword']:
            flash("password and confirm password need to match")
            is_valid = False
        if not PASS_REGEX.match(form_data['password']):
            flash('your password is not strong enough!')
        if len(form_data['password'])<8:
            flash("password must be atleast 8 characters")
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_login(form_data):
        is_valid=True
        user_email={
            "email":form_data['email']
        }
        user_exists= User.get_email(user_email)
        if not user_exists:
            flash("Invalid email/password")
            is_valid=False
        if not bcrypt.check_password_hash(user_exists.password, form_data['password']):
            flash("Invalid email/password")
            is_valid=False
        return is_valid