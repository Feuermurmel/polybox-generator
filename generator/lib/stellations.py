import functools, numpy, operator
from lib import polyhedra, paths, linalg


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


def make_strip(t1, t2):
	h1 = paths.half_plane((t1, 0), (0, -1))
	h2 = paths.half_plane((t2, 0), (0,  1))
	return h1 & h2


def pulses(polyview):
	return generate_pulses(polyview)


def make_teeth(polyview):
	Sm = []
	Sh = []

	for ti, dt, da in pulses(polyview):
		if da > 0:
			Sm.append(make_strip(ti, ti+dt))
		elif da < 0:
			Sh.append(make_strip(ti, ti+dt))

	A = paths.plane()
	Sm = functools.reduce(operator.__or__, Sm, ~A)
	Sh = functools.reduce(operator.__or__, Sh, ~A)

	return Sm, Sh


def teeth_length(polyview):
	d = 0.1

	theta = polyhedra.dihedral_angle(polyview, polyview.adjacent)

	if theta <= numpy.pi/2.0:
		hin = 0.0
	else:
		hin = d / numpy.tan(numpy.pi - theta)

	hout = d / numpy.sin(numpy.pi-theta)

	# Manual override
	#hin = 0.05
	#hout = 2.0

	return hin, hout


def make_V(polyview):
	Sm, Sh = make_teeth(polyview)
	hin, hout = teeth_length(polyview)

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

	V = []
	H = []

	for i, view in enumerate(polyview.face_cycle):
		Vi, Hi = make_V(view)

		# ugly linalg here
		a = v[i]
		b = v[(i+1)%n]
		k1 = b - a
		k2 = linalg.normalize(linalg.rot_ccw(k1))

		# General affine transform
		M = numpy.column_stack([k1, k2])
		T = paths.transform(M[0,0], M[0,1], a[0], M[1,0], M[1,1], a[1])

		V.append(T * Vi)
		H.append(T * Hi)

	return V, H


def stellation_over_face(polyview):
	A = paths.plane()
	V, H = face_V(polyview)
	S = stellation_over_view(polyview)
	Ri = [~(Vi & (Hi | Si)) for Vi, Hi, Si in zip(V,H,S)]
	R = functools.reduce(operator.__or__, Ri)

	return A / R


# def generate_pulses(polyview):
# 	return [(0.0, 0.1, -1),
# 		(0.1, 0.3,  1),
# 		(0.4, 0.1, -1),
# 		(0.5, 0.1,  1),
# 		(0.6, 0.3, -1),
# 		(0.9, 0.1,  1)]

def cantor_pair(k, l):
	return l + (k+l)*(k+l+1)//2

def bin_slots(n, w):
	chi = sum([1 << i for i in range(0, w, 2)])
	return numpy.array(list(map(int, numpy.binary_repr(n^chi, width=w))))

def antisymmetrize(f):
	return numpy.hstack([f, -f[::-1]])

def generate_pulses(polyview):
	edge = sorted(polyview._codata["edge"])
	N = polyview._codata["E"]
	N = int(numpy.ceil(numpy.log2(2*N**2)))
	C = cantor_pair(*edge)
	X = antisymmetrize(bin_slots(C, N))
	P = [(i*1/N/2, 1/N/2, x) for i, x in enumerate(X)]
	return P
