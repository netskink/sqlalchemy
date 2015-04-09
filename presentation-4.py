__author__ = 'davis'
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# +------------------------------------------------------------------+
# | a basic mapping.  __repr__() is optional.                        |
# +------------------------------------------------------ (2 / 72) --+

from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

    def __repr__(self):
        return "<User(%r, %r)>" % (
            self.name, self.fullname
        )

# +------------------------------------------------------------------+
# | the User class now has a Table object associated with it.        |
# +------------------------------------------------------ (3 / 72) --+
#
# >>> User.__table__
# Table('user',
#        MetaData(bind=None),
#        Column('id', Integer(), table=<user>, primary_key=True, nullable=False),
#        Column('name', String(), table=<user>),
#        Column('fullname', String(), table=<user>),
#        schema=None)
print(User.__table__)

# +------------------------------------------------------------------+
# | The Mapper object mediates the relationship between User         |
# | and the "user" Table object.                                     |
# +------------------------------------------------------ (4 / 72) --+
#
# >>> User.__mapper__
# <Mapper at 0x10742f1d0; User>

# +------------------------------------------------------------------+
# | User has a default constructor, accepting field names            |
# | as arguments.                                                    |
# +------------------------------------------------------ (5 / 72) --+
#
# >>> ed_user = User(name='ed', fullname='Edward Jones')
ed_user = User(name='ed', fullname='Edward Jones')

# +------------------------------------------------------------------+
# | The "id" field is the primary key, which starts as None          |
# | if we didn't set it explicitly.                                  |
# +------------------------------------------------------ (6 / 72) --+
#
# >>> print(ed_user.name, ed_user.fullname)
# ('ed', 'Edward Jones')
# >>> print(ed_user.id)
# None

print(ed_user.name, ed_user.fullname, ed_user.id )

# +------------------------------------------------------------------+
# | The MetaData object is here too, available from the Base.        |
# +------------------------------------------------------ (7 / 72) --+
#
# >>> from sqlalchemy import create_engine
# >>> engine = create_engine('sqlite://')
# >>> Base.metadata.create_all(engine)

from sqlalchemy import create_engine
engine = create_engine('sqlite://')
Base.metadata.create_all(engine)

# +------------------------------------------------------------------+
# | To persist and load User objects from the database, we           |
# | use a Session object.                                            |
# +------------------------------------------------------ (8 / 72) --+
#
# >>> from sqlalchemy.orm import Session
# >>> session = Session(bind=engine)

from sqlalchemy.orm import Session
session = Session(bind=engine)

# +------------------------------------------------------------------+
# | new objects are placed into the Session using add().             |
# ------------------------------------------------------ (9 / 72) --+
#
# >>> session.add(ed_user)

session.add(ed_user)

# add this point the user does not exist in the database, its pending.
# you can see the pending sessions with session.new

print(session.new)

# +------------------------------------------------------------------+
# | the Session will *flush* *pending* objects                       |
# | to the database before each Query.                               |
# +----------------------------------------------------- (10 / 72) --+
#
# >>> our_user = session.query(User).filter_by(name='ed').first()
# >>> our_user

our_user = session.query(User).filter_by(name='ed').first()
print(our_user)


# +------------------------------------------------------------------+
# | the User object we've inserted now has a value for ".id"         |
# +----------------------------------------------------- (11 / 72) --+
#
# >>> print(ed_user.id)
# 1

print(ed_user.name, ed_user.fullname, ed_user.id )

# +------------------------------------------------------------------+
# | the Session maintains a *unique* object per identity.            |
# | so "ed_user" and "our_user" are the *same* object                |
# +----------------------------------------------------- (12 / 72) --+
#
# >>> ed_user is our_user
# True

print(ed_user is our_user)


# its the same object
print( id(ed_user) )
print( id(our_user) )
ed_user.hoho='asdf'
print( ed_user.hoho)

# +------------------------------------------------------------------+
# | Add more objects to be pending for flush.                        |
# +----------------------------------------------------- (13 / 72) --+
#
# >>> session.add_all([
#     ...     User(name='wendy', fullname='Wendy Weathersmith'),
#     ...     User(name='mary', fullname='Mary Contrary'),
#     ...     User(name='fred', fullname='Fred Flinstone')
#     >>> ])


