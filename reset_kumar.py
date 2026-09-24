from werkzeug.security import generate_password_hash
import MySQLdb

db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="",
    db="ccrs"
)

cur = db.cursor()

new_password = "Kumar@123"
hashed_password = generate_password_hash(new_password)

cur.execute(
    """
    UPDATE users
    SET password = %s
    WHERE email = %s
    """,
    (hashed_password, "kumar@ccrs.com")
)

db.commit()

print("Kumar password reset successfully.")
print("Email: kumar@ccrs.com")
print("New Password: Kumar@123")

cur.close()
db.close()