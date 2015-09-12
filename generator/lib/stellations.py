import functools, numpy, operator
from lib import polyhedra, paths, linalg


def stellation_over_edge(polyview):
	"""
	"""
	k1, k2, n = polyhedra.view_local_onb(polyview)
	u = polyview.vertex_coordinate

	opposite = polyview.opposite
	l1, l2, m = polyhedra.view_local_onb(opposite)
	yield (u, k1, -m)

	for face in opposite.face_cycle:
		neighbour = face.opposite

		l1, l2, m = polyhedra.view_local_onb(neighbour)
		v = neighbour.vertex_coordinate

		if not linalg.norm(numpy.cross(n, m)) < linalg.parallel_eps:
			s, r = linalg.intersect((u, k1, k2), (v, l1, l2))
			yield (s, r, m)


def line_to_face_coordinates(view, lines):
	"""
	"""
	# TODO: Factor out common face projection
	k1, k2, _ = polyhedra.view_local_onb(view)
	T = numpy.column_stack([k1, k2])
	P = linalg.projector([k1, k2])
	d = numpy.dot(P, view.vertex_coordinate).reshape((1,3))

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
