import pypyodbc as odbc

Driver_name = '{SQL Server}'
Server_name = 'DESKTOP-M0KDECJ\\SQLEXPRESS'
Data_base = 'DeeplMachineLearning'
connection_string  = f"Driver={Driver_name};Server={Server_name};Database={Data_base};Trusted_Connection=yes;"
cnxn = odbc.connect(connection_string)
cursor = cnxn.cursor()
