from . import tenon, polyhedra
import abc, collections, collections.abc


class Tenon(metaclass = abc.ABCMeta):
	@abc.abstractmethod
	def get_left_side(self, view : polyhedra.PolyhedronView):
		pass
	
	@abc.abstractmethod
	def get_right_side(self, view : polyhedra.PolyhedronView):
		pass


class FingerTenon(Tenon):
	def get_left_side(self):
		pass
	
	def get_right_side(self):
		pass


class HoleTenon(Tenon):
	def get_left_side(self):
		pass
	
	def get_right_side(self):
		pass


class HingeTenon(Tenon):
	def get_left_side(self):
		pass
	
	def get_right_side(self):
		pass


class OppositeTenon(Tenon):
	def __init__(self, decorated_tenon : Tenon):
		self._decorated_tenon = decorated_tenon
	
	def get_left_side(self, view : polyhedra.PolyhedronView):
		return self._decorated_tenon.get_right_side(view)
	
	def get_right_side(self, view : polyhedra.PolyhedronView):
		return self._decorated_tenon.get_left_side(view)


class ReversedTenon(Tenon):
	def __init__(self, decorated_tenon : Tenon):
		self._decorated_tenon = decorated_tenon
	
	def get_left_side(self, view : polyhedra.PolyhedronView):
		# TODO: Reverse returned value here
		return self._decorated_tenon.get_left_side(view)
	
	def get_right_side(self, view : polyhedra.PolyhedronView):
		# TODO: Reverse returned value here
		return self._decorated_tenon.get_right_side(view)


class Engraving(metaclass = abc.ABCMeta):
	@abc.abstractmethod
	def get_engraving(self, view : polyhedra.PolyhedronView):
		pass


class ImageEngraving(Engraving):
	def __init__(self, image_path : str):
		pass
	
	def get_engraving(self, view):
		pass


class LayeredEngraving(Engraving):
	def __init__(self, *engravings):
		self._engravings = engravings
	
	def get_engraving(self, view):
		res = []
		
		for i in self._engravings:
			pass # TODO: Insert magic.
		
		return res


class CanonicalizingPropertyMap:
	"""
	This is not a collections.abc.Mapping as it has no __len__ and __iter__.
	"""
	
	def __init__(self, canonicalization_fn, default_factory):
		self._canonicalization_fn = canonicalization_fn
		self._map = collections.defaultdict(default_factory)
	
	def __getitem__(self, item):
		return self._map[self._canonicalization_fn(item)]


class EngravingWithOrigin:
	def __init__(self, engraving : Engraving, origin : polyhedra.PolyhedronView):
		self.engraving = engraving
		self.origin = origin


class PolyhedronProperties:
	def __init__(self):
		self.scale_factor = 1


class FaceProperties:
	def __init__(self):
		self.material_thickness = None
		self.engraving_with_orientation = None
		self.omit = False


class VertexProperties:
	def __init__(self):
		pass


class EdgeProperties:
	def __init__(self):
		pass


class ViewProperties:
	def __init__(self):
		self.tenon = tenon


class Properties:
	def __init__(self):
		self.polyhedron_properties = PolyhedronProperties()
		
		# Indexed by the canonical face view.
		self.face_properties = CanonicalizingPropertyMap(FaceSelectionType._canonicalize_view, FaceProperties)
		
		# Indexed by the canonical edge view.
		self.edge_properties = CanonicalizingPropertyMap(EdgeSelectionType._canonicalize_view, EdgeProperties)
		
		# Indexed by the canonical vertex view.
		self.vertex_properties = CanonicalizingPropertyMap(VertexSelectionType._canonicalize_view, VertexProperties)
		
		# Indexed by the view.
		self.view_properties = CanonicalizingPropertyMap(lambda x: x, ViewProperties)


class Selection(metaclass = abc.ABCMeta):
	def __init__(self, properties : 'Properties', views : list):
		self._properties = properties
		self._views = views
	
	def material_thickness(self, thickness):
		for i in self._views:
			self._properties.face_properties[i].thickness = thickness
	
	def omit(self, omit = True):
		for i in self._views:
			self._properties.face_properties[i].omit = omit
	
	def engraving(self, engraving : Engraving):
		for i in self._views:
			self._properties.face_properties[i].engraving = EngravingWithOrigin(engraving, i)
	
	def tenon(self, tenon : Tenon, *, apply_to_opposite = True):
		for i in self._views:
			self._properties.view_properties[i].tenon = tenon
		
		if apply_to_opposite:
			for i in self._views:
				self._properties.view_properties[i.opposite].tenon = ReversedTenon(OppositeTenon(tenon))


