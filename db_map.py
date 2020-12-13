from sqlalchemy import Column, Integer, String, create_engine, MetaData, Table

def create_db():
   engine = create_engine('sqlite:///dbase.db', echo = True)

   meta = MetaData()

   users = Table(
      'users', meta,
      Column('id', Integer, primary_key = True),
      Column('name', String),
      Column('lastname', String),
      Column('position', String),
      Column('registration_date', Integer),
      Column('last_time', Integer)
   )

   work_table = Table(
      'work_table', meta,
      Column('id_event', Integer, primary_key = True),
      Column('id_user', Integer),
      Column('date_event', Integer),
      Column('name_object', String),
      Column('where_need', String),
      Column('Count_o', String),
      Column('who_ordered', String),
      Column('comments', String),
      Column('foto_id', String),
      Column ('last_edit', Integer)
   )

   log_tbl = Table(
      'log_tbl', meta,
      Column('id', Integer),
      Column('date', Integer),
      Column('message', String)
   )

   meta.create_all(engine)

