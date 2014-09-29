#!/usr/bin/python2

import sys
import io
import os

def shape_to_geojson_feature(coords, properties):
	coords = [c[::-1] for c in coords]
	geom = dict(type="LineString", coordinates=coords)
	feature = dict(
		type="Feature",
		geometry=geom,
		properties=properties)
	return feature

def geojson_marker(coords, properties):
	geom = dict(type="Point", coordinates=coords[::-1])
	feature = dict(
		type="Feature",
		geometry=geom,
		properties=properties)
	return feature


def geojson_feature_collection():
	output = dict(type="FeatureCollection")
	output['features'] = []
	return output

def dump_geojson_shapes(out_dir, good, bad=None, stats=None):
	from common import read_gtfs_shapes
	import json
	in_file = open(good)

	if bad is not None:
		bad = dict(read_gtfs_shapes(open(bad)))
	else:
		bad = {}

	index = []
	shapes = list(read_gtfs_shapes(in_file))
	
	if stats is not None:
		stats = [l.split(';') for l in open(stats)]
		def key(row):
			lik = row[1]
			if lik == "None":
				lik = 0
			else:
				lik = float(lik)
			return (-int(row[2]), lik)
		stats.sort(key=key)
		stats = ((row[0], row[1], row[2]) for row in stats)
	else:
		stats = ((row[0], None, None) for row in shapes)
	
	shapes = dict(shapes)

	#for shape_id, coords in shapes:
	for shape_id, likelihood, outliers in stats:
		coords = shapes[shape_id]
		col = geojson_feature_collection()
		if shape_id in bad:
			col['features'].append(shape_to_geojson_feature(bad[shape_id], dict(name=shape_id, stroke='red')))
		col['features'].append(shape_to_geojson_feature(coords, dict(name=shape_id, stroke='green')))
		col['features'].append(geojson_marker(coords[0], dict(name=shape_id + "/start", stroke='green')))

		filename = shape_id+".json"
		with open(os.path.join(out_dir, filename), 'w') as outfile:
			json.dump(col, outfile)
		index.append(dict(id=shape_id, file=filename, likelihood=likelihood, outliers=outliers))
	with open(os.path.join(out_dir, "index.json"), 'w') as outfile:
		json.dump(index, outfile)
	

if __name__ == '__main__':
	import argh
	argh.dispatch_command(dump_geojson_shapes)
