import sys, math, numpy
from lib import polyhedra, stellations, paths, export, util


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))
	
	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	file = export.AsymptoteFile(sys.stdout)
	file.write('import "../_faces.asy" as _;')
	
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	for face, (c, r) in zip(polyhedron.faces, arrange_grid(len(polyhedron.faces))):
		polygon = polyhedra.get_planar_polygon(face)
		centerx, centery = -numpy.mean(polygon.paths[0].vertices, 0)
		cut = stellations.stellation_over_face(face)
		
		with file.transform('shift(({}, {}) * 100mm) * scale(20)', c, r):
			file.write('transform t = shift(({}, {}) * 1mm);', centerx, centery)
			file.write('face({}, {}, t);', polygon, cut, c, r)
			
			for i, (x, y) in zip(face.face_cycle, polygon.paths[0].vertices):
				file.write('vertex(({}mm, {}mm), {}, t);', x, y, i.vertex_id)
