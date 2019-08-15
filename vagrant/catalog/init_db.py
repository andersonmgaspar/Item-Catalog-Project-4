# (re)Initialize database with categories.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *
from datetime import datetime

engine = create_engine('sqlite:///catalog.db')
DBSession = sessionmaker(bind = engine)
session = DBSession()

session.query(Category).delete()
session.query(Item).delete()
session.query(User).delete()

user = User(name="Anderson Medeiros Gaspar", email="andersonmgaspar@gmail.com")
session.add(user)
session.commit()

user = session.query(User).filter_by(email = "andersonmgaspar@gmail.com").first()
session.add_all([Category(name = "Jazz", user_id=user.id),
    Category(name = "Electronic", user_id=user.id),
    Category(name = "Progressive Metal", user_id=user.id),
    Category(name = "Reggae", user_id=user.id),
    Category(name = "Hip Hop", user_id=user.id),
    Category(name = "Pop", user_id=user.id)])
session.commit()

prog = session.query(Category).filter_by(name = "Progressive Metal").first()
item1 = Item(name = "Tool", date=datetime.now(), description = "Tool is an "
"American rock band from Los Angeles, California, formed in 1990.", picture =
"https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Tool_live_barcelona"
"_2006.jpg/500px-Tool_live_barcelona_2006.jpg", category_id = prog.id,
            user_id=user.id)
session.add(item1)
session.commit()
item2 = Item(name = "King Crimson", date=datetime.now(), description = "King "
"Crimson are an English progressive rock band formed in London in 1968, that "
"now is more international in membership.", picture =
"https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/King_Crimson_-_"
"Dour_Festival_2003_%2801%29.jpg/533px-King_Crimson_-_Dour_Festival_2003_"
"%2801%29.jpg", category_id = prog.id,
            user_id=user.id)
session.add(item2)
session.commit()

elec = session.query(Category).filter_by(name = "Electronic").first()
item3 = Item(name = "Jon Hopkins", date=datetime.now(), description = "Jonathan"
" Julian Hopkins (born 15 August 1979) is an English musician and producer who"
" writes and performs electronic music.", picture =
"https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jon_Hopkins_Rocke"
"feller_2018_213943.jpg/600px-Jon_Hopkins_Rockefeller_2018_213943.jpg",
category_id = elec.id, user_id=user.id)
session.add(item3)
session.commit()
item4 = Item(name = "Aphex Twin", date=datetime.now(), description = "Richard "
"David James (born 18 August 1971), best known by the stage name Aphex Twin, "
"is an English musician.", picture =
"https://upload.wikimedia.org/wikipedia/commons/7/76/Aphex_Twin_2.jpg",
category_id = elec.id, user_id=user.id)
session.add(item4)
session.commit()


print "Reset database and added categories and itens! Hooray!"
