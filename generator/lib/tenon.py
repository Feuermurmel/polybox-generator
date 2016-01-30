import functools, numpy, operator, abc, math
from lib import polyhedra, stellations, paths, linalg, util


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

		if hout is True:
			#hout = d / numpy.sin(numpy.pi - theta)
			hout = d / numpy.tan(theta / 2.0)
		if hin is True:
			if theta <= numpy.pi/2.0:
				hin = 0.0
			else:
				#hin = d / numpy.tan(numpy.pi - theta)
				hin = hout * numpy.cos(numpy.pi - theta)

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
			if hin > 0:
				Ti = Sh / I
			else:
				Ti = Sh / (~I)
		else:
			Ti = Sh

		if hout is not None:
			O = paths.half_plane((0, -hout), (-1, 0))
			if hout > 0:
				To = Sm / O
			else:
				To = Sm / (~O)
		else:
			To = Sm

		# Clip the fingers and slots to desired length
		V = H
		if hin > 0:
			V /= Ti
		else:
			V |= Ti
		if hout > 0:
			V |= To
		else:
			V /= To

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

	def __init__(self,
		     thickness = 1.0,
		     finger_count = 5,
		     finger_length_factor = 1.0,
		     finger_length_add = 0.0,
		     slot_length_factor = 1.0,
		     slot_length_add = 0.0,
		     parity_flip = False):
		"""
		:param thickness: The thickness of the material.
		:param finger_count: The sum of fingers and slots.
		:param parity_flip: Flip the two twin parts of the tenon.
		"""
		super().__init__()
		self._thickness = thickness

		self._finger_count = int(finger_count)

		self._finger_length_factor = finger_length_factor
		self._finger_length_add = finger_length_add
		self._slot_length_factor = slot_length_factor
		self._slot_length_add = slot_length_add

		self._parity_flip = bool(parity_flip)

	def fingers(self, polyview):
		l = polyhedra.edge_length(polyview)
		dx = l / self._finger_count
		return [(i*dx, dx, (-1)**i) for i in range(self._finger_count)]

	def thickness(self, polyview):
		return self._thickness

	def finger_length_adapt(self, polyview, slotlength, fingerlength):
		fingerlength *= self._finger_length_factor
		fingerlength += self._finger_length_add
		slotlength *= self._slot_length_factor
		slotlength += self._slot_length_add
		return slotlength, fingerlength


class KerfCompensatedRegularFingerTenon(RegularFingerTenon):
	"""
	"""
	def __init__(self,
		     thickness = 1.0,
		     finger_count = 5,
		     kerf = 0.0):
		"""
		:param thickness: The thickness of the material.
		:param finger_count: The sum of fingers and slots.
		"""
		super().__init__(thickness, finger_count)
		self._kerf = kerf

	def fingers(self, polyview):
		l = polyhedra.edge_length(polyview)
		k = self._kerf
		dx = l / self._finger_count

		if k >= dx:
			raise ValueError("Kerf is larger than finger slot width.")

		fingers = []
		for i in range(self._finger_count):
			direction = (-1)**i
			if direction > 0:
				# Finger
				position = i*dx - k/2.0
				width = dx + k
			else:
				# Slot
				position = i*dx + k/2.0
				width = dx - k
			fingers.append((position, width, direction))
		return fingers

	def finger_length_adapt_kerf(self, slotdepth, fingerlength):
		k = self._kerf
		return slotdepth - k/2.0, fingerlength + k/2.0


