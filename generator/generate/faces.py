import sys, math, numpy
from lib import polyhedra, stellations, export, util, paths


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))

	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	file = export.AsymptoteFile(sys.stdout)
	file.write('import "../_faces.asy" as _;')

	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	stellation = stellations.Stellation(polyhedron)
	boundary = paths.scale(2.5) * paths.circle()

	for face, (c, r) in zip(polyhedron.faces, arrange_grid(len(polyhedron.faces))):
		polygon = polyhedra.get_planar_polygon(face)
		centerx, centery = -numpy.mean(polygon.paths[0].vertices, 0)
		facet = stellation.stellation(face)

		with file.transform('shift(({}, {}) * 100mm) * scale(20)', c, r):
			file.write('transform t = shift(({}, {}) * 1mm);', centerx, centery)
			file.write('face({}, t);', facet & (paths.move(-centerx, -centery) * boundary))
			file.write('face({}, t);', polygon)