session.add_all([
    User(name='wendy',fullname='Wendy Weathersmith'),
    User(name='mary', fullname='Mary Contrary'),
    User(name='fred', fullname='Fred Flinstone')
])

# +------------------------------------------------------------------+
# | modify "ed_user" - the object is now marked as *dirty*.          |
# +----------------------------------------------------- (14 / 72) --+
#
# >>> ed_user.fullname = 'Ed Jones'

ed_user.fullname = 'Ed Jone'

# +------------------------------------------------------------------+
# | the Session can tell us which objects are dirty...               |
# +----------------------------------------------------- (15 / 72) --+
#
# >>> session.dirty
# IdentitySet([<User('ed', 'Ed Jones')>])

print(session.new)

# +------------------------------------------------------------------+
# | and can also tell us which objects are pending...                |
# +----------------------------------------------------- (16 / 72) --+
#
# >>> session.new
# IdentitySet([<User('wendy', 'Wendy Weathersmith')>, <User('mary', 'Mary Contrary')>, <User('fred', 'Fred Flinstone')>])


print(session.dirty)

# none of this has gone to the database yet

# +------------------------------------------------------------------+
# | The whole transaction is committed.  Commit always triggers      |
# | a final flush of remaining changes.                              |
# +----------------------------------------------------- (17 / 72) --+
#
# >>> session.commit()

session.commit()
print(session.dirty)

# +--------------------------------------------------------------------+
# | After a commit, theres no transaction.  The Session                |
# | *invalidates* all data, so that accessing them will automatically  |
# | start a *new* transaction and re-load from the database.           |
# +------------------------------------------------------- (18 / 72) --+
#
# >>> ed_user.fullname

print(ed_user.fullname)

# +------------------------------------------------------------------+
# | Make another "dirty" change, and another "pending" change,       |
# | that we might change our minds about.                            |
# +----------------------------------------------------- (19 / 72) --+
#
# >>> ed_user.name = 'Edwardo'
# >>> fake_user = User(name='fakeuser', fullname='Invalid')
# >>> session.add(fake_user)

ed_user = 'Edwardo'
fake_user = User(name='fakeuser',fullname='Invalid')
session.add(fake_user)

# +------------------------------------------------------------------+
# | run a query, our changes are flushed; results come back.         |
# +----------------------------------------------------- (20 / 72) --+
#
# >>> session.query(User).filter(User.name.in_(['Edwardo', 'fakeuser'])).all()

print( session.query(User).filter(User.name.in_(['Edwardo','fakeuser'])).all() )

# +------------------------------------------------------------------+
# | But we're inside of a transaction.  Roll it back.                |
# +----------------------------------------------------- (21 / 72) --+
#
# >>> session.rollback()
# [SQL]: ROLLBACK

#print(ed_user.name) # this does not work for me
# print(ed_user.fullname) # nor this
session.rollback()

# +------------------------------------------------------------------+
# | ed_user's name is back to normal                                 |
# +----------------------------------------------------- (22 / 72) --+
#
# >>> ed_user.name
#print(ed_user.name) # this does not work for me
# print(ed_user.fullname) # nor this

# +------------------------------------------------------------------+
# | "fake_user" has been evicted from the session.                   |
# +----------------------------------------------------- (23 / 72) --+
#
# >>> fake_user in session
# False

print(fake_user in session)

# +------------------------------------------------------------------+
# | and the data is gone from the database too.                      |
# +----------------------------------------------------- (24 / 72) --+
#
# >>> session.query(User).filter(User.name.in_(['ed', 'fakeuser'])).all()

print(session.query(User).filter(User.name.in_(['ed','fakeuser'])).all() )

# +-------------------------------------------------------------------+
# | *** Exercises - Basic Mapping ***                                 |
# +-------------------------------------------------------------------+
# |                                                                   |
# | 1. Create a class/mapping for this table, call the class Network  |
# |                                                                   |
# | CREATE TABLE network (                                            |
# |      network_id INTEGER PRIMARY KEY,                              |
# |      name VARCHAR(100) NOT NULL,                                  |
# | )                                                                 |
# |                                                                   |
# | 2. emit Base.metadata.create_all(engine) to create the table      |
# |                                                                   |
# | 3. commit a few Network objects to the database:                  |
# |                                                                   |
# | Network(name='net1'), Network(name='net2')                        |
# +------------------------------------------------------ (25 / 72) --+


