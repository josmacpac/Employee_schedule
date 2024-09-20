import sys
import MySQLdb

try:
	db = MySQLdb.connect("localhost","ventas","password","companydb" )
except MySQLdb.Error as e:
	print("No puedo conectar a la base de datos:",e)
	sys.exit(1)
print("Conexión correcta.")




cursor = db.cursor()
sql = "insert into productos values (NULL ,'producto', 'descripncionwww', 56.5, 99, 45, NULL);"

try:
   cursor.execute(sql)
   db.commit()
except:
   db.rollback()
db.close()

