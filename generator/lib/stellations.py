import functools, numpy, operator
from lib import polyhedra, paths, linalg
from lib import util

def stellation_over_edge(polyview):
	"""
	"""
	k1, k2, n = polyhedra.view_local_onb(polyview)
	u = polyview.vertex_coordinate

	opposite = polyview.opposite
	l1, l2, m = polyhedra.view_local_onb(opposite)
	#yield (u, k1, -m)

	for face in opposite.face_cycle:
		neighbour = face.opposite

		l1, l2, m = polyhedra.view_local_onb(neighbour)
		v = neighbour.vertex_coordinate

		if not linalg.norm(numpy.cross(n, m)) < linalg.parallel_eps:
			s, r = linalg.intersect_planes((u, k1, k2), (v, l1, l2))
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


	#stellation = functools.reduce(operator.__xor__, cells)
	stellation = cells
	return stellation


def times():
	return [0.0, 0.1, 0.4, 0.5, 0.6, 0.9]


def make_strip(t1, t2):
	h1 = paths.half_plane((t1, 0), (0, -1))
	h2 = paths.half_plane((t2, 0), (0.001,  1))
	return h1 & h2


def make_teeth():
	A = make_strip(0, 1)

	Sm = []
	T = times()
	for t1, t2 in zip(T[::2], T[1::2]):
		Sm.append(make_strip(t1, t2))

	Sm = functools.reduce(operator.__or__, Sm)
	Sh = (~Sm) & A

	return Sm, Sh


def teeth_length():
	# TODO: Compute based on dihedral Angle
	hin = 0.05
	hout = 2.0

	return hin, hout


def make_V():
	Sm, Sh = make_teeth()
	hin, hout = teeth_length()

	H = paths.half_plane((0,  0),    ( 1, 0))
	I = paths.half_plane((0,  hin),  ( 1, 0))
	O = paths.half_plane((0, -hout), (-1, 0))

	To = Sm / O
	Ti = Sh / I
	V = (H / Ti) | To

	return V, H


def face_V(polyview):
	v = polyhedra.get_planar_coordinates(polyview)
	n = len(v)

	Vi, Hi = make_V()

	V = []
	H = []

	for i in range(n):
		# ugly linalg here
		a = v[i]
		b = v[(i+1)%n]
		k1 = b - a
		k2 = linalg.normalize(linalg.rot_ccw(k1))

		# General affine transform
		M = numpy.column_stack([k1, k2])
		tt = paths.transform(M[0,0], M[0,1], a[0], M[1,0], M[1,1], a[1])

		# Rotate and move
		#t1 = paths.rotate(turns=i/n)
		#t2 = paths.move(a[0], a[1])
		#tt = t2 * t1

		Vit = tt * Vi
		V.append(Vit)
		Hit = tt * Hi
		H.append(Hit)

	return V, H


def stellation_over_face(polyview):
	A = paths.plane()
	V, H = face_V(polyview)
	S = stellation_over_view(polyview)
	Ri = [~(Vi & (Hi | Si)) for Vi, Hi, Si in zip(V,H,S)]
	R = functools.reduce(operator.__or__, Ri)

	return A / R
