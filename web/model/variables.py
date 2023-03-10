from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

DBEngine = sqlalchemy.create_engine( "mysql+pymysql://lto:LTPs.sWRD@127.0.0.1:3306/um_archive?charset=utf8" )
TablePrefix = ""

Declarative_Base = declarative_base()

