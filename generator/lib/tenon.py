import functools, numpy, operator, abc
from lib import polyhedra, stellations, paths, linalg


class WoodWorker():
	"""Combine different tenons, one for each edge, into
	the final piece structure for a given face.
	"""

	def __init__(self, tenonsource):
		"""
		:param tenonsource: Where the tenons for each edge are defined.
		"""
		self._stellation = stellations.Stellation()
		self._tenonsource = tenonsource


	def _edge_joints(self, polyview):
		"""
		:param polyview: A view on the polyhedron.
		"""
		v = polyhedra.get_planar_coordinates(polyview)
		n = len(v)

		V = []
		H = []

		for i, view in enumerate(polyview.face_cycle):
			# Decide which part to use for this edge
			ei = view.edge_id
			parity = ei[0] > ei[1]

			# Get the tenon
			tenon = self._tenonsource[view]
			Vi, Hi = tenon.tenon(view, parity)

			# ugly linalg here
			a = v[i]
			b = v[(i+1)%n]
			k1 = linalg.normalize(b - a)
			k2 = linalg.normalize(linalg.rot_ccw(k1))

			# General affine transform
			M = numpy.column_stack([k1, k2])
			T = paths.transform(M[0,0], M[0,1], a[0], M[1,0], M[1,1], a[1])

			V.append(T * Vi)
			H.append(T * Hi)

		return V, H


	def piece(self, polyview):
		"""
		Compute the final tenon structure of a piece.

		:param polyview: The view defining the face.
		"""
		A = paths.plane()
		V, H = self._edge_joints(polyview)
		S = self._stellation.cones(polyview)
		Ri = [~(Vi & (Hi | Si)) for Vi, Hi, Si in zip(V,H,S)]
		R = functools.reduce(operator.__or__, Ri)

		return A / R


class Tenon(metaclass = abc.ABCMeta):
	"""
	Implements the basic concept of a very general
	tenon structure along an edge of a polyhedron.
	"""

	def __init__(self):
		self._parity_flip = False


	def _make_fingers(self, polyview):
		"""
		:param polyview: A view on the polyhedron.
		"""
		Sm = []
		Sh = []

		for ti, dt, da in self.fingers(polyview):
			if da > 0:
				Sm.append(paths.strip((ti,0), (dt,0)))
			elif da < 0:
				Sh.append(paths.strip((ti,0), (dt,0)))

		A = paths.plane()
		Sm = functools.reduce(operator.__or__, Sm, ~A)
		Sh = functools.reduce(operator.__or__, Sh, ~A)

		return Sm, Sh


	def _finger_length(self, polyview):
		"""
		:param polyview: A view on the polyhedron.
		"""
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


	def tenon(self, polyview, parity=True):
		"""
		:param polyview: A view on the polyhedron.
		:param parity: Which of the two twin parts to take for the tenon.
		"""
		if parity != self._parity_flip:
			return self._tenon_a(polyview)
		elif parity == self._parity_flip:
			return self._tenon_b(polyview)
		else:
			raise ValueError("Invalid parity")


	def _tenon_a(self, polyview):
		"""
		Compute the tenon structure along a given edge, twin A part.

		:param polyview: A view on the polyhedron defining the edge.
		"""
		Sm, Sh = self._make_fingers(polyview)
		return self._tenon_common(polyview, Sm, Sh)


	def _tenon_b(self, polyview):
		"""
		Compute the tenon structure along a given edge, twin B part.

		:param polyview: A view on the polyhedron defining the edge.
		"""
		Sh, Sm = self._make_fingers(polyview)
		return self._tenon_common(polyview, Sm, Sh)


	def _tenon_common(self, polyview, Sm, Sh):
		"""
		Compute the tenon structure along a given edge.

		:param polyview: A view on the polyhedron defining the edge.
		:param Sm: Finger parts.
		:param Sh: Finger holes.
		"""
		H = paths.half_plane((0, 0), (1, 0))

		hin, hout = self._finger_length(polyview)

		if hin is not None:
			I = paths.half_plane((0, hin), (1, 0))
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
		starting point (0 <= x <= l), 'dx' is the fingers width
		and 'n' the direction. Negative 'n' will give 'slots' while
		positive 'n' will give fingers. The value 'l' is the edge
		length. Return a list of pulses.
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


