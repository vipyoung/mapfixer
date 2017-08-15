"Author: Sofiane"
"""
Class of all static methods needed in the project.
"""

import networkx as nx
from matplotlib import pyplot as plt
from matplotlib import collections as mc
import datetime
from scipy.spatial import cKDTree
import numpy as np
from collections import defaultdict
import operator
import math
import geopy
import geopy.distance

class GpsPoint:
	def __init__(self, vehicule_id=None, lon=None, lat=None, speed=None, timestamp=None, angle=None, traj_id=None):
			self.vehicule_id = int(vehicule_id) if vehicule_id != None else 0
			self.speed = float(speed) if speed != None else 0.0
			if timestamp != None:
				self.timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S+03')
			self.lon = float(lon)
			self.lat = float(lat)
			self.angle = float(angle)
			if traj_id != None:
				self.traj_id = traj_id

	def get_coordinates(self):
		"""
		return the lon,lat of a gps point
		:return: tuple (lon, lat)
		"""
		return (self.lat, self.lon)

	def get_lonlat(self):
		return (self.lon, self.lat)

	def set_traj_id(self, traj_id):
		self.traj_id = traj_id

	def __str__(self):
		return "bt_id:%s, speed:%s, timestamp:%s, lon:%s, lat:%s, angle:%s" % \
			   (self.vehicule_id, self.speed, self.timestamp, self.lon, self.lat, self.angle)

	def __repr__(self):
		return "bt_id:%s, speed:%s, timestamp:%s, lon:%s, lat:%s, angle:%s" % \
			   (self.vehicule_id, self.speed, self.timestamp, self.lon, self.lat, self.angle)


