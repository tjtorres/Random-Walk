from sqlalchemy import create_engine, engine
import pandas as pd
import sys


#Specify CSV file with flickr photos from 100M photo Database
csv_file = sys.argv[1]


DB_NAME = '' #Name of your SQL Database
TABLE_NAME = '' #Name of your SQL Table

def db_conn(df, DB_NAME , table_name):

    # MySql connection in sqlAlchemy
    engine = create_engine('mysql://root:password@localhost:3306/'+DB_NAME+'?charset=utf8')
    connection = engine.connect()
 
    # Do not insert the row number (index=False)
    df.to_sql(name=table_name, con=engine, if_exists='append', flavor='mysql', index=False, chunksize=2000)
    connection.close()

if __name__ == '__main__':   

	pics = pd.read_csv(csv_file,index_col=None)

	#If table exists then set index ('ID') to be at the end of the current table.
	try:
		engine = create_engine('mysql://root:password@localhost:3306/'+DB_NAME+'?charset=utf8')
		connection = engine.connect()
		max_ID_q = connection.execute("select max(ID) from "+TABLE_NAME+";")
		max_ID = -1

		for item in max_ID_q: 
			max_ID = item[0]

		indexer = range(max_ID+1, max_ID+1+pics.shape[0])
		pics['ID'] = indexer

	except:
		pics['ID'] = range(pics.shape[0])



	db_conn(pics, DB_NAME, TABLE_NAME)