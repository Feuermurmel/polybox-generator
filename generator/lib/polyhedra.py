import json, numpy
from . import util


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
	
	def __init__(self, vertex_coordinate):
		self._vertex_coordinate = vertex_coordinate
		
		# These are filled by the Polyhedron.__init__()
		self._next_view = None
		self._opposite_view = None
	
	@property
	def vertex_coordinate(self):
		"""
		The coordinate of this view's vertex.
		"""
		
		return self._vertex_coordinate
	
	@property
	def next(self) -> 'PolyhedronView':
		"""
		Returns the second element of self.face_cycle.
		"""
		
		return self._next_view
	
	@property
	def opposite(self):
		"""
		Return the reversed view for this view's edge.
		
		This is the view containing the same edge the vertex at the end of the edge.
		"""
		
		return self._opposite_view
	
	@property
	def adjacent(self) -> 'PolyhedronView':
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


def edge_direction(view : PolyhedronView):
	"""
	The normalized vector pointing in the direction of the specified view's edge.
	"""

@property
def face_normal(view : PolyhedronView):
	"""
	The normalized vector representing the normal of the specified view's face pointing outwards of the polyhedron.
	"""


class Polyhedron:
	def __init__(self, vertices, faces):
		"""
		:param vertices: List of coordinate triples.
		:param faces: List of lists of vertex indexes.
		"""
		
		views_by_face = [[((j1, j2), PolyhedronView(vertices[j1])) for j1, j2 in zip(i, i[1:] + i[:1])] for i in faces]
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
	
	@classmethod
	def load_from_json(cls, path):
		with open(path, encoding = 'utf-8') as file:
			data = json.load(file)
		
		vertices = [numpy.array(i) for i in data['vertices']]
		faces = data['faces']
		
		return cls(vertices, faces)


def get_planar_polygon(view : PolyhedronView):
	"""
	Return the coordinates of the vertices of the specified view's face into a coordinate system which spans a plane through that face.
	
	The coordinate system is two-dimensional, right-angled and has the same unit length as the polyhedrons coordinate system.
	"""
	
	vertex_coordinates = [i.vertex_coordinate for i in view.face_cycle]
	a, b, c, *_ = vertex_coordinates
	k1 = util.normalize(b - a)
	k2 = util.normalize(numpy.cross(numpy.cross(b - a, c - b), k1))
	
	return [numpy.array([(numpy.dot(k1, v)), (numpy.dot(k2, v))]) for v in vertex_coordinates]