class methods:
	def __init__(self,):
		pass

	@staticmethod
	def draw_simple_roadnet(rn, showNodes=False):
		lines = [[s, t] for s, t in rn.edges()]
		lc = mc.LineCollection(lines, colors='black', linewidths=2)
		fig, ax = plt.subplots(facecolor='black', figsize=(14, 10))
		ax.add_collection(lc)
		ax.autoscale()
		if showNodes == True:
			plt.scatter([node[0] for node in rn.nodes()], [node[1] for node in rn.nodes()], s=30)
		plt.show()

	@staticmethod
	def draw_roadnet_with_edge_features(rn, discriminating_feature='maxspeed', showNodes=False):
		lines = [[s, t] for s, t in rn.edges()]
		colors = ['black' if rn[s][t][discriminating_feature] is not None else 'red' for s, t in rn.edges()]
		lc = mc.LineCollection(lines, colors=colors, linewidths=2)
		fig, ax = plt.subplots(facecolor='black', figsize=(14, 10))
		ax.add_collection(lc)
		ax.autoscale()
		if showNodes == True:
			plt.scatter([node[0] for node in rn.nodes()], [node[1] for node in rn.nodes()], s=30)
		plt.show()

	@staticmethod
	def is_point_in_bboxes(point, bboxes):
		"""
		Check if a point (lon, lat) is within a set of bboxes [[max_lon, max_lat, min_lon, min_lat]]
		:param point: lon, lat
		:param bboxes: [[max_lon, max_lat, min_lon, min_lat]]
		:return: Boolean
		"""

		# Case where bboxes are not defines, accept all points. Always return True
		if bboxes == None:
			return True

		lon, lat = point
		for bbox in bboxes:
			if lon <= bbox[0] + 0.002 and lon >= bbox[2] - 0.002 and lat <= bbox[1] + 0.002 and lat >= bbox[3] - 0.02:
				return True
		return False

	@staticmethod
	def load_data(fname='data/gps_data/gps_points.csv', BBOXES=None):
		"""
		Given a file that contains gps points, this method creates different data structures
		:param fname: the name of the input file, as generated by QMIC
		:return: data_points (list of gps positions with their metadata), raw_points (coordinates only),
		points_tree is the KDTree structure to enable searching the points space
		"""
		data_points = list()
		raw_points = list()

		with open(fname, 'r') as f:
			f.readline()
			for line in f:
				if len(line) < 10:
					continue
				vehicule_id, timestamp, lat, lon, speed, angle = line.split(',')
				if not methods.is_point_in_bboxes((float(lon), float(lat)), BBOXES):
					continue
				pt = GpsPoint(vehicule_id=vehicule_id, timestamp=timestamp, lat=lat, lon=lon, speed=speed, angle=angle)
				data_points.append(pt)
				raw_points.append(pt.get_coordinates())
		print 'nb points:', len(raw_points)
		points_tree = cKDTree(raw_points)
		return np.array(data_points), np.array(raw_points), points_tree


	@staticmethod
	def create_trajectories(input_fname='data/gps_data/gps_points_07-11.csv', waiting_threshold=5, BBOXES=None):
		"""
		return all trajectories.
		The heuristic is simple. Consider each users sorted traces not broken by more than 1 hour as trajectories.
		:param waiting_threshold: threshold for trajectory split expressed in seconds.
		:return: list of lists of trajectories
		"""

		data_points, raw_points, points_tree = methods.load_data(fname=input_fname, BBOXES=BBOXES)

		detections = defaultdict(list)
		for p in data_points:
			detections[p.vehicule_id].append(p)

		# compute trajectories: split detections by waiting_threshold
		print 'Computing trajectories'
		trajectories = []
		for btd, ldetections in detections.iteritems():
			points = sorted(ldetections, key=operator.attrgetter('timestamp'))
			source = 0
			prev_point = 0
			i = 1
			while i < len(points):
				delta = points[i].timestamp - points[prev_point].timestamp
				if delta.days * 24 * 3600 + delta.seconds > waiting_threshold:
					trajectories.append(points[source: i])
					source = i
				prev_point = i
				i += 1
			if source < len(points):
				trajectories.append(points[source: -1])
		return trajectories


	@staticmethod
	def create_gps_stream_from_data(gps_data_fname, BBOXES=None):
		"""
		Simple function to prepare the stream of points.
		:param DATA_PATH:
		:param FILE_CODE:
		:return:
		"""
		# Generate Trajectories
		trajectories = methods.create_trajectories(input_fname=gps_data_fname,
		                                           waiting_threshold=21, BBOXES=BBOXES)
		# Sort trajectories into a stream of points
		print 'Computing points stream'
		building_trajectories = dict()
		gps_point_stream = []
		for i, trajectory in enumerate(trajectories):
			for point in trajectory:
				point.set_traj_id(i)
				gps_point_stream.append(point)
		gps_point_stream = sorted(gps_point_stream, key=operator.attrgetter('timestamp'))
		return gps_point_stream


	@staticmethod
	def assign_gps_points_to_osm_clusters(osm_rn, gps_points, radius_meters=5):
		"""
		Right now, angle is not taken into account.
		:param osm_rn:
		:param gps_points:
		:return:
		"""
		assignment = defaultdict(list)
		print osm_rn.nodes()[:3]
		kd_index = cKDTree([c for c in osm_rn.nodes()])
		RADIUS_DEGREES = radius_meters * 10e-6
		clusters = osm_rn.nodes()
		for point in gps_points:
			nearest_cluster_indices = [clu_index for clu_index in
			                           kd_index.query_ball_point(x=point.get_lonlat(), r=RADIUS_DEGREES, p=2)]
			if len(nearest_cluster_indices) == 0:
				# The gps point doesn't match any of the OSM clusters
				continue
			pt = geopy.Point(point.get_coordinates())
			close_clusters_distances = [geopy.distance.distance(pt, geopy.Point(clusters[clu_index])).meters
			                            for clu_index in nearest_cluster_indices]
			closest_cluster_indx = nearest_cluster_indices[close_clusters_distances.index(min(close_clusters_distances))]
			assignment[closest_cluster_indx].append(point)

			# TODO: case in which we account for angles.
			# nearest_cluster_indices = [clu_index for clu_index in
		     #                       kd_index.query_ball_point(x=point.get_lonlat(), r=RADIUS_DEGREES, p=2)
		     #                       if math.fabs(
			# 		diffangles(point.angle, kd_index[clu_index].angle)) <= HEADING_ANGLE_TOLERANCE]

		return assignment

	@staticmethod
	def calculate_bearing(latitude_1, longitude_1, latitude_2, longitude_2):
		"""
		Got it from this link: http://pastebin.com/JbhWKJ5m
	   Calculation of direction between two geographical points
	   """
		rlat1 = math.radians(latitude_1)
		rlat2 = math.radians(latitude_2)
		rlon1 = math.radians(longitude_1)
		rlon2 = math.radians(longitude_2)
		drlon = rlon2 - rlon1

		b = math.atan2(math.sin(drlon) * math.cos(rlat2), math.cos(rlat1) * math.sin(rlat2) -
		               math.sin(rlat1) * math.cos(rlat2) * math.cos(drlon))
		return (math.degrees(b) + 360) % 360