class Network(Base):
    __tablename__ = 'network'
    network_id = Column(Integer,primary_key=True)
    name = Column(String(100), nullable=False)

Base.metadata.create_all(engine)
session.add_all([Network(name='net1'), Network(name='net2')])
session.commit()

# +------------------------------------------------------------------+
# | *** ORM Querying ***                                             |
# +------------------------------------------------------------------+
# | The attributes on our mapped class act like Column objects, and  |
# | produce SQL expressions.                                         |
# +----------------------------------------------------- (26 / 72) --+
#
# >>> print(User.name == "ed")
# "user".name = :name_1

print(User.name == "ed")

# it acts like a column
print User.name
print User.name.property.columns[0]

# +------------------------------------------------------------------+
# | These SQL expressions are compatible with the select() object    |
# | we introduced earlier.                                           |
# +----------------------------------------------------- (27 / 72) --+
#
# >>> from sqlalchemy import select
# >>> sel = select([User.name, User.fullname]). \
#     ...         where(User.name == 'ed'). \
#     ...         order_by(User.id)
# >>> session.connection().execute(sel).fetchall()

from sqlalchemy import select

sel = select([User.name, User.fullname]).\
                where(User.name == 'ed'). \
                order_by(User.id)
print ( session.connection().execute(sel).fetchall() )

# +------------------------------------------------------------------+
# | but when using the ORM, the Query() object provides a lot more functionality,  |
# | here selecting the User *entity*.                                              |
# +------------------------------------------------------------------- (28 / 72) --+
#
# >>> query = session.query(User).filter(User.name == 'ed').order_by(User.id)
# >>> query.all()

query = session.query(User).filter(User.name == 'ed').order_by(User.id)
query.all()

# +------------------------------------------------------------------+
# | Query can also return individual columns                         |
# +----------------------------------------------------- (29 / 72) --+
#
# >>> for name, fullname in session.query(User.name, User.fullname):
#     ...     print(name, fullname)

for name, fullname in session.query(User.name, User.fullname):
    print(name,fullname)


# +------------------------------------------------------------------+
# | and can mix entities / columns together.                         |
# +----------------------------------------------------- (30 / 72) --+
#
# >>> for row in session.query(User, User.name):
#     ...     print(row.User, row.name)

for row in session.query(User,User.name):
        print(row.User, row.name)

# +------------------------------------------------------------------+
# | Array indexes will OFFSET to that index and LIMIT by one...      |
# +----------------------------------------------------- (31 / 72) --+
#
# >>> u = session.query(User).order_by(User.id)[2]
# >>> print(u)

u = session.query(User).order_by(User.id)[2]
print(u)

# +------------------------------------------------------------------+
# | and array slices work too.                                       |
# +----------------------------------------------------- (32 / 72) --+
#
# >>> for u in session.query(User).order_by(User.id)[1:3]:
#     ...     print(u)

for u in session.query(User).order_by(User.id)[1:3]:
    print(u)

# +------------------------------------------------------------------+
# | the WHERE clause is either by filter_by(), which is convenient   |
# +----------------------------------------------------- (33 / 72) --+
#
# >>> for name, in session.query(User.name). \
#         ...                 filter_by(fullname='Ed Jones'):
#     ...     print(name)

for name, in session.query(User.name).\
                            filter_by(fullname='Ed Jones'):
    print(name)


# +------------------------------------------------------------------+
# | or filter(), which is more flexible                              |
# +----------------------------------------------------- (34 / 72) --+
#
# >>> for name, in session.query(User.name). \
#         ...                 filter(User.fullname == 'Ed Jones'):
#     ...     print(name)

for name, in session.query(User.name). \
                            filter(User.fullname == 'Ed Jones'):
            print(name)


# +------------------------------------------------------------------+
# | conjunctions can be passed to filter() as well                   |
# +----------------------------------------------------- (35 / 72) --+
#
# >>> from sqlalchemy import or_
# >>> for name, in session.query(User.name). \
#         ...                 filter(or_(User.fullname == 'Ed Jones', User.id < 5)):
#     ...     print(name)

from sqlalchemy import or_
for name, in session.query(User.name). \
                    filter(or_(User.fullname == 'Ed Jones', User.id < 5)):
            print(name)


