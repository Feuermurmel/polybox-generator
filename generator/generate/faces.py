import sys, math, numpy
from lib import polyhedra, stellations, paths, export, util


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))
	
	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	file = export.AsymptoteFile(sys.stdout)
	file.write('access "../_faces.asy" as faces;')
	
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	for face, (c, r) in zip(polyhedron.faces, arrange_grid(len(polyhedron.faces))):
		center = -numpy.mean(polyhedra.get_planar_polygon(face).paths[0].vertices, 0)
		
		polygon = paths.move(*center) * polyhedra.get_planar_polygon(face)
		cut = paths.move(*center) * stellations.stellation_over_face(face)
		
		file.write('faces.face({}, {}, {}, {});', polygon, cut, c, r)
