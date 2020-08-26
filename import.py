import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker



def importData():

	try:

		#connect to database
		engine = create_engine(os.getenv("DATABASE_URL"))
		db = scoped_session(sessionmaker (bind = engine))

		#open file
		file = open('books.csv')
		#read contents
		contents = csv.reader(file)
		#then insert into books table
		next(contents) #skip top row

		for isbn, title, author, year in contents:
			db.execute("INSERT INTO books (isbn,title,author,published,reviewcount,averagescore) VALUES(:isbn, :title, :author, :published, :reviewcount , :averagescore)", {"isbn" : isbn, "title" : title, "author": author, "published" : year, "reviewcount" : 0, "averagescore" : 0})
		db.commit()

	except:
		print("something went wrong, file data could not be inserted")
	finally:
		file.close()



if __name__ == "__main__":
	importData()
