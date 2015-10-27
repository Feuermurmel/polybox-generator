import functools, numpy, operator
from lib import polyhedra, paths, linalg


class Stellation:
	"""
	"""

	def __init__(self, polyhedron : polyhedra.PolyhedronView):
		self._polyhedron = polyhedron

	@property
	def polyhedron(self):
		"""
		Returns the underlying polyhedron.
		"""
		return self._polyhedron


	def _line_to_face_coordinates(self, view : polyhedra.PolyhedronView, lines):
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


	def _compute_halfplanes(self, lines):
		"""
		"""
		halfplanes = [paths.half_plane(s, linalg.rot_ccw(n)) for s, r, n in lines]
		return functools.reduce(operator.__and__, halfplanes)


	def _compute_stellation(self, polyview :  polyhedra.PolyhedronView, closed : bool = True):
		k1, k2, n = polyhedra.view_local_onb(polyview)
		u = polyview.vertex_coordinate

		opposite = polyview.opposite
		l1, l2, m = polyhedra.view_local_onb(opposite)
		if closed:
			yield (u, k1, -m)

		for face in opposite.face_cycle:
			neighbour = face.opposite

			l1, l2, m = polyhedra.view_local_onb(neighbour)
			v = neighbour.vertex_coordinate

			if not linalg.norm(numpy.cross(n, m)) < linalg.parallel_eps:
				s, r = linalg.intersect_planes((u, k1, k2), (v, l1, l2))
				yield (s, r, m)


	def _cone_over_edge(self, polyview : polyhedra.PolyhedronView):
		"""
		"""
		return self._compute_stellation(polyview, closed=False)


	def _cell_over_edge(self, polyview : polyhedra.PolyhedronView):
		"""
		stellation_over_edge(polyview)
		"""
		return self._compute_stellation(polyview, closed=True)


	def cones(self, polyview : polyhedra.PolyhedronView):
		"""
		"""
		cones = []

		for view in polyview.face_cycle:
			lines = self._cone_over_edge(view)
			lines = self._line_to_face_coordinates(polyview, lines)
			cones.append(self._compute_halfplanes(lines))

		return cones


	def cells(self, polyview : polyhedra.PolyhedronView):
		"""
		"""
		cells = []

		for view in polyview.face_cycle:
			lines = self._cell_over_edge(view)
			lines = self._line_to_face_coordinates(polyview, lines)
			cells.append(self._compute_halfplanes(lines))

		return cells


	def stellation(self, polyview : polyhedra.PolyhedronView):
		"""
		"""
		cells = self.cells(polyview)
		stellation = functools.reduce(operator.__xor__, cells)
		return stellation
