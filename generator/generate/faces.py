import sys, functools, math, numpy
from lib import polyhedra, stellations, paths, export
from ._helpers import write_line


def arrange_shapes(shapes, size = 5, gap = 0.1):
	width = math.ceil(math.sqrt(len(shapes)))
	clip = paths.scale(size / 2) * paths.circle()
	
	def iter_arranged_shapes():
		for i, shape in enumerate(shapes):
			y, x = divmod(i, width)
			
			yield paths.move((size + gap) * x, -(size + gap) * y) * (shape & clip)
	
	return functools.reduce(lambda x, y: x | y, iter_arranged_shapes())


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	def iter_stellations():
		for face in polyhedron.faces:
			# TODO: Hack to get the offset of the view's vertex relative to the center of the view's face.
			c = -numpy.mean([[i.x, i.y] for i in polyhedra.get_planar_polygon(face).paths[0].vertices], 0)

			yield paths.move(*c) * stellations.stellation_over_face(face)



	def iter_faces():
		for face in polyhedron.faces:
			# TODO: Hack to get the offset of the view's vertex relative to the center of the view's face.
			c = -numpy.mean([[i.x, i.y] for i in polyhedra.get_planar_polygon(face).paths[0].vertices], 0)

			yield paths.move(*c) * polyhedra.get_planar_polygon(face)


	stellation = paths.scale(20) * arrange_shapes(list(iter_stellations()))
	faces = paths.scale(20) * arrange_shapes(list(iter_faces()))

	write_line('import "../_laser_cutting" as _laser_cutting;')
	write_line('fill({}, red + white);', export.asymptote_expression(stellation))
	write_line('draw({}, black);', export.asymptote_expression(stellation))
	write_line('draw({}, gray);', export.asymptote_expression(faces))


main(*sys.argv[1:])