class HoleTenon(Tenon):
	"""
	Computes a regular finger tenon joint.
	The number of fingers per edge is globally constant.
	"""

	def __init__(self,
		     thickness = 1.0,
		     finger_count = 5,
		     flip_fingers = False,
		     parity_flip = False):
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
		d = self.thickness(polyview.adjacent)
		theta = polyhedra.dihedral_angle(polyview, polyview.adjacent)
		_, l = self._finger_length(polyview.adjacent)

		if theta >= numpy.pi / 2:
			ca = l * numpy.cos(numpy.pi - theta)
			cb = d / numpy.cos(theta - numpy.pi / 2)
		elif theta < numpy.pi / 2:
			ca = 0
			cb = (l + d * numpy.tan(theta)) * numpy.cos(theta)
		cl = ca + cb

		S = paths.square()
		H = paths.half_plane((0, 0), (1, 0))

		Si = []
		for ti, dt, da in self.fingers(polyview):
			if da > 0:
				s = paths.scale(x=dt, y=-cl)
				m = paths.move(x=ti, y=ca)
				Si.append(m * s * S)

		A = paths.plane()
		Si = functools.reduce(operator.__or__, Si, ~A)
		Hs = paths.half_plane((0, -2*cb), (1, 0))
		V = Hs / Si

		return V, H


class HingeTenon(Tenon):
	"""
	Computes a regular finger tenon joint.
	The number of fingers per edge is globally constant.
	"""

	def __init__(self,
		     thickness = 1.0,
		     dl = 3,
		     w = 2,
		     dr = 1,
		     eps = 0.0,
		     edge_flip = False,
		     parity_flip = False):
		"""
		:param thickness: The thickness of the material.
		:param finger_count: The sum of fingers and slots.
		:param parity_flip: Flip the two twin parts of the tenon.
		"""
		super().__init__()
		self._thickness = thickness
		self._parity_flip = bool(parity_flip)

		# Hinge parameters
		self._dl = dl
		self._w = w
		self._dr = dr
		self._eps = eps

		# Flip along edge
		self._edge_flip = edge_flip


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
		d = self.thickness(polyview.adjacent)
		ri = math.sqrt(self._w**2 / 4 + d**2 / 4) + self._eps
		ro = ri + self._dr

		H = paths.half_plane((0, 0), (1, 0))

		s = paths.move(self._dl, -d/2.0)
		Co = s * paths.scale(ro) * paths.circle()
		Ci = s * paths.scale(ri) * paths.circle()

		V = (H | Co) / Ci

		if self._edge_flip:
			l = polyhedra.edge_length(polyview)
			m = paths.scale(x=-1)
			s = paths.move(x=l)
			V = s*m*V

		return V, H

	def _tenon_b(self, polyview):
		d = self.thickness(polyview) # sic
		ri = math.sqrt(self._w**2 / 4 + d**2 / 4) + self._eps
		ro = ri + self._dr

		d = self.thickness(polyview.adjacent)
		l = polyhedra.edge_length(polyview)
		t = d + self._eps
		b = l - (self._dl + ro + self._eps)

		H = paths.half_plane((0, 0), (1, 0))

		# Hinge axis
		A = paths.strip((0, 0), (self._w, 0))
		A /= (~H)
		t = paths.move(self._dl - self._w/2, -t)
		A = t * A

		# Rest
		B = paths.strip((0, 0), (b, 0))
		B /= (~H)
		t = paths.move(l-b, -d)
		B = t * B

		V = H | A | B

		if not self._edge_flip:
			m = paths.scale(x=-1)
			s = paths.move(x=l)
			V = s*m*V

		return V, H

	def fingers(self, polyview):
		# Unused abstract method :-/
		return None

	def thickness(self, polyview):
		# Unused abstract method :-/
		return self._thickness


