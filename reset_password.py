from flask_mysqldb import MySQL
from flask import Flask
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ccrs'

mysql = MySQL(app)

with app.app_context():
    new_password = 'Rithika@123'

    hashed_password = generate_password_hash(new_password)

    cursor = mysql.connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET password = %s
        WHERE email = %s
        """,
        (
            hashed_password,
            'rithika.mca2025@adhiyamaan.in'
        )
    )

    mysql.connection.commit()
    cursor.close()

    print("Password reset successfully!")
    print("Email: rithika.mca2025@adhiyamaan.in")
    print("Password: Rithika@123")