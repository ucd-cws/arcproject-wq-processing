from arcproject.waterquality import classes
from sqlalchemy import exc, orm


def select_allrecs_siteid(session, site):
	"""
	select all water quality records for a given site id
	:param session:
	:param site: site id (not site code or abbreviation)
	:return:
	"""
	wq = classes.WaterQuality
	q = session.query(wq).filter(wq.site_id == site).all()
	return q


def lookup_siteid(session, site_abbr):
	"""
	Gets the site id from the abbreviation
	:param site_abbr: abbreviation for the site
	:return:
	"""
	s = classes.Site
	try:
		q = session.query(s.id).filter(s.code == site_abbr.upper()).one()
		return q[0]
	except orm.exc.NoResultFound:
		raise Exception("{} is not a valid current site code. Add to site table in database and try again.".format(site_abbr))


def recs_swap_id(session, oldid, newid, note=None):
	"""
	Swaps the site_ids for all the records that belong to the oldid, replacing with the new site id
	:param session:
	:param oldid: current id for the record
	:param newid: desired site
	:return:
	"""
	recs = select_allrecs_siteid(session, oldid)
	c = 0
	for r in recs:
		r.site_id = int(newid)
		r.notes = note
		c += 1
	return c


def main(current, desired, remove=False, note=None):
	"""
	Changes the assigned site for all records for a provided site abbreviation
	:param current: abbreviation of currently assigned site
	:param desired: abbreviation of the new site to assign to the records
	:param remove: optional - remove the original site for the sites table after changing the wq recs
	:param note: optional - new note to add to the wq record
	:return:
	"""
	# open new session
	session = classes.get_new_session()

	try:
		# get the current site id from abbrev
		old = lookup_siteid(session, current)
		new = lookup_siteid(session, desired)

		# add exception if trying to swap with self
		if old == new:
			raise Exception("Unable to swap with self")

		# swap old and new while returning the count of records updated.
		count = recs_swap_id(session, old, new, note)

		if remove:
			s = classes.Site
			q = session.query(s).filter(s.id == old).one()
			session.delete(q)

		session.commit()
	finally:
		session.close()
	return count