class RegularFingerTenon(Tenon):
	"""
	Computes a regular finger tenon joint.
	The number of fingers per edge is globally constant.
	"""

	def __init__(self, thickness=0.08, finger_count=8, parity_flip=False):
		"""
		:param thickness: The thickness of the material.
		:param finger_count: The sum of fingers and slots.
		:param parity_flip: Flip the two twin parts of the tenon.
		"""
		super().__init__()
		self._thickness = thickness
		self._finger_count = int(finger_count)
		self._parity_flip = bool(parity_flip)

	def fingers(self, polyview):
		l = polyhedra.edge_length(polyview)
		dx = l / self._finger_count
		return [(i*dx, dx, (-1)**i) for i in range(self._finger_count)]

	def thickness(self, polyview):
		return self._thickness

	def finger_length_adapt(self, polyview, slotdepth, fingerlength):
		fingerlength *= 1.0
		return slotdepth, fingerlength


class HoleTenon(Tenon):
	"""
	Computes a regular finger tenon joint.
	The number of fingers per edge is globally constant.
	"""

	def __init__(self, thickness=0.08, finger_count=8, flip_fingers=False, parity_flip=False):
		"""
		:param thickness: The thickness of the material.
		:param finger_count: The sum of fingers and slots.
		:param parity_flip: Flip the two twin parts of the tenon.
		"""
		super().__init__()
		self._thickness = thickness
		self._finger_count = int(finger_count)
		self._flip_fingers = bool(flip_fingers)
		self._parity_flip = bool(parity_flip)

	def fingers(self, polyview):
		o = 0 if not self._flip_fingers else 1
		l = polyhedra.edge_length(polyview)
		dx = l / self._finger_count
		return [(i*dx, dx, (-1)**(i+o)) for i in range(self._finger_count)]

	def thickness(self, polyview):
		return self._thickness

	def finger_length_adapt(self, polyview, slotdepth, fingerlength):
		fingerlength *= 1.0
		return slotdepth, fingerlength


	def _tenon_a(self, polyview):
		"""
		Compute the tenon structure along a given edge, twin A part.

		:param polyview: A view on the polyhedron defining the edge.
		"""
		Sm, Sh = self._make_fingers(polyview)
		H = paths.half_plane((0, 0), (1, 0))

		hin, hout = self._finger_length(polyview)

		if hin is not None:
			I = paths.half_plane((0, hin), (1, 0))
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


	def _tenon_b(self, polyview):
		"""
		Compute the tenon structure along a given edge, twin B part.

		:param polyview: A view on the polyhedron defining the edge.
		"""
		d = self._thickness
		S = paths.square()
		H = paths.half_plane((0, 0), (1, 0))

		Sis = []
		for ti, dt, da in self.fingers(polyview):
			if da > 0:
				s = paths.scale(x=dt, y=-d)
				m = paths.move(x=ti, y=0)
				Si = m * s * S
				Sis.append(Si)

		A = paths.plane()
		Sis = functools.reduce(operator.__or__, Sis, ~A)

		Hs = paths.half_plane((0, -2*d), (1, 0))

		V = Hs / Sis

		return V, H


class NullTenon(Tenon):
	"""
	The null tenon represents a simple straight edge.
	"""

	def __init__(self, thickness=0.08):
		"""
		:param thickness: The thickness of the material.
		"""
		super().__init__()
		self._thickness = thickness

	def fingers(self, polyview):
		return []

	def thickness(self, polyview):
		return self._thickness

	def finger_length(self, polyview):
		return (0, 0)
