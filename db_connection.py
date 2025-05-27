import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ilove127",
    database="org_management"
)

cursor = db.cursor()
