"""
Contains all the stuff needed by module settings but shouldn't be exported or documented in that module.
"""

from .. import tenon as _tenon, polyhedra as _polyhedra
import abc as _abc, collections as _collections


class SelectionType(metaclass = _abc.ABCMeta):
	@classmethod
	@_abc.abstractmethod
	def _cast_view(cls, polyhedron : _polyhedra.Polyhedron, element) -> _polyhedra.PolyhedronView: pass
	
	@classmethod
	@_abc.abstractmethod
	def _canonicalize_view(cls, view : _polyhedra.PolyhedronView) -> _polyhedra.PolyhedronView: pass
	
	@classmethod
	@_abc.abstractmethod
	def _get_all_views(cls, polyhedron : _polyhedra.Polyhedron) -> set: pass
	
	@classmethod
	def parse_elements(cls, polyhedron : _polyhedra.Polyhedron, elements : tuple, invert : bool):
		"""
		Process a list of elements and cast each element to a PolyhedronView element.
		"""
		
		if ... in elements:
			elements = []
			invert = not invert
		
		def cast(element):
			if isinstance(element, _polyhedra.PolyhedronView):
				return element
			else:
				return cls._cast_view(polyhedron, element)
		
		views = list(map(cast, elements))
		
		if invert:
			views = cls._get_all_views(polyhedron) - set(map(cls._canonicalize_view, views))
		
		return views


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


class CanonicalizingPropertyMap:
	"""
	This is not a collections.abc.Mapping as it has no __len__ and __iter__.
	"""
	
	def __init__(self, canonicalization_fn, default_factory):
		self._canonicalization_fn = canonicalization_fn
		self._map = _collections.defaultdict(default_factory)
	
	def __getitem__(self, item):
		return self._map[self._canonicalization_fn(item)]


class EngravingWithOrigin:
	def __init__(self, engraving, origin : _polyhedra.PolyhedronView):
		self.engraving = engraving
		self.origin = origin


class PolyhedronProperties:
	def __init__(self):
		self.scale_factor = 1


class FaceProperties:
	def __init__(self):
		self.material_thickness = 4
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
		self.tenon = _tenon.RegularFingerTenon()


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
