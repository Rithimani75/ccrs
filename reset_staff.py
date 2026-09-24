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

    password = "Kumar@123"
    hashed_password = generate_password_hash(password)

    cursor = mysql.connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET password = %s
        WHERE email = %s
        AND role = 'staff'
        """,
        (hashed_password, "kumar@ccrs.com")
    )

    mysql.connection.commit()

    print("================================")
    print("PASSWORD RESET SUCCESSFULLY")
    print("Email: kumar@ccrs.com")
    print("Password: Kumar@123")
    print("================================")

    cursor.close()