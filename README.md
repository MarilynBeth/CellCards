TODO: This script is not consistent with the schema discussed, some column/variable names need to be changed as well as the SPARQL query present in the code. 

MySQL Workbench version = 8.0.34


Python version = 3.12


Call create_server_connection (return connection to server, for local MySQL sv pass in “localhost”, “root”, and password)

From connection returned from create_server_connection, pass to create_database and the create database query (query = “Create database someName”)

Database with name “someName” should be created.

Get connection from create_database_connection (returns connection to database, if local hostname should be “localhost”, “root”, password, and database name just created)

Theres also some variables with on line 135 and 136 that could be assigned as your password (pw) and database name (db)

Pass connection returned from  create_database_connection to execute_query with the query wanted, createTable is a query that creates a table in the database. 

From there you can replace the SPARQL query with another one, but you would need to change some variables names in there in order to be consistent with the insert query. 
