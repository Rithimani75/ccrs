from werkzeug.security import check_password_hash
import MySQLdb

db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="",
    db="ccrs"
)

cur = db.cursor()

cur.execute(
    "SELECT id, name, email, password, role FROM users WHERE email = %s",
    ("admin@ccrs.com",)
)

user = cur.fetchone()

if user is None:
    print("ERROR: Admin account was not found.")
else:
    print("Admin account found.")
    print("ID:", user[0])
    print("Name:", user[1])
    print("Email:", user[2])
    print("Role:", user[4])

    if check_password_hash(user[3], "Admin@123"):
        print("PASSWORD TEST: SUCCESS")
    else:
        print("PASSWORD TEST: FAILED")

cur.close()
db.close()