class SelectionType(metaclass = abc.ABCMeta):
	@classmethod
	@abc.abstractmethod
	def _cast_view(cls, polyhedron : polyhedra.Polyhedron, element) -> polyhedra.PolyhedronView: pass
	
	@classmethod
	@abc.abstractmethod
	def _canonicalize_view(cls, view : polyhedra.PolyhedronView) -> polyhedra.PolyhedronView: pass
	
	@classmethod
	@abc.abstractmethod
	def _get_all_views(cls, polyhedron : polyhedra.Polyhedron) -> set: pass
	
	@classmethod
	def create_selection(cls, properties : Properties, polyhedron : polyhedra.Polyhedron, elements : tuple, invert : bool):
		"""
		Process a list of elements and cast each non-PolyhedronView-element using the specified function and create a selection of the specified type selecting those elements.
		"""
		
		if ... in elements:
			elements = []
			invert = not invert
		
		def cast(element):
			if isinstance(element, polyhedra.PolyhedronView):
				return element
			else:
				return cls._cast_view(polyhedron, element)
		
		views = list(map(cast, elements))
		
		if invert:
			views = cls._get_all_views(polyhedron) - set(map(cls._canonicalize_view, views))
		
		return Selection(properties, views)


class FaceSelectionType(SelectionType):
	@classmethod
	def _cast_view(cls, polyhedron, element):
		return polyhedron.face_by_id(element)
	
	@classmethod
	def _canonicalize_view(cls, view):
		representative_view, = [i for i in view.face_cycle if i in view.polyhedron.faces]
		
		return representative_view
	
	@classmethod
	def _get_all_views(cls, polyhedron):
		return polyhedron.faces


class EdgeSelectionType(SelectionType):
	@classmethod
	def _cast_view(cls, polyhedron, element):
		return polyhedron.edge_by_id(*element)
	
	@classmethod
	def _canonicalize_view(cls, view):
		representative_view, = [i for i in [view, view.opposite] if i in view.polyhedron.edges]
		
		return representative_view
	
	@classmethod
	def _get_all_views(cls, polyhedron):
		return polyhedron.edges


class VertexSelectionType(SelectionType):
	@classmethod
	def _cast_view(cls, polyhedron, element):
		return polyhedron.vertex_by_id(element)
	
	@classmethod
	def _canonicalize_view(cls, view):
		representative_view, = [i for i in view.vertex_cycle if i in view.polyhedron.vertices]
		
		return representative_view
	
	@classmethod
	def _get_all_views(cls, polyhedron):
		return polyhedron.vertices


class Settings:
	def __init__(self, properties : Properties, polyhedron : polyhedra.Polyhedron):
		self._properties = properties
		self._polyhedron = polyhedron
	
	def scale_factor(self, scale : float):
		self._properties.polyhedron_properties.scale_factor = scale
	
	def face(self, *faces, invert = False):
		"""
		Select one or more faces.
		
		:param faces: Each argument is either an int, which specifies a face by its id, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all faces not specified in elements.
		"""
		
		return FaceSelectionType.create_selection(self._properties, self._polyhedron, faces, invert)
	
	def edge(self, *edges, invert = False):
		"""
		Select one or more edges.
		
		:param edges: Each argument is either a tuple (a  int, b : int), which specifies an edge from vertex a to vertex b, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all edges not specified in elements.
		"""
		
		return EdgeSelectionType.create_selection(self._properties, self._polyhedron, edges, invert)
	
	def vertex(self, *vertices, invert = False):
		"""
		Select one or more edges.
		
		:param vertices: Each argument is either an int, which specifies a vertex by its idb, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all vertices not specified in elements.
		"""
		
		return VertexSelectionType.create_selection(self._properties, self._polyhedron, vertices, invert)
	
	@property
	def polyhedron(self):
		return self._polyhedron
