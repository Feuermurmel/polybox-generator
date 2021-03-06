import json, numpy
from . import linalg, paths


def _grab_view_cycle(view, fn):
	def iter_views():
		v = view
		
		while True:
			yield v
			
			v = fn(v)
			
			if v == view:
				break
	
	return list(iter_views())


class PolyhedronView:
	"""
	Represents the combination of a face, an adjacent edge and the vertex at the start of that edge when traversing the boundary of the face in positive order.
	"""

	def __init__(self, polyhedron : 'Polyhedron', vertex_id, edge_id, face_id):
		self._polyhedron = polyhedron
		self._vertex_id = vertex_id
		self._edge_id = edge_id
		self._face_id = face_id

		# These are filled by the Polyhedron.__init__()
		self._next_view = None
		self._opposite_view = None

	@property
	def polyhedron(self):
		"""
		Returns the underlying polyhedron.
		"""
		return self._polyhedron

	@property
	def vertex_id(self):
		"""
		Return the vertex identifier (unique per polyhedron).
		"""

		return self._vertex_id

	@property
	def edge_id(self):
		"""
		Return the edge identifier (unique per polyhedron).
		"""

		return self._edge_id

	@property
	def face_id(self):
		"""
		Return the face identifier (unique per polyhedron).
		"""

		return self._face_id

	@property
	def vertex_coordinate(self):
		"""
		The coordinate of this view's vertex.
		"""

		return self.polyhedron._vertex_coordinates[self._vertex_id]

	@property
	def next(self) -> 'PolyhedronView':
		"""
		Returns the second element of self.face_cycle.
		"""
		
		return self._next_view
	
	@property
	def opposite(self) -> 'PolyhedronView':
		"""
		Return the reversed view for this view's edge.
		
		This is the view containing the same edge the vertex at the end of the edge.
		"""
		
		return self._opposite_view
	
	@property
	def adjacent(self):
		"""
		Returns the second element of self.vertex_cycle.
		"""
		
		return self.opposite.next
	
	@property
	def face_cycle(self):
		"""
		A list of views for his view's face starting with this view and enumerating edges and vertices in positive order around this view's face.
		"""
		
		return _grab_view_cycle(self, lambda x: x.next)
	
	@property
	def vertex_cycle(self):
		"""
		A list of views for his view's vertex starting with this view and enumerating edges and faces in positive order around this view's vertex.
		"""
		
		return _grab_view_cycle(self, lambda x: x.adjacent)


def edge_vector(view : PolyhedronView):
	"""
	The vector pointing in the direction of the specified view's edge.
	"""

	a, b = [i.vertex_coordinate for i in [view, view.next]]

	return b - a


def edge_direction(view : PolyhedronView):
	"""
	The normalized vector pointing in the direction of the specified view's edge.
	"""

	v = edge_vector(view)

	return linalg.normalize(v)


def edge_length(view : PolyhedronView):
	"""
	The length of the specified view's edge.
	"""

	v = edge_vector(view)

	return linalg.norm(v)


def face_normal(view : PolyhedronView):
	"""
	The normalized vector representing the normal of the specified view's face pointing outwards of the polyhedron.
	"""
	
	a, b, c = [i.vertex_coordinate for i in [view, view.next, view.next.next]]

	return linalg.normalize(numpy.cross(b - a, c - b))


def view_local_onb(view : PolyhedronView):
	"""
	Construct a view-local orthonormal basis of `R^3` for the given view.
	"""

	a, b, c = [i.vertex_coordinate for i in [view, view.next, view.next.next]]
	k1 = linalg.normalize(b - a)
	k2 = linalg.normalize(numpy.cross(numpy.cross(b - a, c - b), k1))
	k3 = linalg.normalize(numpy.cross(k1, k2))

	return [k1, k2, k3]


def face_coordinate_system(view : PolyhedronView):
	"""
	Return a transformation matrix which, when applied to the homogeneous coordinates
	of a point in the coordinate system of a face, will transform those coordinates
	to the coordinate system of the polyhedron.

	The coordinate system of a face is defined as the right-angled, right-handed
	coordinate system whose origin is in the view's vertex, whose x-axis points
	along the view's edge and whose z-axis points in the direction of the view's
	faces' normal outwards of the polyhedron.
	"""

	return numpy.row_stack([numpy.column_stack(view_local_onb(view) + [view.vertex_coordinate]), [0, 0, 0, 1]])


