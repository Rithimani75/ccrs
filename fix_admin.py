from flask import Flask
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ccrs'

mysql = MySQL(app)

with app.app_context():

    cursor = mysql.connection.cursor()

    password = generate_password_hash("admin123")

    cursor.execute(
        """
        UPDATE users
        SET password = %s,
            role = 'admin'
        WHERE email = %s
        """,
        (password, "admin@ccrs.com")
    )

    mysql.connection.commit()

    print("================================")
    print("ADMIN ACCOUNT UPDATED")
    print("Email: admin@ccrs.com")
    print("Password: admin123")
    print("Role: admin")
    print("================================")

    cursor.close()