# +------------------------------------------------------------------+
# | multiple filter() calls join by AND just like select().where()   |
# +----------------------------------------------------- (36 / 72) --+
#
# >>> for user in session.query(User). \
#         ...                         filter(User.name == 'ed'). \
#         ...                         filter(User.fullname == 'Ed Jones'):
#     ...     print(user)
# [SQL]: SELECT user.id AS user_id,

for user in session.query(User). \
                    filter(User.name == 'ed'). \
                    filter(User.fullname == 'Ed Jones'):
            print(user)


# +------------------------------------------------------------------+
# | Query has some variety for returning results                     |
# +----------------------------------------------------- (37 / 72) --+
#
# >>> query = session.query(User).filter_by(fullname='Ed Jones')

query = session.query(User).filter_by(fullname = 'Ed Jones')
print(query)

# +------------------------------------------------------------------+
# | all() returns a list                                             |
# +----------------------------------------------------- (38 / 72) --+
#
# >>> query.all()

print(query.all())


# +------------------------------------------------------------------+
# | first() returns the first row, or None                           |
# +----------------------------------------------------- (39 / 72) --+
#
# >>> query.first()

print( query.first() )


# +-------------------------------------------------------------------------+
# | one() returns the first row and verifies that there's one and only one  |
# +------------------------------------------------------------ (40 / 72) --+
#
# >>> query.one()

# print( query.one() )

# +------------------------------------------------------------------+
# | if there's not one(), you get an error                           |
# +----------------------------------------------------- (41 / 72) --+
#
# >>> query = session.query(User).filter_by(fullname='nonexistent')
# >>> query.one()


query = session.query(User).filter_by(fullname='nonexistent')
#query.one()

# +------------------------------------------------------------------+
# | if there's more than one(), you get an error                     |
# +----------------------------------------------------- (42 / 72) --+
#
# >>> query = session.query(User)
# >>> query.one()

# +---------------------------------------------------------------------------+
# | *** Exercises - ORM Querying ***                                          |
# +---------------------------------------------------------------------------+
# | 1. Produce a Query object representing the list of "fullname" values for  |
# |    all User objects in alphabetical order.                                |
# |                                                                           |
# | 2. call .all() on the query to make sure it works!                        |
# |                                                                           |
# | 3. build a second Query object from the first that also selects           |
# |    only User rows with the name "mary" or "ed".                           |
# |                                                                           |
# | 4. return only the second row of the Query from #3.                       |
# +-------------------------------------------------------------- (43 / 72) --+

query = session.query(User.fullname).all()
print(query)


query = session.query(User.fullname)
print(query.all())

query = session.query(User).\
    filter_by(fullname='nonexistent').\
    filter(User.name == 'ed')
print(query)

q = session.query(User.fullname).order_by(User.fullname)
q2 = q.filter(or_(User.name == 'mary', User.name == 'ed'))
print(q2[1])


# +-------------------------------------------------------------------------+
# | *** Joins and relationships ***                                         |
# +-------------------------------------------------------------------------+
# | A new class called Address, with a *many-to-one* relationship to User.  |
# +------------------------------------------------------------ (44 / 72) --+
#
# >>> from sqlalchemy import ForeignKey
# >>> from sqlalchemy.orm import relationship
#
# >>> class Address(Base):
#     ...     __tablename__ = 'address'
#
# ...     id = Column(Integer, primary_key=True)
# ...     email_address = Column(String, nullable=False)
# ...     user_id = Column(Integer, ForeignKey('user.id'))
#
# ...     user = relationship("User", backref="addresses")
#
# ...     def __repr__(self):
#     ...         return "<Address(%r)>" % self.email_address


from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    # this allows you to have one to many and many to one
    # relationship with the remote table.
    user = relationship("User", backref="addresses")

    def __repr__(self):
        return "<Address(%r)>" % self.email_address


# +------------------------------------------------------------------+
# | create the new table.                                            |
# +----------------------------------------------------- (45 / 72) --+
#
# >>> Base.metadata.create_all(engine)

Base.metadata.create_all(engine)

# +--------------------------------------------------------------------+
# | a new User object also gains an empty "addresses" collection now.  |
# +------------------------------------------------------- (46 / 72) --+
#
# >>> jack = User(name='jack', fullname='Jack Bean')
# >>> jack.addresses
# []

jack = User(name='jack', fullname='Jack Bean')
print(jack.addresses)