class HingeTenonGeneral(Tenon):
	"""
	Computes a regular finger tenon joint.
	The number of fingers per edge is globally constant.
	"""

	def __init__(self,
		     thickness = 1.0,
		     dl = 3,
		     w = 2,
		     dr = 1,
		     eps = 0.1,
		     gamma = numpy.pi/2,
		     edge_flip = False,
		     parity_flip = False):
		"""
		:param thickness: The thickness of the material.
		:param finger_count: The sum of fingers and slots.
		:param parity_flip: Flip the two twin parts of the tenon.
		"""
		super().__init__()
		self._thickness = thickness
		self._parity_flip = bool(parity_flip)

		# Hinge parameters
		self._gamma = gamma
		self._dl = dl
		self._w = w
		self._dr = dr
		self._eps = eps

		# Flip along edge
		self._edge_flip = edge_flip


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
		d = self.thickness(polyview.adjacent)
		ri = math.sqrt(self._w**2 / 4 + d**2 / 4) + self._eps
		ro = ri + self._dr

		theta = polyhedra.dihedral_angle(polyview, polyview.adjacent)
		gamma = self._gamma

		# Incidence angle
		alpha = numpy.arccos(numpy.sqrt(numpy.cos(gamma)**2 + numpy.cos(theta)**2 * numpy.sin(gamma)**2))

		# Ellipse shift
		x = d / numpy.tan(alpha)
		S = paths.move(x, 0)
		S2 = paths.move(x/2, 0)

		# Ellipse distortion
		DCi = paths.scale(2*ri/numpy.sin(alpha), 2*ri)
		DCo = paths.scale(2*ro/numpy.sin(alpha), 2*ro)
		DMi = paths.scale(x, 2*ri)
		DMo = paths.scale(x, 2*ro)

		# Ellipse rotation
		sx = d / numpy.tan(gamma) / numpy.sin(theta)
		sy = d / numpy.tan(theta)
		r = numpy.arctan2(-sy, sx)
		R = paths.rotate(r)

		# Main figure o=o

		# Inner contour
		C1i  =      DCi * paths.scale(0.5) * paths.circle()
		C2i  = S  * DCi * paths.scale(0.5) * paths.circle()
		M12i = S2 * DMi * paths.move(-0.5, -0.5) * paths.square()
		EI = R * (C1i | M12i | C2i )

		# Outer contour
		C1o  =      DCo * paths.scale(0.5) * paths.circle()
		C2o  = S  * DCo * paths.scale(0.5) * paths.circle()
		M12o = S2 * DMo * paths.move(-0.5, -0.5) * paths.square()
		EO = R * (C1o | M12o | C2o )

		# Move
		s = paths.move(self._dl, -d/2.0)
		EI = s * EI
		EO = s * EO

		H = paths.half_plane((0, 0), (1, 0))

		V = (H | EO) / EI

		if self._edge_flip:
			l = polyhedra.edge_length(polyview)
			m = paths.scale(x=-1)
			s = paths.move(x=l)
			V = s*m*V

		return V, H

	def _tenon_b(self, polyview):
		d = self.thickness(polyview) # sic
		ri = math.sqrt(self._w**2 / 4 + d**2 / 4) + self._eps
		ro = ri + self._dr
		d = self.thickness(polyview.adjacent) # sic

		theta = polyhedra.dihedral_angle(polyview, polyview.adjacent)
		gamma = self._gamma

		# Incidence angle
		alpha = numpy.arccos(numpy.sqrt(numpy.cos(gamma)**2 + numpy.cos(theta)**2 * numpy.sin(gamma)**2))

		R = paths.rotate(numpy.pi/2 - self._gamma)

		l = polyhedra.edge_length(polyview)
		t = d / numpy.sin(self._gamma) + d/2 * numpy.abs(numpy.tan(numpy.pi/2 - self._gamma)) + self._eps

		H = paths.half_plane((0, 0), (1, 0))

		# Hinge axis
		A = paths.strip((-self._w/2, 0), (self._w, 0))
		A /= ~(paths.move(0, -t) * H)
		A = paths.move(self._dl, 0) * R * A

		x = d / numpy.tan(alpha)
		u = (d/2 + ro + self._eps) * numpy.cos(alpha)

		Q = paths.move(-0.5, -0.5) * paths.square()
		Q = paths.scale(2*ro/numpy.sin(alpha) + x + self._eps, 2*u) * Q
		Q = paths.move(self._dl, 0) * R * Q

		V = (H / Q) | A

		if not self._edge_flip:
			m = paths.scale(x=-1)
			s = paths.move(x=l)
			V = s*m*V

		return V, H

	def fingers(self, polyview):
		# Unused abstract method :-/
		return None

	def thickness(self, polyview):
		# Unused abstract method :-/
		return self._thickness


class NullTenon(Tenon):
	"""
	The null tenon represents a simple straight edge.
	"""

	def __init__(self,
		     thickness = 1.0):
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
