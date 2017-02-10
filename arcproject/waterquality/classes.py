import os

import numpy

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import Column, Integer, String, Float, Numeric, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship, validates

db_name = "wqdb.sqlite"
db_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_name)
Base = declarative_base()

class db_abstract(object):

	def connect_db(self, database=db_location):
		"""
			Just a helper function that sets up the database engine
		:return:
		"""
		db_engine = sqlalchemy.create_engine('sqlite:///{}'.format(database))
		return db_engine

	def db_session(self, engine):
		"""
			provides a Session to the database - can be run for each thing that needs a new session.
		:param engine:
		:return:
		"""

		Session = orm.sessionmaker(bind=engine, autoflush=False)
		Session.configure(bind=engine)

		return Session

# this structure is still a bit weird for SQLAlchemy, but much closer to how it should be and avoids the use of a global call.
db_abstract_container = db_abstract()
db_engine = db_abstract_container.connect_db(db_location)
Session = db_abstract_container.db_session(db_engine)

def get_new_session():
	"""
		A simple function that provides a new session object from the Session factory. Made a function because it used
		to have more code involved
	:return:
	"""
	return Session()


class Site(Base):
	__tablename__ = "sites"

	id = Column(Integer, primary_key=True)
	name = Column(String)
	code = Column(String, unique=True)

	# vertical_profiles = relationship("VerticalProfile", backref="site")
	# water_quality_records = relationship("WaterQuality", backref="site")

	@validates('code')
	def convert_upper(self, key, value):
		return value.upper()


class ProfileSite(Base):
	__tablename__ = "profile_sites"

	id = Column(Integer, primary_key=True)
	abbreviation = Column(String, unique=True)
	y_coord = Column(Float)
	x_coord = Column(Float)
	m_value = Column(Float)
	slough = Column(String, ForeignKey("sites.code"))
	site_id = relationship(Site, backref="profile_sites")

	@validates('abbreviation', 'slough')
	def convert_upper(self, key, value):
		return value.upper()

gain_water_quality_header_map = {
	"Temp": "temp",
	"pH": "ph",
	"SpCond": "sp_cond",
	"Sal": "salinity",
	"DO_PCT": "dissolved_oxygen_percent",
	"DO": "dissolved_oxygen",
	"DEP25": "dep_25",
	"DEPX": "dep_25",
	"PAR": "par",
	"RPAR": "rpar",
	"TurbSC": "turbidity_sc",
	"CHL": "chl",
	"CHL_VOLTS": "chl_volts",
	"WQ_SOURCE": "source",  # a None here means it'll skip it
	"Gain": "gain_setting",
	"Site": "profile_site_id",
	"Date_Time": "date_time",
}

class VerticalProfile(Base):
	__tablename__ = "vertical_profiles"
	__table_args__ = (UniqueConstraint('date_time', name='_time_uc'),)
	id = Column(Integer, primary_key=True)
	profile_site_id = Column(Integer, ForeignKey("profile_sites.id"))
	profile_site = relationship(ProfileSite,
								backref="vertical_profiles")
	gain_setting = Column(Float)
	date_time = Column(DateTime)
	temp = Column(Float)
	ph = Column(Float)
	sp_cond = Column(Float)
	salinity = Column(Float)
	dissolved_oxygen = Column(Float)
	dissolved_oxygen_percent = Column(Float)
	dep_25 = Column(Float)
	par = Column(Float)
	rpar = Column(Float)
	turbidity_sc = Column(Float)
	chl = Column(Float)  # raw measurement by sonde
	chl_volts = Column(Float)
	source = Column(String)

	@validates('profile_site_abbreviation')
	def convert_upper(self, key, value):
		return value.upper()


regression_field_map = {
	"Date": "date",
	"Gain": "gain",
	"Rsquared": "r_squared",
	"A_coeff": "a_coefficient",
	"B_coeff": "b_coefficient",
}

class Regression(Base):
	__tablename__ = "regression"

	id = Column(Integer, primary_key=True)
	date = Column(Date)
	gain = Column(Integer)
	r_squared = Column(Numeric(asdecimal=False, precision=8))
	a_coefficient = Column(Numeric(asdecimal=False, precision=8))
	b_coefficient = Column(Numeric(asdecimal=False, precision=8))

	__table_args__ = (UniqueConstraint('date', 'gain', name='_date_gain_uc'),
	                  CheckConstraint(gain.in_([0, 1, 10, 100]), name='_check_gains'))  # limits gains


sample_field_map = {
	"Date": "date",
	"Sample_ID": "sample_id",
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
	"PreHCL": "pre_hcl",
	"TSS": "tss",
	"VSS": "vss",
	"NOTES": "notes",
	"SOURCE": "source",
}


# class Station(Base):
# 	"""
# 		Stations are locations where= grab samples occur
# 	"""
# 	__tablename__ = 'stations'
#
# 	id = Column(Integer, primary_key=True)
# 	code = Column(String)  # the station code
# 	y_coord = Column(Numeric(asdecimal=False))
# 	x_coord = Column(Numeric(asdecimal=False))
#

class GrabSample(Base):
	__tablename__ = 'grab_samples'
	id = Column(Integer, primary_key=True)
	profile_site_id = Column(String, ForeignKey("profile_sites.id"))
	sample_id = Column(String)
	site_id = Column(String)
	date = Column(Date)
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
	source = Column(String)


water_quality_header_map = {
	"Temp": "temp",
	"pH": "ph",
	"SpCond": "sp_cond",
	"Sal": "salinity",
	"DO_PCT": "dissolved_oxygen_percent",
	"DO": "dissolved_oxygen",
	"DEP25": "dep_25",
	"DEPX": "dep_25",
	"PAR": "par",
	"RPAR": "rpar",
	"TurbSC": "turbidity_sc",
	"CHL": "chl",
	"CHL_VOLTS": "chl_volts",
	"Date_Time": "date_time",
	"WQ_SOURCE": "source",  # a None here means it'll skip it
	"GPS_SOURCE": None,
	"GPS_Time": None,
	"GPS_Date": None,
	"POINT_Y": "y_coord",
	"POINT_X": "x_coord",
}

class WaterQuality(Base):
	"""
		Each instance of this class is an observation in the database
	"""
	__tablename__ = 'water_quality'
	__table_args__ = (UniqueConstraint('date_time', name='_time_uc'),)

	id = Column(Integer, primary_key=True)
	site_id = Column(Integer, ForeignKey('sites.id'))
	site = relationship("Site", backref="water_quality_records")
	date_time = Column(DateTime)  # unique constraint - see __table_args__
	y_coord = Column(Float)  # currently assumes consistent projections
	x_coord = Column(Float)
	spatial_reference_code = Column(Integer)  # stores the ESPG/factory code for the coordinate system projection
	m_value = Column(Float)
	source = Column(String)
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
	notes = Column(String)