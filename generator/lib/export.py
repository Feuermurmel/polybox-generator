import collections, itertools, functools
from . import paths


def _asymptote_path_array(x, depth):
	def _array(seq):
		return '{{ {} }}'.format(', '.join(seq))
	
	def convert_path(element, closed):
		res = ' -- '.join('({}mm, {}mm)'.format(*i) for i in element.vertices)
		
		if closed:
			res += ' -- cycle'
		
		return res
	
	def convert_element(element, depth):
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
	
	return prefix + convert_element(x, depth)


def asymptote_expression(x, array_depth = 1):
	"""
	Convert an object or a (possibly nested) list of objects to an Asymptote expression.
	
	The following types can be converted:
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
	
	vertex_indices = collections.defaultdict(functools.partial(next, itertools.count()))
	paths = [[vertex_indices[j] for j in i.vertices] for i in polygon.paths]
	
	return 'polygon({}, {});'.format(
		_array(str(vertex_indices[i]) for i in range(len(vertex_indices))),
		_array(_array(map(str, i)) for i in paths))
