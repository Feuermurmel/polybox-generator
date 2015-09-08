import numpy
from . import paths


def _asymptote_path_array(x, depth):
	def _array(seq):
		return '{{ {} }}'.format(', '.join(seq))
	
	def convert_path(element, closed):
		def iter_pairs():
			for i in element.vertices:
				if not i.finite:
					raise Exception('Path contains points at infinity: {}'.format(element))
				
				yield '({}mm, {}mm)'.format(i.x, i.y)
		
		res = ' -- '.join(iter_pairs())
		
		if closed:
			res += ' -- cycle'
		
		return res
	
	def convert_element(element, depth):
		if isinstance(element, paths.Vertex):
			assert depth == 0
			
			return convert_path(paths.point(element), False)
		if isinstance(element, paths.Path):
			assert depth == 0
			
			return convert_path(element, False)
		elif isinstance(element, paths.Polygon):
			assert depth == 1
			
			return _array(convert_path(i, True) for i in element.paths)
		else:
			return _array(convert_element(i, depth - 1) for i in element)
	
	if depth:
		prefix = 'new path' + '[]' * depth
	else:
		prefix = '(path)'
	
	return prefix + ' ' + convert_element(x, depth)


def asymptote_expression(x, array_depth = 1):
	"""
	Convert an object or a (possibly nested) list of objects to an Asymptote expression.
	
	The following types can be converted:
	- paths.Vertex (forming a path consisting of a single point)
	- paths.Path (forming an open path)
	- paths.Polygon (forming an array of closed paths)
	- Lists of all of the types in this list.
	
	Unless x is an instance of paths.Path or paths.Polygon, array_depth must be set to the depth of the generated path array. If x is a list, array_depth is assumed to be 1. This works for a list of paths.Path instances. If e.g. a list of paths.Polygon instances should be converted, array_depth needs to be set to 2.
	"""
	
	if isinstance(x, paths.Path):
		return _asymptote_path_array(x, 0)
	elif isinstance(x, paths.Polygon):
		return _asymptote_path_array(x, 1)
	else:
		return _asymptote_path_array(x, array_depth)


def openscad_polygon(polygon : paths.Polygon):
	def _array(seq):
		return '[{}]'.format(', '.join(seq))
	
	vertices = []
	
	def save_vertex(v):
		index = len(vertices)
		
		vertices.append(v)
		
		return index
	
	paths = [[save_vertex(j) for j in i.vertices] for i in polygon.paths]
	
	return 'polygon({}, {});'.format(
		_array(_array(map(str, [i.x, i.y])) for i in vertices),
		_array(_array(map(str, i)) for i in paths))


def openscad_expression(expression):
	if isinstance(expression, (int, float, numpy.number)):
		return str(expression)
	elif isinstance(expression, (tuple, list, numpy.ndarray)):
		return '[{}]'.format(', '.join(map(openscad_expression, expression)))
	else:
		raise Exception('Unsupported expression type: {}'.format(type(expression)))
