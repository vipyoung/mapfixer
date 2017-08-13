"""
Author: Sofiane
Let's find a good way to represent OSM data: graph and metadata.

"""
import json
import networkx as nx
from collections import defaultdict


class OSMReader():
	def __init__(self, osm_shapefile):
		self.shapefile = osm_shapefile
		pass

	@staticmethod
	def build_road_network_from_shapefile(shape_file):
		"""
		This function builds a road graph from road geojson file.
		:param shape_file: the road shape file of the city
		:return: a graph
		"""

		sh = json.load(open(shape_file))
		try:
			features = sh['features']
		except KeyError:
			print 'weired file format. Can not find feature attribute.'
			raise

		g = nx.DiGraph()
		line_points = defaultdict(list)
		line_properties = dict()
		for obj in features:
			try:
				line_properties[obj['properties']['id']] = obj['properties']
				path = obj['geometry']['coordinates']
				line_points[obj['properties']['id']] = path
				g.add_path(path)
				if obj['properties']['oneway'] == 0:
					path.reverse()
					g.add_path(path)
			except:
				continue
		return g, line_points, line_properties


if __name__ == '__main__':
	shapefile = '/home/sofiane/Downloads/doha_qatar.imposm-geojson/doha_qatar_roads.geojson'
	osmreader = OSMReader(osm_shapefile=shapefile)
	rn, line_points, line_properties = osmreader.build_road_network_from_shapefile(shapefile)
