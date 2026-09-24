from werkzeug.security import generate_password_hash
import MySQLdb

password = "Admin@123"
hashed_password = generate_password_hash(password)

db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="",
    db="ccrs"
)

cur = db.cursor()

cur.execute(
    "UPDATE users SET password = %s, role = 'admin' WHERE email = %s",
    (hashed_password, "admin@ccrs.com")
)

db.commit()

print("Admin password reset successfully!")
print("Email: admin@ccrs.com")
print("Password: Admin@123")

cur.close()
db.close()