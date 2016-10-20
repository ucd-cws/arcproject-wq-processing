import os

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db_name = "wqdb.sqlite"
db_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_name)
db_engine = None

Base = declarative_base()
Session = None


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
	global Session

	if not Session:
		Session = orm.sessionmaker(bind=engine)
		Session.configure(bind=engine)

	return Session()

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

	# records = relationship("WaterQuality", backref="file")


class Site(Base):
	__tablename__ = "sites"

	id = Column(Integer, primary_key=True)
	name = Column(String)

	# vertical_profiles = relationship("VerticalProfile", backref="site")
	# water_quality_records = relationship("WaterQuality", backref="site")


class VerticalProfile(Base):
	__tablename__ = "vertical_profiles"

	id = Column(Integer, primary_key=True)
	date = Column(Date)
	measured_chl = Column(Float)  # average by site/date for 1m

	site_id = Column(Integer, ForeignKey("sites.id"))
	site = relationship(Site,
						primaryjoin=(site_id == Site.id),
						backref="vertical_profiles")


class WaterQuality(Base):
	"""
		Each instance of this class is an observation in the database
	"""
	__tablename__ = 'water_quality'

	id = Column(Integer, primary_key=True)

	# might need to move this to the "file" level - check data tables
	site_id = Column(Integer, ForeignKey('sites.id'))
	site = relationship("Site",
						primaryjoin=(site_id == Site.id),
						backref="water_quality_records")

	water_quality_file_id = Column(Integer, ForeignKey('water_quality_files.id'))
	file = relationship(WaterQualityFile,
						primaryjoin=(water_quality_file_id == WaterQualityFile.id),
						backref="water_quality_records")

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

	chl = Column(Float)  # raw measurement by sonde
	chl_volts = Column(Float)

	chl_corrected = Column(Float)  # this is the value that's corrected after running the regression.z