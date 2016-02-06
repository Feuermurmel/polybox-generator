"""
This module can be * imported.
"""

from . import polyhedra as _polyhedra, config as _config, paths as _paths
import abc as _abc

from lib.tenon import Tenon, ReversedTenon, OppositeTenon, RegularFingerTenon


class Selection(metaclass = _abc.ABCMeta):
	def __init__(self, properties : _config.helpers.Properties, views : list):
		self._properties = properties
		self._views = views
	
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
	
	def face(self, *faces, invert = False) -> Selection:
		"""
		Select one or more faces.
		
		:param faces: Each argument is either an int, which specifies a face by its id, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all faces not specified in elements.
		"""
		
		return Selection(self._properties, _config.helpers.FaceSelectionType.parse_elements(self._polyhedron, faces, invert))
	
	def edge(self, *edges, invert = False) -> Selection:
		"""
		Select one or more edges.
		
		:param edges: Each argument is either a tuple (a  int, b : int), which specifies an edge from vertex a to vertex b, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all edges not specified in elements.
		"""
		
		return Selection(self._properties, _config.helpers.EdgeSelectionType.parse_elements(self._polyhedron, edges, invert))
	
	def vertex(self, *vertices, invert = False) -> Selection:
		"""
		Select one or more edges.
		
		:param vertices: Each argument is either an int, which specifies a vertex by its idb, or a polyhedra.PolyhedronView instance.
		:param invert: If set to true, return a selection for all vertices not specified in elements.
		"""
		
		return Selection(self._properties, _config.helpers.VertexSelectionType.parse_elements(self._polyhedron, vertices, invert))
	
	@property
	def polyhedron(self):
		return self._polyhedron
