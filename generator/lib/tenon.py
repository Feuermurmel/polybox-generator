import functools, numpy, operator, abc
from lib import polyhedra, stellations, paths, linalg


class WoodWorker:
	"""
	Combine different tenons, one for each edge, into the final piece structure for a given face.
	"""

	def __init__(self, properties : 'config.helpers.Properties'):
		self._stellation = stellations.Stellation()
		self._properties = properties
	
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
			
			# Get the tenon
			tenon = self._properties.view_properties[view].tenon
			Vi, Hi = tenon.get_left_side(view, self._properties)

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
	@abc.abstractmethod
	def get_left_side(self, polyview, properties : 'config.helpers.Properties'):
		"""
		Compute the tenon structure along a given edge, twin A part.

		:param polyview: A view on the polyhedron defining the edge.
		"""

	@abc.abstractmethod
	def get_right_side(self, polyview, properties : 'config.helpers.Properties'):
		"""
		Compute the tenon structure along a given edge, twin B part.

		:param polyview: A view on the polyhedron defining the edge.
		"""


class OppositeTenon(Tenon):
	def __init__(self, decorated_tenon : Tenon):
		self._decorated_tenon = decorated_tenon
	
	def get_left_side(self, view, properties):
		return self._decorated_tenon.get_right_side(view, properties)
	
	def get_right_side(self, view, properties):
		return self._decorated_tenon.get_left_side(view, properties)


class ReversedTenon(Tenon):
	def __init__(self, decorated_tenon : Tenon):
		self._decorated_tenon = decorated_tenon
	
	def get_left_side(self, view, properties):
		return self._mirror(self._decorated_tenon.get_left_side, view, properties)

	def get_right_side(self, view, properties):
		return self._mirror(self._decorated_tenon.get_right_side, view, properties)
	
	@classmethod
	def _mirror(cls, tenon, view, properties):
		l = polyhedra.edge_length(view)
		V, H = tenon(view, properties)
		V = paths.move(x=l) * paths.scale(x=-1) * V
		return V, H


class BasicTenon(Tenon):
	"""
	Implements the basic concept of a very general
	tenon structure along an edge of a polyhedron.
	"""
	
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


	def _finger_length(self, polyview, properties : 'config.helpers.Properties'):
		"""
		:param polyview: A view on the polyhedron.
		"""
		d = properties.face_properties[polyview].material_thickness
		theta = polyhedra.dihedral_angle(polyview, polyview.adjacent)

		# Is the finger length given or do we have to compute it
		hin, hout = self.finger_length(polyview)

		if hout is True:
			hout = d / numpy.sin(numpy.pi - theta)
			#hout = d / numpy.tan(theta / 2.0)
		if hin is True:
			if theta <= numpy.pi/2.0:
				hin = 0.0
			else:
				hin = d / numpy.tan(numpy.pi - theta)
				#hin = hout * numpy.cos(numpy.pi - theta)

		# Manual override
		return self.finger_length_adapt(polyview, hin, hout)
	
	
	def get_left_side(self, polyview, properties : 'config.helpers.Properties'):
		Sm, Sh = self._make_fingers(polyview)
		return self._tenon_common(polyview, properties, Sm, Sh)


	def get_right_side(self, polyview, properties : 'config.helpers.Properties'):
		Sh, Sm = self._make_fingers(polyview)
		return self._tenon_common(polyview, properties, Sm, Sh)


	def _tenon_common(self, polyview, properties, Sm, Sh):
		"""
		Compute the tenon structure along a given edge.

		:param polyview: A view on the polyhedron defining the edge.
		:param Sm: Finger parts.
		:param Sh: Finger holes.
		"""
		H = paths.half_plane((0, 0), (1, 0))

		hin, hout = self._finger_length(polyview, properties)

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
	def fingers(self, polyview) -> list:
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
	

class RegularFingerTenon(BasicTenon):
	"""
	Computes a regular finger tenon joint.
	The number of fingers per edge is globally constant.
	"""

	def __init__(self,
			finger_count = 5,
			finger_length_factor = 1.0,
			finger_length_add = 0.0,
			slot_length_factor = 1.0,
			slot_length_add = 0.0):
		"""
		:param finger_count: The sum of fingers and slots.
		"""
		super().__init__()
		
		self._finger_count = int(finger_count)

		self._finger_length_factor = finger_length_factor
		self._finger_length_add = finger_length_add
		self._slot_length_factor = slot_length_factor
		self._slot_length_add = slot_length_add

	def fingers(self, polyview):
		l = polyhedra.edge_length(polyview)
		dx = l / self._finger_count
		return [(i*dx, dx, (-1)**i) for i in range(self._finger_count)]
	
	def finger_length_adapt(self, polyview, slotlength, fingerlength):
		fingerlength *= self._finger_length_factor
		fingerlength += self._finger_length_add
		slotlength *= self._slot_length_factor
		slotlength += self._slot_length_add
		return slotlength, fingerlength


# FIXME: Needs refactoring. Currently we have a circular dependency config.helpers.ViewProperties -> tenon -> config.helpers.Properties
# For type hints.
from lib import config
import lib.config.helpers
