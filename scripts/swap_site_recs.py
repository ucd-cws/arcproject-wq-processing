from waterquality import classes


def select_allrecs_siteid(session, site):
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
	q = session.query(s.id).filter(s.code == site_abbr.upper()).one()
	return q[0]


def swap_id(session, oldid, newid):
	recs = select_allrecs_siteid(session, oldid)
	for r in recs:
		r.site_id = int(newid)
	return recs


def main(current, desired, remove=False):

	# open new session
	session = classes.get_new_session()

	try:
		# get the current site id from abbrev
		old = lookup_siteid(session, current)
		new = lookup_siteid(session, desired)
		swap_id(session, old, new)

		if remove:
			s = classes.Site
			q = session.query(s).filter(s.id == old).one()
			print(q)
			session.remove(q)

		session.commit()
	finally:
		session.close()


main("LN", "UL", remove=False)