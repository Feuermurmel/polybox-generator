"""
This module can be * imported.
"""

from . import polyhedra as _polyhedra, config as _config, paths as _paths
import abc as _abc


class Tenon(metaclass = _abc.ABCMeta):
	@_abc.abstractmethod
	def get_left_side(self, view : _polyhedra.PolyhedronView):
		pass
	
	@_abc.abstractmethod
	def get_right_side(self, view : _polyhedra.PolyhedronView):
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
	
	def get_left_side(self, view : _polyhedra.PolyhedronView):
		return self._decorated_tenon.get_right_side(view)
	
	def get_right_side(self, view : _polyhedra.PolyhedronView):
		return self._decorated_tenon.get_left_side(view)


class ReversedTenon(Tenon):
	def __init__(self, decorated_tenon : Tenon):
		self._decorated_tenon = decorated_tenon

	def _mirror(self, tenon, view):
		l = _polyhedra.edge_length(view)
		V, H = tenon(view)
		V = _paths.move(x=l) * _paths.scale(x=-1) * V
		return V, H

	def get_left_side(self, view : _polyhedra.PolyhedronView):
		return self._mirror(self._decorated_tenon.get_left_side, view)

	def get_right_side(self, view : _polyhedra.PolyhedronView):
		return self._mirror(self._decorated_tenon.get_right_side, view)


class Engraving(metaclass = _abc.ABCMeta):
	@_abc.abstractmethod
	def get_engraving(self, view : _polyhedra.PolyhedronView):
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


class Selection(metaclass = _abc.ABCMeta):
	def __init__(self, properties : '_config.helpers.Properties', views : list):
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
			self._properties.face_properties[i].engraving = _config.helpers.EngravingWithOrigin(engraving, i)
	
	def tenon(self, tenon : Tenon, *, apply_to_opposite = True):
		for i in self._views:
			self._properties.view_properties[i].tenon = tenon
		
		if apply_to_opposite:
			for i in self._views:
				self._properties.view_properties[i.opposite].tenon = ReversedTenon(OppositeTenon(tenon))


class Settings:
	def __init__(self, properties : _config.helpers.Properties, polyhedron : _polyhedra.Polyhedron):
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
		
		return Selection(self._properties, _config.helpers.FaceSelectionType.parse_elements(self._polyhedron, faces, invert))
	
	def edge(self, *edges, invert = False):
		"""
		Select one or more edges.
		
		:param edges: Each argument is either a tuple (a  int, b : int), which specifies an edge from vertex a to vertex b, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all edges not specified in elements.
		"""
		
		return Selection(self._properties, _config.helpers.EdgeSelectionType.parse_elements(self._polyhedron, edges, invert))
	
	def vertex(self, *vertices, invert = False):
		"""
		Select one or more edges.
		
		:param vertices: Each argument is either an int, which specifies a vertex by its idb, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all vertices not specified in elements.
		"""
		
		return Selection(self._properties, _config.helpers.VertexSelectionType.parse_elements(self._polyhedron, vertices, invert))
	
	@property
	def polyhedron(self):
		return self._polyhedron
