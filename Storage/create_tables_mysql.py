import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-utran2.eastus2.cloudapp.azure.com",
                                  user="user", password="Password", database="Inventory", port="3306")

db_c = db_conn.cursor()
db_c.execute('''
          CREATE TABLE item
          (id INTEGER NOT NULL AUTO_INCREMENT,
          item_id BIGINT NOT NULL,
           brand VARCHAR(250) NOT NULL,
           description VARCHAR(250),
           item_name VARCHAR(250) NOT NULL,
           price VARCHAR(100) NOT NULL,
           quantities INT NOT NULL,
           last_update VARCHAR(100) NOT NULL,
           created_date VARCHAR(100) NOT NULL,
           CONSTRAINT item_pk PRIMARY KEY (id))
          ''')

db_c.execute('''
          CREATE TABLE brand
          (id INTEGER NOT NULL AUTO_INCREMENT,
           brand_id BIGINT NOT NULL, 
           brand_name VARCHAR(250) NOT NULL,
           location VARCHAR(250) NOT NULL,
           email_address VARCHAR(100) NOT NULL,
           phone_number VARCHAR(100) NOT NULL,
           description VARCHAR(250) NOT NULL,
           last_update VARCHAR(100) NOT NULL,
           created_date VARCHAR(100) NOT NULL,
           CONSTRAINT brand_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
