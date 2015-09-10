import sys, functools
from lib import polyhedra, stellations, paths, export


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)

	c = paths.circle()

	def iter_stellations():
		for i, face in enumerate(polyhedron.faces):
			s = stellations.stellation_over_view(face)
			yield paths.move(i * 250) * ((paths.scale(200) * c) & (paths.scale(50) * s))

	stellation = functools.reduce(lambda x, y: x | y, iter_stellations())

	def write_line(line, *args):
		print(line.format(*args))

	write_line('import "../_laser_cutting" as _laser_cutting;')
	write_line('fill({}, red + white);', export.asymptote_expression(stellation))
	write_line('draw({}, black);', export.asymptote_expression(stellation))


main(*sys.argv[1:])
