import os

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db_name = "wqdb.sqlite"
db_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_name)
db_engine = None

Base = declarative_base()

def connect_db(database=db_location):
	"""
		Just a helper function that sets up the database engine
	:return:
	"""
	global db_engine
	db_engine = sqlalchemy.create_engine('sqlite:///{}'.format(database))


def db_session(engine=db_engine):
	"""
		provides a Session to the database - can be run for each thing that needs a new session.
	:param engine:
	:return:
	"""
	return orm.sessionmaker(bind=engine)

water_quality_header_map = {
	"Temp": "temp",
	"pH": "ph",
	"SpCond": "sp_cond",
	"Sal": "salinity",
	"DO%": "dissolved_oxygen_percent",
	"DO": "dissolved_oxygen",
	"DEP25": "dep_25",
	"PAR": "par",
	"RPAR": "rpar",
	"TurbSC": "turbidity_sc",
	"CHL": "chl",
	# TODO: Missing other CHL
}

class WaterQualityFile(Base):
	"""
		This class gives us a framework to hang observations on so they can all be traced back to the same origin
	"""
	__tablename__ = 'water_quality_files'

	id= Column(Integer, primary_key=True)
	original_file_path = Column(String)
	processed_file_path = Column(String)


class WaterQuality(Base):
	__tablename__ = 'water_quality'

	id = Column(Integer, primary_key=True)

	# might need to move this to the "file" level - check data tables
	site_id = Column(Integer, ForeignKey('sites_.id'))
	site = relationship("Site", back_populates="records")

	water_quality_file_id = Column(Integer, ForeignKey('water_quality_files.id'))
	file = relationship("WaterQualityFile", back_populates="records")
	#date and time
	#still need adjusted values
	temp = Column(Float)
	ph = Column(Float)
	sp_cond = Column(Integer)
	salinity = Column(Float)
	dissolved_oxygen = Column(Float)
	dissolved_oxygen_percent = Column(Float)
	dep_25 = Column(Float)
	par = Column(Integer)
	rpar = Column(Integer)
	turbidity_sc = Column(Float)
	chl = Column(Float)
	chl_volts = Column(Float)


class Site(Base):
	id = Column(Integer, primary_key=True)
	name = Column(String)
