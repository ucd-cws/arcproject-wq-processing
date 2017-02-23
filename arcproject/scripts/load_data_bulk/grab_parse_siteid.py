from arcproject.waterquality import classes

def main():
	"""
	Looks up the vertical profile site from grab.site_id and updates the grab_samples table if there is a match
	:return:
	"""
	# pull all records from grab samples
	grab = classes.GrabSample
	vp = classes.ProfileSite

	session = classes.get_new_session()
	try:
		query = session.query(grab).filter(grab.profile_site_id == None, grab.site_id != None).all()

		for g in query:
			# check if site id is in the profile sites table
			p = session.query(vp).filter(vp.abbreviation == g.site_id).one_or_none()

			if p is None:
				print("No profile site found for {}".format(g.site_id))
			else:
				print("Match found. {} is profile site # {}".format(g.site_id, p.id))
				g.profile_site_id = p.id
		session.commit()
	finally:
		session.close()

if __name__ == '__main__':
	main()
