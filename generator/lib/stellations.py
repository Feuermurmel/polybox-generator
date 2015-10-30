import functools, numpy, operator
from lib import polyhedra, paths, linalg


class Stellation:
	"""
	Represents the (first, inner-most) stellation structure
	over a given polyhedron.
	"""


	def _compute_stellation(self, polyview : polyhedra.PolyhedronView, closed : bool = True):
		"""
		Compute the edges of a stellation cell as the intersections
		of the current face plane with all other (relevant) face planes
		of the polyhedron. To compute the facets that lie in the plane of
		the given face, it is sufficient to compute (parts of) the stellation
		cells of all neighbour faces and then select this facet.
		All computations take place in 3 dimensions.

		:param polyview: Select the center face and edge which then
		                 defines the stellation facet.
		:param closed: Add the edge of the face to close the cone to a cell.
		"""
		k1, k2, n = polyhedra.view_local_onb(polyview)
		u = polyview.vertex_coordinate

		opposite = polyview.opposite
		if closed:
			l1, l2, m = polyhedra.view_local_onb(opposite)
			yield (u, k1, -m)

		for face in opposite.face_cycle:
			neighbour = face.opposite

			l1, l2, m = polyhedra.view_local_onb(neighbour)
			v = neighbour.vertex_coordinate

			if not linalg.norm(numpy.cross(n, m)) < linalg.parallel_eps:
				s, r = linalg.intersect_planes((u, k1, k2), (v, l1, l2))
				yield (s, r, m)


	def _line_to_face_coordinates(self, view : polyhedra.PolyhedronView, lines):
		"""
		Project the lines from the last step into the plane (and local
		coordinate system) of the center face.

		:param view: Select the center face.
		:param lines: The lines defining the edges of the stellation facet.
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
		Compute the half-planes whose intersection yields
		the stellation facet.

		:param lines: The lines defining the edges of the stellation facet.
		"""
		halfplanes = [paths.half_plane(s, linalg.rot_ccw(n)) for s, r, n in lines]
		return functools.reduce(operator.__and__, halfplanes)


	def _cone_over_edge(self, polyview : polyhedra.PolyhedronView):
		"""
		Compute the open stellation cone over the edge
		of the given view. The cone lies in the same plane
		as the face.

		:param polyview: A view on the polyhedron.
		"""
		return self._compute_stellation(polyview, closed=False)


	def _cell_over_edge(self, polyview : polyhedra.PolyhedronView):
		"""
		Compute the closed stellation cell over the edge
		of the given view. The cell lies in the same plane
		as the face. Closing the cone with the edge yields
		the cell.

		:param polyview: A view on the polyhedron.
		"""
		return self._compute_stellation(polyview, closed=True)


	def cones(self, polyview : polyhedra.PolyhedronView):
		"""
		Compute all the open stellation cones over
		all edges of the given view. The cones lie in
		the same plane as the face.

		:param polyview: A view on the polyhedron.
		"""
		cones = []

		for view in polyview.face_cycle:
			lines = self._cone_over_edge(view)
			lines = self._line_to_face_coordinates(polyview, lines)
			cones.append(self._compute_halfplanes(lines))

		return cones


	def cells(self, polyview : polyhedra.PolyhedronView):
		"""
		Compute all the closed stellation cells over
		all edges of the given view. The cells lie in
		the same plane as the face.

		:param polyview: A view on the polyhedron.
		"""
		cells = []

		for view in polyview.face_cycle:
			lines = self._cell_over_edge(view)
			lines = self._line_to_face_coordinates(polyview, lines)
			cells.append(self._compute_halfplanes(lines))

		return cells


	def stellation(self, polyview : polyhedra.PolyhedronView):
		"""
		Compute the stellation figure in the plane
		of the face. The figure is just the (disjoint)
		union of all stellation facets.

		:param polyview: A view on the polyhedron.
		"""
		cells = self.cells(polyview)
		stellation = functools.reduce(operator.__xor__, cells)
		return stellation
