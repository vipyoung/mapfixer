from OSMReader import OSMReader
from methods import methods


gps_data_fname = '../kharita/data/data_2015-10-01.csv'
# Reading and preparing trajectory data.
roads_fname = '/home/sofiane/projects/data/overpass_doha_roads.geojson'

rn, line_points, line_properties = OSMReader.build_road_network_from_overpass_output(roads_fname)
gps_point_stream =  methods.create_gps_stream_from_data(gps_data_fname=gps_data_fname, BBOXES=None)
assignment = methods.assign_gps_points_to_osm_clusters(rn, gps_point_stream, radius_meters=7)
print 'total matched osm nodes:', len(assignment)
print 'total matched gps points:', sum([len(v) for v in assignment.values()])

def estimate_nb_lanes(points):
	"""
	Adapt the KDD'16 idea: project points into the perpendicular line to the cluster angle, build histogram, and decide
	on the number.
	We can also do Hierarchical Clustering on the points and try to find the best cut => number of lanes.
	Or think of a mixture of gaussian distributions.

	:param points: set of points
	:return: number of lanes (or vectors of number of lanes with their probabilities...)
	"""