# +------------------------------------------------------------------+
# | populate this collection with new Address objects.               |
# +----------------------------------------------------- (47 / 72) --+
#
# >>> jack.addresses = [
#     ...                 Address(email_address='jack@gmail.com'),
#     ...                 Address(email_address='j25@yahoo.com'),
#     ...                 Address(email_address='jack@hotmail.com'),
#     ...                 ]
#

jack.addresses = [
                 Address(email_address='jack@gmail.com'),
                 Address(email_address='j25@yahoo.com'),
                 Address(email_address='jack@hotmail.com'),
                 ]




print(jack.addresses)
print(jack.addresses[1])

# +------------------------------------------------------------------+
# | the "backref" sets up Address.user for each User.address.        |
# +----------------------------------------------------- (48 / 72) --+

# >>> jack.addresses[1]
# <Address('j25@yahoo.com')>
# >>> jack.addresses[1].user
# <User('jack', 'Jack Bean')>


print(jack.addresses[1])
print(jack.addresses[1].user)

# +--------------------------------------------------------------------------+
# | adding User->jack will *cascade* each Address into the Session as well.  |
# +------------------------------------------------------------- (49 / 72) --+
#
# >>> session.add(jack)
# >>> session.new
# IdentitySet([<User('jack', 'Jack Bean')>, <Address('j25@yahoo.com')>, <Address('jack@hotmail.com')>, <Address('jack@gmail.com')>])

session.add(jack)
session.new

# +------------------------------------------------------------------+
# | commit.                                                          |
# +----------------------------------------------------- (50 / 72) --+
#
# >>> session.commit()

session.commit()

# +------------------------------------------------------------------+
# | After expiration, jack.addresses emits a *lazy load* when first  |
# | accessed.                                                        |
# +----------------------------------------------------- (51 / 72) --+
#
# >>> jack.addresses

print(jack.addresses)

# +------------------------------------------------------------------+
# | the collection stays in memory until the transaction ends.       |
# +----------------------------------------------------- (52 / 72) --+
#
# >>> jack.addresses
# [<Address(u'jack@gmail.com')>, <Address(u'j25@yahoo.com')>, <Address(u'jack@hotmail.com')>]

# +------------------------------------------------------------------+
# | collections and references are updated by manipulating objects,  |
# | not primary / foreign key values.                                |
# +----------------------------------------------------- (53 / 72) --+
#
# >>> fred = session.query(User).filter_by(name='fred').one()
# >>> jack.addresses[1].user = fred
# >>> fred.addresses
# >>> session.commit()


fred = session.query(User).filter_by(name='fred').one()
jack.addresses[1].user = fred
fred.addresses
session.commit()

# +------------------------------------------------------------------+
# | Query can select from multiple tables at once.                   |
# | Below is an *implicit join*.                                     |
# +----------------------------------------------------- (54 / 72) --+
#
# >>> session.query(User, Address).filter(User.id == Address.user_id).all()

session.query(User, Address).filter(User.id == Address.user_id).all()

# +------------------------------------------------------------------+
# | join() is used to create an explicit JOIN.                       |
# +----------------------------------------------------- (55 / 72) --+
#
# >>> session.query(User, Address).join(Address, User.id == Address.user_id).all()

session.query(User, Address).join(Address, User.id == Address.user_id).all()

# +------------------------------------------------------------------+
# | The most succinct and accurate way to join() is to use the       |
# | the relationship()-bound attribute to specify ON.                |
# +----------------------------------------------------- (56 / 72) --+
#
# >>> session.query(User, Address).join(User.addresses).all()

session.query(User, Address).join(User.addresses).all()

# +---------------------------------------------------------------------+
# | join() will also figure out very simple joins just using entities.  |
# +-------------------------------------------------------- (57 / 72) --+
#
# >>> session.query(User, Address).join(Address).all()


session.query(User, Address).join(Address).all()

# +-------------------------------------------------------------------+
# | Either User or Address may be referred to anywhere in the query.  |
# +------------------------------------------------------ (58 / 72) --+
#
# >>> session.query(User.name).join(User.addresses). \
#     ...     filter(Address.email_address == 'jack@gmail.com').first()


session.query(User.name).join(User.addresses). \
         filter(Address.email_address == 'jack@gmail.com').first()

# +------------------------------------------------------------------+
# | we can specify an explicit FROM using select_from().             |
# +----------------------------------------------------- (59 / 72) --+
#
# >>> session.query(User, Address).select_from(Address).join(Address.user).all()

