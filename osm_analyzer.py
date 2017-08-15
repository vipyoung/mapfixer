from collections import Counter
from OSMReader import OSMReader
from matplotlib import pyplot as plt
from methods import methods

infile = '/home/sofiane/projects/data/overpass_doha_roads.geojson'
rn, line_points, line_properties = OSMReader.build_road_network_from_overpass_output(infile)
methods.draw_roadnet_with_edge_features(rn, discriminating_feature='maxspeed')





way_lanes = []
way_speeds = []
way_oneway = []
for k, v in line_properties.iteritems():
	way_lanes.append(v.get('lanes', None))
	way_speeds.append(v.get('maxspeed', None))
	way_oneway.append(v.get('oneway', None))

cnt = Counter(way_lanes)
cnt = cnt.most_common()
plt.figure(figsize=(12,6))
plt.bar(range(len(cnt)), [v[1] for v in cnt], width=1/1, color="blue", align='center')
plt.xticks(range(len(cnt)), [v[0] for v in cnt], fontsize=12)
plt.ylabel('Number of OSM ways')
plt.xlabel('OSM Lanes Label')
#plt.savefig('/home/sofiane/papers/1.in_preparation/mapMetadata/figs/osm_nb_lanes.pdf', format='PDF')

cnt = Counter(way_speeds)
cnt = cnt.most_common()
plt.figure(figsize=(18,6))
plt.bar(range(len(cnt)), [v[1] for v in cnt], width=1/1, color="blue", align='center')
plt.xticks(range(len(cnt)), [v[0] for v in cnt], fontsize=12)
plt.ylabel('Number of OSM ways')
plt.xlabel('OSM Speed Label')
#plt.savefig('/home/sofiane/papers/1.in_preparation/mapMetadata/figs/osm_nb_speeds.pdf', format='PDF')

cnt = Counter(way_oneway)
cnt = cnt.most_common()
plt.figure(figsize=(9, 6))
plt.bar(range(len(cnt)), [v[1] for v in cnt], width=1/1, color="blue", align='center')
plt.xticks(range(len(cnt)), [v[0] for v in cnt], fontsize=12)
plt.ylabel('Number of OSM ways')
plt.xlabel('OSM One-Way Label')
#plt.savefig('/home/sofiane/papers/1.in_preparation/mapMetadata/figs/osm_oneways.pdf', format='PDF')

