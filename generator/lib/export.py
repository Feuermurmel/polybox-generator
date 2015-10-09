import numpy, abc, itertools, io, contextlib
from . import paths, util


# TODO: Create subclass for OpenSCAD.
class File:
	"""
	Context manager which yields a File instance. The statements written to that instance are written to a file at the specified path.
	"""
	
	def __init__(self, file : io.TextIOBase):
		self.file = file
		self.variable_id_iter = itertools.count()
	
	def _write_line(self, line : str):
		print(line, file = self.file)
	
	def get_variable_name(self):
		return '_var_{}'.format(next(self.variable_id_iter))
	
	@abc.abstractmethod
	def write(self, statement, *args): pass


class AsymptoteFile(File):
	def _serialize_path(self, path, closed):
		def iter_pairs():
			for x, y in path.vertices:
				yield '({}mm, {}mm)'.format(x, y)
			
			if closed:
				yield 'cycle'
		
		variable = self.get_variable_name()
		
		self.write('path {};', variable)
		
		for i in _group(iter_pairs(), 500):
			self.write('{} = {} -- {};', variable, variable, ' -- '.join(i))
		
		return variable
	
	def _serialize_array(self, type, value, depth, close_paths):
		if depth:
			type += '[]' * depth
			variable = self.get_variable_name()
			
			self.write('{} {};', type, variable)
			
			for i in _group(value, 500):
				self.write('{}.append(new {} {{ {} }});', variable, type, ', '.join(self._serialize_array(type, j, depth - 1, close_paths) for j in i))
			
			return variable
		else:
			return self._serialize_value(value, close_paths)
	
	def _serialize_value(self, value, close_paths):
		if isinstance(value, paths.Path):
			return self._serialize_path(value, closed = close_paths)
		elif isinstance(value, paths.Polygon):
			return self._serialize_array('path', value.paths, 1, True)
		else:
			# Let str.format() deal with it.
			return value
	
	def declare_array(self, type, elements, depth = 1):
		return self._serialize_array(type, elements, depth, False)
	
	def write(self, statement, *args):
		"""
		Write a statement to the file.
		
		The specified statement is formatted with the specified arguments using str.format(). The following types of arguments are handled specially:
		
		- paths.Path (forming an open path)
		- paths.Polygon (forming an array of closed paths)
		
		Other types are serialized using the default behavior of str.format().
		"""
		
		self._write_line(statement.format(*[self._serialize_value(i, False) for i in args]))


@contextlib.contextmanager
def writing_asymptote_file(path):
	with util.writing_text_file(path) as file:
		yield AsymptoteFile(file)


def _group(iterable, count):
	accu = []
	
	for i in iterable:
		if len(accu) >= count:
			yield accu
			
			accu = []
		
		accu.append(i)
	
	if accu:
		yield accu


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
		_array(_array(map(str, i)) for i in vertices),
		_array(_array(map(str, i)) for i in paths))


def openscad_expression(expression):
	if isinstance(expression, (int, float, numpy.number)):
		return str(expression)
	elif isinstance(expression, (tuple, list, numpy.ndarray)):
		return '[{}]'.format(', '.join(map(openscad_expression, expression)))
	else:
		raise Exception('Unsupported expression type: {}'.format(type(expression)))
