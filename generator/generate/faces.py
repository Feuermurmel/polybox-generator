import sys, math, functools
from lib import polyhedra, stellations, paths, export, util


def well_height(thickness, angle):
	if angle < util.tau / 4:
		return thickness / math.tan(angle)
	else:
		return 0


def get_inversion_points(length):
	"""
	Returns the inversion points for the teeth of an edge of the specified length.
	
	This function should return a list of numbers in the interval [0..length] describing at which points the inversion points between wells and teeth lie. Normally, the edge will start with a well at position 0. If It should start with a tooth, 0 needs to be included as an inversion point.
	"""
	
	teeth_per_unit = 3
	num_inversions = 2 * math.ceil(length * teeth_per_unit)

	return [i * length / num_inversions for i in range(1, num_inversions)]


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
