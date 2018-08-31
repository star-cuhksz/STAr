import pymysql

db = pymysql.connect("192.168.0.102","root","root","star")
while True:
	cursor = db.cursor()
	cursor.execute("SELECT * FROM data WHERE id=1")
	data = cursor.fetchone()
	#print(data[4:6])
	print(data[4])
db.close()