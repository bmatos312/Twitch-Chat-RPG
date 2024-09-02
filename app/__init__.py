from flask import Flask
import pymysql
from app.routes import main, blueprint_name

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

def create_app():
    app = Flask(__name__)

    app.register_blueprint(main)

    app.register_blueprint(blueprint_name, url_prefix='/blueprint')

    return app

# Database connection
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='DB_USERNAME',
        password='DB_PASSWORD',
        db='DB_NAME',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)

