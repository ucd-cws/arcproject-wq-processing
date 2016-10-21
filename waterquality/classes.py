import os

import numpy

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db_name = "wqdb.sqlite"
db_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_name)
db_engine = None

Base = declarative_base()
Session = None


def _connect_db(database=db_location):
	"""
		Just a helper function that sets up the database engine
	:return:
	"""
	global db_engine
	if not db_engine:
		db_engine = sqlalchemy.create_engine('sqlite:///{}'.format(database))


def _db_session(engine=db_engine):
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


def get_new_session():
	_connect_db(database=db_location)
	return _db_session(engine=db_engine)


water_quality_header_map = {
	"Temp": "temp",
	"pH": "ph",
	"SpCond": "sp_cond",
	"Sal": "salinity",
	"DO_PCT": "dissolved_oxygen_percent",
	"DO": "dissolved_oxygen",
	"DEP25": "dep_25",
	"PAR": "par",
	"RPAR": "rpar",
	"TurbSC": "turbidity_sc",
	"CHL": "chl",
	"CHL_VOLTS": "chl_volts"
	# TODO: Missing other CHL
}

# commented out the following class because I'm not sure it's providing anything of use
#class WaterQualityFile(Base):
	"""
		This class gives us a framework to hang observations on so they can all be traced back to the same origin
	"""
#	__tablename__ = 'water_quality_files'

#	id= Column(Integer, primary_key=True)
#	original_file_path = Column(String)
#	processed_file_path = Column(String)

	# records = relationship("WaterQuality", backref="file")


class Site(Base):
	__tablename__ = "sites"

	id = Column(Integer, primary_key=True)
	name = Column(String)
	code = Column(String)

	# vertical_profiles = relationship("VerticalProfile", backref="site")
	# water_quality_records = relationship("WaterQuality", backref="site")


class ProfileSite(Base):
	__tablename__ = "profile_sites"

	id = Column(Integer, primary_key=True)

	site_id = Column(Integer, ForeignKey("sites.id"))
	site = relationship(Site,
						backref="profile_sites")


class VerticalProfile(Base):
	__tablename__ = "vertical_profiles"

	id = Column(Integer, primary_key=True)
	date = Column(Date)
	measured_chl = Column(Float)  # average by site/date for 1m

	_gain_setting = Column(Float)

	profile_site_id = Column(Integer, ForeignKey("profile_sites.id"))
	profile_site = relationship(ProfileSite,
								backref="vertical_profiles")

	@property
	def gain_setting(self):
		return self._gain_setting

	@gain_setting.setter
	def gain_setting(self, value_list):
		self._gain_setting = numpy.mean(value_list)


class Station(Base):
	__tablename__ = 'stations'

	id = Column(Integer, primary_key=True)
	code = Column(String)  # the station code


sample_field_map = {
	"Date": "date",
	"ID": "internal_id",
	"SiteID": "site_id",
	"LabNum": "lab_num",
	"EC": "ec",
	"pH": "ph",
	"Turbidity": "turbidity",
	"TP": "tp",
	"TDP": "tdp",
	"PO4P": "po4p",
	"TN": "tn",
	"TDN": "tdn",
	"NH4N": "nh4n",
	"NO3N": "no3n",
	"DOC": "doc",
	"TNTP": "tntp",
	"ChlorophyllA": "chlorophyll_a",
	"PheophytinA": "pheophytin_a",
	"PreHCl": "pre_hcl",
	"TSS": "tss",
	"VSS": "vss",
	"NOTES": "notes",
	"SOURCE": "source",
}


class GrabSample(Base):
	__tablename__ = 'grab_samples'

	id = Column(Integer, primary_key=True)
	internal_id = Column(String)
	date = Column(Date)

	station_id = Column(Integer, ForeignKey('stations.id'))
	station = relationship("Station",
					backref="grab_samples")

	site_id = Column(String)
	lab_num = Column(String)
	ec = Column(Float)
	ph = Column(Float)
	turbidity = Column(Float)
	tp = Column(Float)
	tdp = Column(Float)
	po4p = Column(Float)
	tn = Column(Float)
	tdn = Column(Float)
	nh4n = Column(Float)
	no3n = Column(Float)
	doc = Column(Float)
	tntp = Column(Float)
	chlorophyll_a = Column(Float)
	pheophytin_a = Column(Float)
	pre_hcl = Column(Float)
	tss = Column(Float)
	vss = Column(Float)
	notes = Column(String)
	source = Column(Float)


class WaterQuality(Base):
	"""
		Each instance of this class is an observation in the database
	"""
	__tablename__ = 'water_quality'

	id = Column(Integer, primary_key=True)

	site_id = Column(Integer, ForeignKey('sites.id'))
	site = relationship("Site",
						backref="water_quality_records")

	# water_quality_file_id = Column(Integer, ForeignKey('water_quality_files.id'))
	# file = relationship(WaterQualityFile,
	#					backref="water_quality_records")

	#date and time
	date_time = Column(DateTime)
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

	chl_corrected = Column(Float)  # this is the value that's corrected after running the regression.
	corrected_gain = Column(Float)  # storing this here in case we need it instead of joining back