def get_planar_coordinates(view : PolyhedronView):
	"""
	Return a paths.Polygon instance of the vertices of the specified view's face
	translated into a coordinate system which spans a plane through that face.

	The coordinate system is two-dimensional, right-angled and has the same unit
	length as the polyhedrons coordinate system. It's origin is at the view's
	vertex and it's x axis points along the view's edge.
	"""

	vertex_coordinates = [i.vertex_coordinate for i in view.face_cycle]
	k1, k2, _ = view_local_onb(view)
	P = linalg.projector([k1, k2])
	s = numpy.dot(P, vertex_coordinates[0])
	p = numpy.dot(numpy.array(vertex_coordinates) - s, numpy.column_stack([k1, k2]))
	
	return list(p)


def get_planar_polygon(view : PolyhedronView):
	"""
	Return a paths.Polygon instance of the vertices of the specified view's face translated into a coordinate system which spans a plane through that face.
	
	The coordinate system is two-dimensional, right-angled and has the same unit length as the polyhedrons coordinate system. It's origin is at the view's vertex and it's x axis points along the view's edge.
	"""
	
	vertex_coordinates = [i.vertex_coordinate for i in view.face_cycle]
	k1, k2, _ = view_local_onb(view)
	P = linalg.projector([k1, k2])
	s = numpy.dot(P, vertex_coordinates[0])
	p = numpy.dot(numpy.array(vertex_coordinates) - s, numpy.column_stack([k1, k2]))
	return paths.polygon(p)


def dihedral_angle(view1 : PolyhedronView, view2 : PolyhedronView):
	"""
	Compute the dihedral angle between two faces.
	"""
	n1 = face_normal(view1)
	n2 = face_normal(view2)
	theta = numpy.pi - numpy.arccos(numpy.dot(n1, n2))
	return theta


class Polyhedron:
	def __init__(self, vertices, faces):
		"""
		:param vertices: List of coordinate triples.
		:param faces: List of lists of vertex indexes.
		"""
		# Store numerical geometry data
		self._vertex_coordinates = vertices[:]

		# Store topology
		views_by_face = [[((j1, j2), PolyhedronView(self, j1, (j1,j2), fi))
				  for j1, j2 in zip(i, i[1:] + i[:1])]
				 for fi, i in enumerate(faces)]
		views_by_edge = dict(j for i in views_by_face for j in i)
		
		# Setup face cycles and opposite views.
		for i in views_by_face:
			for ((v1, v2), f1), (_, f2) in zip(i, i[1:] + i[:1]):
				f1._next_view = f2
				f1._opposite_view = views_by_edge[(v2, v1)]
		
		self._all_views = [v for i in views_by_face for _, v in i]
		self._faces = [i[0][1] for i in views_by_face]
		self._edges = [e for i in views_by_face for (v1, v2), e in i if v1 < v2]
		self._vertices = list({ v: f for i in views_by_face for (v, _), f in i }.values())
	
	@property
	def all_views(self):
		"""
		The set of all views, one for each edge of each face (thus counting each edge twice).
		"""
		
		return self._all_views
	
	@property
	def faces(self):
		"""
		A set of views with one view chosen arbitrarily for each face of the polyhedron.
		"""
		
		return self._faces
	
	@property
	def edges(self):
		"""
		A set of views with one view chosen arbitrarily for each edge of the polyhedron.
		"""
		
		return self._edges
	
	@property
	def vertices(self):
		"""
		A set of views with one view chosen arbitrarily for each vertex of the polyhedron.
		"""
		
		return self._vertices

	@property
	def vertex_count(self):
		"""
		Returns the number of vertices of the polyhedron.
		"""
		return len(self.vertices)
	
	@property
	def edge_count(self):
		"""
		Returns the number of edges of the polyhedron.
		"""
		return len(self.edges)
	
	@property
	def face_count(self):
		"""
		Returns the number of faces of the polyhedron.
		"""
		return len(self.faces)
	
	@classmethod
	def load_from_json(cls, path, scale=1):
		with open(path, encoding = 'utf-8') as file:
			data = json.load(file)

		vertices = [scale * numpy.array(i) for i in data['vertices']]
		faces = data['faces']
		
		return cls(vertices, faces)
