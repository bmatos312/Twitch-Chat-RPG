from flask import Flask
import pymysql
from app.routes import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database connection
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='tolstoy',
        password='Performix312!',
        db='rpg_data',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)