session.query(User, Address).select_from(Address).join(Address.user).all()


# +--------------------------------------------------------------------+
# | A query that refers to the same entity more than once in the FROM  |
# | clause requires *aliasing*.                                        |
# +------------------------------------------------------- (60 / 72) --+
#
# >>> from sqlalchemy.orm import aliased
# >>> a1, a2 = aliased(Address), aliased(Address)
# >>> session.query(User). \
#     ...         join(a1). \
#     ...         join(a2). \
#     ...         filter(a1.email_address == 'jack@gmail.com'). \
#     ...         filter(a2.email_address == 'jack@hotmail.com'). \
#     ...         all()


from sqlalchemy.orm import aliased
a1, a2 = aliased(Address), aliased(Address)
session.query(User). \
            join(a1). \
            join(a2). \
            filter(a1.email_address == 'jack@gmail.com'). \
            filter(a2.email_address == 'jack@hotmail.com'). \
            all()

# +------------------------------------------------------------------+
# | We can also join with subqueries.  subquery() returns            |
# | an "alias" construct for us to use.                              |
# +----------------------------------------------------- (61 / 72) --+
#
# >>> from sqlalchemy import func
# >>> subq = session.query(
#    ...                 func.count(Address.id).label('count'),
#                        ...                 User.id.label('user_id')
#    ...                 ). \
#    ...                 join(Address.user). \
#    ...                 group_by(User.id). \
#    ...                 subquery()
# >>> session.query(User.name, func.coalesce(subq.c.count, 0)). \
#    ...             outerjoin(subq, User.id == subq.c.user_id).all()


from sqlalchemy import func

subq = session.query(
                 func.count(Address.id).label('count'),
                                    User.id.label('user_id')
                 ). \
                 join(Address.user). \
                 group_by(User.id). \
                 subquery()

session.query(User.name, func.coalesce(subq.c.count, 0)). \
             outerjoin(subq, User.id == subq.c.user_id).all()

session.query(User.name, subq.c.count). \
    outerjoin(subq, User.id == subq.c.user_id).all()

subq
subq.element
subq.element.froms
subq.element.froms[0]
subq.element.froms[0].right
subq.element.froms[0].left
q = session.query(User)
q.subquery()

# +------------------------------------------------------------------+
# | *** Exercises ***                                                |
# +------------------------------------------------------------------+
# | 1. Run this SQL JOIN:                                            |
# |                                                                  |
# |    SELECT user.name, address.email_address FROM user             |
# |    JOIN address ON user.id=address.user_id WHERE                 |
# |    address.email_address='j25@yahoo.com'                         |
# |                                                                  |
# | 2. Tricky Bonus!  Select all pairs of distinct user names.       |
# |    Hint: "... ON user_alias1.name < user_alias2.name"            |
# +----------------------------------------------------- (62 / 72) --+


# +------------------------------------------------------------------+
# | *** Eager Loading ***                                            |
# +------------------------------------------------------------------+
# | the "N plus one" problem refers to the many SELECT statements    |
# | emitted when loading collections against a parent result         |
# +----------------------------------------------------- (63 / 72) --+
#
# >>> for user in session.query(User):
#     ...     print(user, user.addresses)

for user in session.query(User):
    print(user, user.addresses)

# if you have 5 rows, you will do six queries. here how to solve that.

# +-------------------------------------------------------------------+
# | *eager loading* solves this problem by loading *all* collections  |
# | at once.                                                          |
# +------------------------------------------------------ (64 / 72) --+
#
# >>> session.rollback()  # so we can see the load happen again.
# >>> from sqlalchemy.orm import subqueryload
# >>> for user in session.query(User).options(subqueryload(User.addresses)):
#    ...     print(user, user.addresses)


session.rollback()  # so we can see the load happen again.
from sqlalchemy.orm import subqueryload
for user in session.query(User).options(subqueryload(User.addresses)):
        print(user, user.addresses)

# +---------------------------------------------------------------------------+
# | joinedload() uses a LEFT OUTER JOIN to load parent + child in one query.  |
# +-------------------------------------------------------------- (65 / 72) --+
#
# >>> session.rollback()
# >>> from sqlalchemy.orm import joinedload
# >>> for user in session.query(User).options(joinedload(User.addresses)):
#     ...     print(user, user.addresses)


session.rollback()
from sqlalchemy.orm import joinedload
for user in session.query(User).options(joinedload(User.addresses)):
    print(user, user.addresses)

