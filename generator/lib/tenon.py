import functools, numpy, operator
from lib import polyhedra, stellations, paths, linalg


def make_strip(t1, t2):
	h1 = paths.half_plane((t1, 0), (0, -1))
	h2 = paths.half_plane((t2, 0), (0,  1))
	return h1 & h2


class Tenon:
	"""
	"""

	def __init__(self, polyhedron):
		self._polyhedron = polyhedron
		self._stellation = stellations.Stellation(polyhedron)

	@property
	def polyhedron(self):
		"""
		Returns the underlying polyhedron.
		"""
		return self._polyhedron


	def _pulses(self, polyview):
		return self.pulses(polyview)


	def _make_teeth(self, polyview):
		Sm = []
		Sh = []

		for ti, dt, da in self._pulses(polyview):
			if da > 0:
				Sm.append(make_strip(ti, ti+dt))
			elif da < 0:
				Sh.append(make_strip(ti, ti+dt))

		A = paths.plane()
		Sm = functools.reduce(operator.__or__, Sm, ~A)
		Sh = functools.reduce(operator.__or__, Sh, ~A)

		return Sm, Sh


	def _teeth_length(self, polyview):
		d = self.thickness(polyview)
		theta = polyhedra.dihedral_angle(polyview, polyview.adjacent)

		if theta <= numpy.pi/2.0:
			hin = 0.0
		else:
			hin = d / numpy.tan(numpy.pi - theta)

		hout = d / numpy.sin(numpy.pi-theta)

		# Manual override
		return self.teeth_adapt(hin, hout)


	def _make_V(self, polyview):
		Sm, Sh = self._make_teeth(polyview)
		hin, hout = self._teeth_length(polyview)

		H = paths.half_plane((0,  0),    ( 1, 0))
		I = paths.half_plane((0,  hin),  ( 1, 0))
		O = paths.half_plane((0, -hout), (-1, 0))

		To = Sm / O
		Ti = Sh / I
		V = (H / Ti) | To

		return V, H


	def _face_V(self, polyview):
		v = polyhedra.get_planar_coordinates(polyview)
		n = len(v)

		V = []
		H = []

		for i, view in enumerate(polyview.face_cycle):
			Vi, Hi = self._make_V(view)

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


	def tenon(self, polyview):
		A = paths.plane()
		V, H = self._face_V(polyview)
		S = self._stellation.cones(polyview)
		Ri = [~(Vi & (Hi | Si)) for Vi, Hi, Si in zip(V,H,S)]
		R = functools.reduce(operator.__or__, Ri)

		return A / R



class RegularFingerTenon(Tenon):
	"""
	"""

	def __init__(self, polyhedron, thickness=0.08, number_teeth=8):
		super().__init__(polyhedron)
		self._thickness = thickness
		self._number_teeth = number_teeth

	def pulses(self, polyview):
		dx = 1.0 / self._number_teeth
		return [(i*dx, dx, (-1)**i) for i in range(self._number_teeth)]

	def teeth_adapt(self, hin, hout):
	        #hin = 0.05
		hout *= 2.0
		return hin, hout

	def thickness(self, polyview):
		return self._thickness
