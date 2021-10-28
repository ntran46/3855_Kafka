import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-utran2.eastus2.cloudapp.azure.com", user="user", password="Password", database="Inventory")


db_c = db_conn.cursor()
db_c.execute('''
          DROP TABLE Inventory.brand, Inventory.item;
          ''')

db_conn.commit()
db_conn.close()