# +------------------------------------------------------------------+
# | eager loading *does not* change the *result* of the Query.       |
# | only how related collections are loaded.                         |
# +----------------------------------------------------- (66 / 72) --+
#
# >>> for address in session.query(Address). \
#         ...                 join(Address.user). \
#         ...                 filter(User.name == 'jack'). \
#         ...                 options(joinedload(Address.user)):
#     ...     print(address, address.user)


for address in session.query(Address). \
        join(Address.user). \
        filter(User.name == 'jack'). \
        options(joinedload(Address.user)):
    print(address, address.user)


# +------------------------------------------------------------------+
# | to join() *and* joinedload() at the same time without using two  |
# | JOIN clauses, use contains_eager()                               |
# +----------------------------------------------------- (67 / 72) --+
#
# from sqlalchemy.orm import contains_eager
# for address in session.query(Address). \
#                          join(Address.user). \
#                          filter(User.name == 'jack'). \
#                          options(contains_eager(Address.user)):
#          print(address, address.user)


from sqlalchemy.orm import contains_eager
for address in session.query(Address). \
                          join(Address.user). \
                          filter(User.name == 'jack'). \
                          options(contains_eager(Address.user)):
          print(address, address.user)


# +------------------------------------------------------------------+
# | *** Delete Cascades ***                                          |
# +------------------------------------------------------------------+
# | removing an Address sets its foreign key to NULL.                |
# | We'd prefer it gets deleted.                                     |
# +----------------------------------------------------- (68 / 72) --+
#
# jack = session.query(User).filter_by(name='jack').one()
# del jack.addresses[0]
# session.commit()

jack = session.query(User).filter_by(name='jack').one()
del jack.addresses[0]
session.commit()

# +------------------------------------------------------------------+
# | This can be configured on relationship() using                   |
# | "delete-orphan" cascade on the User->Address                     |
# | relationship.                                                    |
# +----------------------------------------------------- (69 / 72) --+
#
# User.addresses.property.cascade = "all, delete, delete-orphan"


User.addresses.property.cascade = "all, delete, delete-orphan"

# +------------------------------------------------------------------+
# | Removing an Address from a User will now delete it.              |
# +----------------------------------------------------- (70 / 72) --+
#
# fred = session.query(User).filter_by(name='fred').one()
# del fred.addresses[0]
# session.commit()

fred = session.query(User).filter_by(name='fred').one()
del fred.addresses[0]
session.commit()


# +------------------------------------------------------------------+
# | Deleting the User will also delete all Address objects.          |
# +----------------------------------------------------- (71 / 72) --+
#
# session.delete(jack)
# session.commit()

session.delete(jack)
session.commit()

# +----------------------------------------------------------------------------+
# | 1. Create a class called 'Account', with table "account":                  |
# |                                                                            |
# |      id = Column(Integer, primary_key=True)                                |
# |      owner = Column(String(50), nullable=False)                            |
# |      balance = Column(Numeric, default=0)                                  |
# |                                                                            |
# | 2. Create a class "Transaction", with table "transaction":                 |
# |      * Integer primary key                                                 |
# |      * numeric "amount" column                                             |
# |      * Integer "account_id" column with ForeignKey('account.id')           |
# |                                                                            |
# | 3. Add a relationship() on Transaction named "account", which refers       |
# |    to "Account", and has a backref called "transactions".                  |
# |                                                                            |
# | 4. Create a database, create tables, then insert these objects:            |
# |                                                                            |
# |      a1 = Account(owner='Jack Jones', balance=5000)                        |
# |      a2 = Account(owner='Ed Rendell', balance=10000)                       |
# |      Transaction(amount=500, account=a1)                                   |
# |      Transaction(amount=4500, account=a1)                                  |
# |      Transaction(amount=6000, account=a2)                                  |
# |      Transaction(amount=4000, account=a2)                                  |
# |                                                                            |
# | 5. Produce a report that shows:                                            |
# |     * account owner                                                        |
# |     * account balance                                                      |
# |     * summation of transaction amounts per account (should match balance)  |
# |       A column can be summed using func.sum(Transaction.amount)            |
# +--------------------------------------------------------------- (72 / 72) --+
#
# >>> from sqlalchemy import Integer, String, Numeric

from sqlalchemy import Integer, String, Numeric




