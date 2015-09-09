import sys, math, functools, numpy, operator
from lib import polyhedra, paths, linalg, export, util


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


def stellation_over_edge(polyview):
	"""
	"""
	k1, k2, n = polyhedra.local_coordinates(polyview)
	u = polyview.vertex_coordinate

	opposite = polyview.opposite
	l1, l2, m = polyhedra.local_coordinates(opposite)
	yield (u, k1, -m)

	for face in opposite.face_cycle:
		neighbour = face.opposite

		l1, l2, m = polyhedra.local_coordinates(neighbour)
		v = neighbour.vertex_coordinate

		if linalg.norm(numpy.cross(n, m)) < linalg.parallel_eps:
			print("Parallel faces detected")
			continue
		else:
			s, r = linalg.intersect((u, k1, k2), (v, l1, l2))
			yield (s, r, m)


def line_to_face_coordinates(view, lines):
	"""
	"""
	# TODO: Factor out common face projection
	k1, k2, _ = polyhedra.local_coordinates(view)
	T = numpy.column_stack([k1, k2])
	P = linalg.projector([k1, k2])
	d = numpy.dot(P, view.vertex_coordinate).reshape(1,3)

	for line in lines:
		s, r, n = line
		sp = numpy.dot(P, s) - d
		rp = numpy.dot(P, r) # = r
		np = numpy.dot(P, n)

		At = numpy.dot(numpy.row_stack([sp, rp, np]), T)
		yield map(lambda v: v.reshape(-1), numpy.vsplit(At,3))


def compute_halfplanes(lines):
	"""
	"""
	halfplanes = [paths.half_plane(s, linalg.rot_ccw(n)) for s, r, n in lines]
	return functools.reduce(operator.__and__, halfplanes)


def stellation_over_view(polyview):
	"""
	"""
	cells = []

	for view in polyview.face_cycle:
		lines = stellation_over_edge(view)
		lines = line_to_face_coordinates(polyview, lines)
		cells.append(compute_halfplanes(lines))

	stellation = functools.reduce(operator.__xor__, cells)
	return stellation


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)

	c = paths.circle()

	# def iter_polygons():
	# 	for i, face in enumerate(polyhedron.faces):
	# 		yield paths.scale(50) * paths.move(i * 5) * polyhedra.get_planar_polygon(face)

	# polygon = functools.reduce(lambda x, y: x | y, iter_polygons())

	def iter_stellations():
		for i, face in enumerate(polyhedron.faces):
			s = stellation_over_view(face)
			yield paths.move(i * 250) * ((paths.scale(200) * c) & (paths.scale(50) * s))

	stellation = functools.reduce(lambda x, y: x | y, iter_stellations())

	def write_line(line, *args):
		print(line.format(*args))

	write_line('import _laser_cutting;')
	write_line('fill({}, red + white);', export.asymptote_expression(stellation))
	write_line('draw({}, black);', export.asymptote_expression(stellation))


main(*sys.argv[1:])
