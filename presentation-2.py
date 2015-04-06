#!/sw/bin/python2.7
__author__ = 'davis'
# for debug
import code



from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String

# DDL description of a table
metadata = MetaData()
user_table = Table('user', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('name', String),
                   Column('fullname', String)
                   )

# usage examples
print("*** name of table")
# >>> user_table.name
# 'user'
print(user_table.name)

print('*** column description')
# >>> user_table.c.name
# Column('name', String(), table=<user>)
print(user_table.c.name)

print('*** column names as dictionary keys')
# >>> user_table.columns.keys()
# ['id', 'name', 'fullname']
print(user_table.columns.keys())

print('*** column info')
# in debugger
# >>> user_table.columns.id
# Column('id', Integer(), table=<user>, primary_key=True, nullable=False)
print(user_table.columns.id)


print(user_table.c.name.name)
print(user_table.c.name.type)
name_col = user_table.c.name
print(name_col)
print(name_col.type)
print(name_col.name)
# the table which owns the column. ie. parent table
print(name_col.table)

print(user_table.select())

# we have a table described with metadata, now we can create a db
# this is a in table database
from sqlalchemy import create_engine
engine = create_engine("sqlite://")
metadata.create_all(engine)

#################################
from sqlalchemy import String, Numeric, DateTime, Enum
fancy_table = Table('fancy',metadata,
                    Column('key',String(50),primary_key=True),
                    Column('timestamp',DateTime),
                    Column('amount',Numeric(10,2)),
                    Column('type',Enum('a','b','c'))
                )
fancy_table.create(engine)


#################################
# How to add a foreignkey
from sqlalchemy import ForeignKey
addresses_table = Table('address',metadata,
                        Column('id',Integer,primary_key=True),
                        Column('email_address',String(100),nullable=False),
                        Column('user_id',Integer,ForeignKey('user.id'))
                    )
addresses_table.create(engine)

#################################
# ForeignKeyConstraint for a composite foreign key
from sqlalchemy import Unicode, UnicodeText, DateTime
from sqlalchemy import ForeignKeyConstraint

story_table = Table('story',metadata,
                    Column('story_id',Integer, primary_key=True),
                    Column('version_id', Integer, primary_key=True),
                    Column('headline',Unicode(100),nullable=False),
                    Column('body',UnicodeText)
                )

# foreign key constraint, local column and then foreign table column
published_table = Table('published',metadata,
                        Column('pub_id',Integer,primary_key=True),
                        Column('pub_timestamp',DateTime,nullable=False),
                        Column('story_id',Integer),
                        Column('version_id',Integer),
                        ForeignKeyConstraint(
                            ['story_id','version_id'],
                            ['story.story_id','story.version_id']
                        )
                    )

# Exercise
# Write a table construct corresponding to this create table statement
# CREATE TABLE network (
#       network_id INTEGER PRIMARY KEY,
#       name VARCHAR(100) NOT NULL,
#       created_at DATETIME NOT NULL,
#       owner_id INTEGER,
#       FOREIGN KEY owner_id REFERENCES user(id)
# )
#
# Then emit metadata.createa_all(), which will emit CREATE_TABLE for this table
network_table = Table('network',metadata,
                        Column('network_id',Integer,primary_key=True),
                        Column('name',String(100),nullable=False),
                        Column('created_at',DateTime,nullable=False),
                        Column('owner_id',Integer,ForeignKey('user.id'))
                 )
# why does he want create_all instead of create?
# Ahh, he is using metadata to create all the tables he created, fancy, story, etc.
metadata.create_all(engine)

# reflection refers to loading table objects based on reading
# from an existing database.
metadata2 = MetaData()
user_reflected = Table('user',metadata2,autoload=True,autoload_with=engine)

#todo: look up multicorn.org for John

# You can use the reflected capability to pull in the schema to python

# another thing you can do
from sqlalchemy import inspect
inspector = inspect(engine)
# it can be used to query more specific info from the database
print(inspector)
print(inspector.get_table_names())
print(inspector.get_columns('address'))
print(inspector.get_foreign_keys('address'))

# exercise
# using metadata2 reflect the network table in the same way
# then display the columns
# then using inspector print a list of all table names that include
# a column called "story_id"

network_reflected = Table('network',metadata2,autoload=True,autoload_with=engine)
print(network_reflected)
for tname in inspector.get_table_names():
    for column in inspector.get_columns(tname):
        if column['name'] == 'story_id':
            print tname






# interactive python interpeter
# code.interact(local=locals())




