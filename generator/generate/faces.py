import sys, math, numpy
from lib import polyhedra, stellations, export, util, paths


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))

	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	file = export.AsymptoteFile(sys.stdout)
	file.write('import "../_faces.asy" as _;')
	
	# Both are in mm.
	scale = 20
	spacing = 100

	polyhedron = polyhedra.Polyhedron.load_from_json(src_path, scale)
	stellation = stellations.Stellation()
	boundary = paths.scale(spacing / 2) * paths.circle()

	for face, grid_pos in zip(polyhedron.faces, arrange_grid(len(polyhedron.faces))):
		polygon = polyhedra.get_planar_polygon(face)
		offset = -numpy.mean(polygon.paths[0].vertices, 0)
		facets = stellation.stellation(face)
		
		polygon = paths.move(*offset) * polygon
		facets = paths.move(*offset) * facets
		
		with file.transform('shift({} * {})', grid_pos, spacing):
			file.write('face({});', facets & boundary)
			file.write('face({});', polygon)
