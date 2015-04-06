__author__ = 'davis'
"""
This file is for a demo of all the sql statements
"""

# execute turns these python objects into strings
# when it does the execute statement

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String


engine = create_engine("sqlite://")
metadata = MetaData()
user_table = Table('user', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('username', String(50)),
                  Column('fullname', String)
                  )

metadata.create_all(engine)

print(user_table.c.username)
# I dont have any users in my table yet
print(user_table.c.username == 'ed')
x = (user_table.c.username == 'ed')
print(type(x == 'jack'))

# they become SQL when evaluated as a string
str(user_table.c.username == 'ed')

# ColumnElements can be further combined to produce more ColumnElements
print(
    (user_table.c.username == 'ed') | (user_table.c.username == 'jack')
)

# OR and AND are available with |, &, or or_() and and_()
from sqlalchemy import and_, or_
print(
    and_(
        user_table.c.fullname == 'ed jones',
            or_(
                user_table.c.username == 'ed',
                user_table.c.username == 'jack'
            )
    )
)

# comparison operators
print(user_table.c.id > 5)

# compare to None produces IS NULL
print(user_table.c.fullname == None)
print(user_table.c.fullname != None)
print(user_table.c.fullname is(None))

# "+" might mean "addition"...
print(user_table.c.id + 5)
# ... or might mean "string concatenation"
print(user_table.c.fullname + "some name")

# an IN
# all the usernames where they are wendy, mary or ed
print(user_table.c.username.in_(["wendy",'mary','ed']))

# expressions produce different strings according to dialect objects
expression = user_table.c.username == 'ed'

# mysql
from sqlalchemy.dialects import mysql
print(expression.compile(dialect=mysql.dialect()))


# PostgreSQL
from sqlalchemy.dialects import postgresql
print(expression.compile(dialect=postgresql.dialect()))

# the compiled object also converts literal values to "bound" parameters
compiled = expression.compile()
compiled.params
expression
print expression
expression.compile()
expression.compile().params
expression
expression.left
expression.right
expression.operator

import operator
operator.eq
operator.eq(1,1)
# the bound parameters are extracted when we execute()
engine.execute(
    user_table.select().where(user_table.c.username == 'ed')
)

# Exercise
# produce these expressions using "user_table.c.fullname",
# "user_table.c.id", and "user_table.c.username":
#
# 1. user.fullname = 'ed'
# 2. user.fullname = 'ed' AND user.id > 5
# 3. user.fullname = 'edward' OR (user.fullname = 'ed' AND user.id > 5)

# we can insert data using the insert() construct
insert_stmt = user_table.insert().values(username='ed',fullname='Ed Jones')
conn = engine.connect()
result = conn.execute(insert_stmt)

# executing an insert() gives us the "last inserted id"
result.inserted_primary_key

# insert() and other DML can run multiple parameters at once.
conn.execute(user_table.insert(), [
    {'username':'jack','fullname':'Jack Burger'},
    {'username':'wendy','fullname':'Wendy Weathersmith'}
])

# select() is used to produce any SELECT statement.
from sqlalchemy import select
select_stmt = select([user_table.c.username, user_table.c.fullname]).\
    where(user_table.c.username == 'ed')
result = conn.execute(select_stmt)
for row in result:
    print(row)

# select all columns from a table
select_stmt = select([user_table])
conn.execute(select_stmt).fetchall()

# specify a WHERE clause
select_stmt = select([user_table]).\
    where(
        or_(
            user_table.c.username == 'ed',
            user_table.c.username == 'wendy'
        )
)
conn.execute(select_stmt).fetchall()

# specify multiple WHERE, will be joined by AND
select_stmt = select([user_table]).\
    where(user_table.c.username == 'ed').\
    where(user_table.c.fullname == 'Ed Jones')
conn.execute(select_stmt).fetchall()

# ordering is applied using order_by()
select_stmt = select([user_table]).\
    order_by(user_table.c.username)
print(conn.execute(select_stmt).fetchall())

# Joins / Foreign Keys
# We create a new table to illustrate multi-table operations
from sqlalchemy import ForeignKey
address_table = Table('address',metadata,
                      Column('id',Integer,primary_key=True),
                      Column('user_id',Integer,ForeignKey('user.id'),nullable=False),
                      Column('email_address',String(100),nullable=False)
                      )
metadata.create_all(engine)

# data
conn.execute(address_table.insert(),[
    {'user_id':1, 'email_address':'ed@ed.com'},
    {'user_id':1, 'email_address':'ed@egmail.com'},
    {'user_id':2, 'email_address':'jack@yahoo.com'},
    {'user_id':3, 'email_address':'wendy@gmail.com'},
])

# two table objects can be joined using join()
# <left>.join(<right>, [<onclause>])
join_obj = user_table.join(address_table,
                           user_table.c.id == address_table.c.user_id)
print(join_obj)

# to select from a join, use select_from()
select_stmt = select([user_table,address_table]).select_from(join_obj)
conn.execute(select_stmt).fetchall()

# the select() object is a "selectable" obj just like Table.
# It has a .c. attribute also.
select_stmt = select([user_table]).where(user_table.c.username == 'ed')
print(
    select([select_stmt.c.username]).
        where(select_stmt.c.username == 'ed')
)

# in SQL, a "subquery" is usually an alias() of a select()
select_alias = select_stmt.alias()
print(
    select([select_alias.c.username]).
        where(select_alias.c.username == 'ed')
)

# a subquery against "address" counts addresses per user:
from sqlalchemy import func
address_subq = select([
    address_table.c.user_id,
        func.count(address_table.c.id).label('count')
    ]).\
    group_by(address_table.c.user_id).\
    alias()
print(address_subq)

# we use join() to link the alias() with another select()
username_plus_count = select([
                                user_table.c.username,
                                address_subq.c.count
                        ]).select_from(
                                user_table.join(address_subq)
                        ).order_by(user_table.c.username)

# Scalar selects, updates, deletes
# a "scalar select" returns exactly one row and one column
address_sel = select([
                func.count(address_table.c.id)
                ]).\
                where(user_table.c.id == address_table.c.user_id)


# Scalar selects can be used in column expressions,
# specify it using as_scalar()
select_stmt = select([user_table.c.username,address_sel.as_scalar()])
conn.execute(select_stmt).fetchall()

# to round out INSERT and SELECT, this is an UPDATE
update_stmt = address_table.update().\
                    values(email_address="jack@msn.com").\
                    where(address_table.c.email_address == "jack@yahoo.com")
result = conn.execute(update_stmt)

# an UPDATE can also use expressions based on other columns
update_stmt = user_table.update().\
                    values(fullname=user_table.c.username +
                           " " + user_table.c.fullname)
result = conn.execute(update_stmt)

# and this is a DELETE
delete_stmt = address_table.delete().\
                where(address_table.c.email_address == "ed@ed.com")
result = conn.execute(delete_stmt)

# UPDATE and DELETE have a 'rowcount', number of rows matched by the
# WHERE clause
result.rowcount

# pickup at 1:20 in the presentation

