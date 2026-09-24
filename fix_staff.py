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

    password = generate_password_hash("staff123")

    cursor.execute("""
        INSERT INTO users
        (name, register_number, email, password, role)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        password = %s,
        role = 'staff',
        name = %s
    """, (
        "Staff User",
        "STAFF001",
        "staff@ccrs.com",
        password,
        "staff",
        password,
        "Staff User"
    ))

    mysql.connection.commit()
    cursor.close()

    print("================================")
    print("STAFF ACCOUNT CREATED/UPDATED")
    print("================================")
    print("Email    : staff@ccrs.com")
    print("Password : staff123")
    print("Role     : staff")