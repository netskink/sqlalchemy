#!/sw/bin/python2.7
__author__ = 'davis'

from sqlalchemy import create_engine

# four slasshes for absolute path
# postgresql
# posgres "postgresql://scott//scott:tiger@localhost/test")
# postgresql plus psycopg2
# posgres "postgresql+psycopg2://scott:tiger@localhost/test")
engine = create_engine("sqlite:///some.db")

result = engine.execute("select emp_id, emp_name "
                        "from employee "
                        "where emp_id=:emp_id",
                        emp_id=3)

row = result.fetchone()
print type(row), row
print "=="
print type(row['emp_name']), row['emp_name']
print type(row['emp_id']), row['emp_id']
print type(row.emp_id), row.emp_id
# this closes cursor and connection.
result.close()

# showing how you can iterate rows
result = engine.execute("select * from employee")
for row in result:
    print(row)

# +------------------------------------------------------------------+
# | the fetchall() method is a shortcut to producing a list          |
# | of all rows.                                                     |
# +------------------------------------------------------ (8 / 13) --+
result = engine.execute("select * from employee")
print(result.fetchall())

# +------------------------------------------------------------------+
# | The execute() method of Engine will *autocommit*                 |
# | statements like INSERT by default.                               |
# +------------------------------------------------------ (9 / 13) --+
engine.execute("insert into employee_of_month (emp_name) values (:emp_name)", emp_name='fred')

# +------------------------------------------------------------------+
# | We can control the scope of connection using connect().          |
# +----------------------------------------------------- (10 / 13) --+
conn = engine.connect()
result = conn.execute("select * from employee")
result.fetchall()
conn.close()

# +------------------------------------------------------------------+
# | to run several statements inside a transaction, Connection       |
# | features a begin() method that returns a Transaction.            |
# +----------------------------------------------------- (11 / 13) --+

conn = engine.connect()
trans = conn.begin()
conn.execute("insert into employee (emp_name) values (:emp_name)", emp_name="wendy")
conn.execute("update employee_of_month set emp_name = :emp_name", emp_name="wendy")
trans.commit()
conn.close()

# +------------------------------------------------------------------+
# | a context manager is supplied to streamline this process.        |
# +----------------------------------------------------- (12 / 13) --+
with engine.begin() as conn:
    conn.execute("insert into employee (emp_name) values (:emp_name)", emp_name="mary")
    conn.execute("update employee_of_month set emp_name = :emp_name", emp_name="mary")
#
# +-----------------------------------------------------------------------------------+
# | *** Exercises ***                                                                 |
# +-----------------------------------------------------------------------------------+
# | Assuming this table:                                                              |
# |                                                                                   |
# |     CREATE TABLE employee (                                                       |
# |         emp_id INTEGER PRIMARY KEY,                                               |
# |         emp_name VARCHAR(30)                                                      |
# |     }                                                                             |
# |                                                                                   |
# | And using the "engine.execute()" method to invoke a statement:                    |
# |                                                                                   |
# | 1. Execute an INSERT statement that will insert the row with emp_name='dilbert'.  |
# |    The primary key column can be omitted so that it is generated automatically.   |
# |                                                                                   |
# | 2. SELECT all rows from the employee table.                                       |
# +---------------------------------------------------------------------- (13 / 13) --+
result = engine.execute("select * from employee")
print(result.fetchall())
engine.execute("insert into employee (emp_name) values (:emp_name)", emp_name='dilbert')
result = engine.execute("select * from employee")
print(result.fetchall())


