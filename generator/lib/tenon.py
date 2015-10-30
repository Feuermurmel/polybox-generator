import functools, numpy, operator, abc
from lib import polyhedra, stellations, paths, linalg


class Tenon(metaclass = abc.ABCMeta):
	"""
	Implements the basic concept of a very general
	tenon structure along an edge of a polyhedron.
	"""

	def __init__(self):
		self._stellation = stellations.Stellation()


	def _fingers(self, polyview):
		return self.fingers(polyview)


	def _make_fingers(self, polyview):
		Sm = []
		Sh = []

		for ti, dt, da in self._fingers(polyview):
			if da > 0:
				Sm.append(paths.strip((ti,0), (dt,0)))
			elif da < 0:
				Sh.append(paths.strip((ti,0), (dt,0)))

		A = paths.plane()
		Sm = functools.reduce(operator.__or__, Sm, ~A)
		Sh = functools.reduce(operator.__or__, Sh, ~A)

		return Sm, Sh


	def _finger_length(self, polyview):
		d = self.thickness(polyview)
		theta = polyhedra.dihedral_angle(polyview, polyview.adjacent)

		# Is the finger length given or do we have to compute it
		hin, hout = self.finger_length(polyview)

		if hin is True:
			if theta <= numpy.pi/2.0:
				hin = 0.0
			else:
				hin = d / numpy.tan(numpy.pi - theta)
		if hout is True:
			hout = d / numpy.sin(numpy.pi-theta)

		# Manual override
		return self.finger_length_adapt(polyview, hin, hout)


	def _make_V(self, polyview):
		Sm, Sh = self._make_fingers(polyview)
		H = paths.half_plane((0,  0),    ( 1, 0))

		hin, hout = self._finger_length(polyview)

		if hin is not None:
			I = paths.half_plane((0,  hin),  ( 1, 0))
			Ti = Sh / I
		else:
			Ti = Sh
		if hout is not None:
			O = paths.half_plane((0, -hout), (-1, 0))
			To = Sm / O
		else:
			To = Sm

		# Clip the fingers and slots to desired length
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

	@abc.abstractmethod
	def thickness(self, polyview):
		"""
		Return the thickness of the material. This is usually a
		constant for the whole polyhedron but could in principle
		also vary per face.
		"""


	@abc.abstractmethod
	def fingers(self, polyview):
		"""
		Define the finger positions and widths via 'pulses'.
		Each pulse is a triple (x, dx, n) where 'x' is the
		starting point (0 <= x <= 1), 'dx' is the fingers width
		and 'n' the direction. Negative 'n' will give 'slots' while
		positive 'n' will give fingers. Return a list of pulses.
		"""


	def finger_length(self, polyview):
		"""
		Set the initial finger length before any clipping takes place.
		Return a pair 'slot depth' and 'finger length' in this order.
		A number value is used literally, while 'True' means we compute
		a sensible value and 'None' stands for infinitely long fingers.
		"""
		return (True, True)


	def finger_length_adapt(self, polyview, slotdepth, fingerlength):
		"""
		Adapt the computed 'slot depth' and 'finger length' if desired.
		Return again a pair 'slot depth' and 'finger length'.
		"""
		return (slotdepth, fingerlength)


	def finger_clip_contour(self, polyview):
		"""
		Additional polyline contour which is used for clipping the fingers
		after they got clipped along the edges of the stellation facet.
		NOTE: This feature is not yet implemented.
		"""
		pass


	def tenon(self, polyview):
		"""
		Compute the final tenon structure.

		:param polyview: The view defining the edge along which to compute the tenon.
		"""
		A = paths.plane()
		V, H = self._face_V(polyview)
		S = self._stellation.cones(polyview)
		Ri = [~(Vi & (Hi | Si)) for Vi, Hi, Si in zip(V,H,S)]
		R = functools.reduce(operator.__or__, Ri)

		return A / R




class RegularFingerTenon(Tenon):
	"""
	Computes a regular finger tenon joint.
	The number of fingers per edge is globally constant.
	"""

	def __init__(self, thickness=0.08, finger_count=8):
		"""
		:param polyhedron: The underlying polyhedron.
		:param thickness: The thickness of the material.
		:param finger_count: The sum of fingers and slots.
		"""
		
		super().__init__()
		
		self._thickness = thickness
		self._finger_count = finger_count

	def fingers(self, polyview):
		dx = 1.0 / self._finger_count
		return [(i*dx, dx, (-1)**i) for i in range(self._finger_count)]

	def thickness(self, polyview):
		return self._thickness

	def finger_length_adapt(self, polyview, slotdepth, fingerlength):
		fingerlength *= 2.0
		return slotdepth, fingerlength
