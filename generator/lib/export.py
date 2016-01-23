import numpy, itertools, io, contextlib, json, svgwrite.path
from . import paths, util


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


class AsymptoteFile(File):
	def __init__(self, *args):
		super().__init__(*args)
		
		self._picture_stack_id_iter = itertools.count()
	
	def _serialize_path(self, path, closed):
		def iter_pairs():
			for x, y in path.vertices:
				yield self._serialize_value((x, y), False)
			
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
	
	def _serialize_length(self, value):
		return '{}mm'.format(self._serialize_value(value, False))
	
	def _serialize_value(self, value, close_paths):
		if isinstance(value, paths.Path):
			return self._serialize_path(value, closed = close_paths)
		elif isinstance(value, paths.Polygon):
			return self._serialize_array('path', value.paths, 1, True)
		elif isinstance(value, tuple):
			return '({})'.format(', '.join(map(self._serialize_length, value)))
		else:
			# Let str.format() deal with it.
			return value
	
	def _format_expression(self, expression, *args):
		return expression.format(*[self._serialize_value(i, False) for i in args])
	
	def declare_array(self, type, elements, depth = 1):
		return self._serialize_array(type, elements, depth, False)
	
	@contextlib.contextmanager
	def transform(self, expression, *args):
		id = next(self._picture_stack_id_iter)
		saved_name = '_currentpicture_stack_{}'.format(id)
		transform_name = '_currentpicture_transform_{}'.format(id)
		
		self.write('transform {} = {};', transform_name, self._format_expression(expression, *args))
		self.write('picture {} = currentpicture;', saved_name)
		self.write('currentpicture = new picture;')
		
		yield
		
		self.write('add({}, {} * currentpicture);', saved_name, transform_name)
		self.write('currentpicture = {};', saved_name)
	
	def write(self, statement, *args):
		"""
		Write a statement to the file.
		
		The specified statement is formatted with the specified arguments using str.format(). The following types of arguments are handled specially:
		
		- paths.Path (forming an open path)
		- paths.Polygon (forming an array of closed paths)
		
		Other types are serialized using the default behavior of str.format().
		"""
		
		self._write_line(self._format_expression(statement, *args))


class OpenSCADFile(File):
	def __init__(self, *args):
		super().__init__(*args)
		
		self._indentation_level = 0
	
	def line(self, line, *args):
		self._write_line('\t' * self._indentation_level + line.format(*args))
	
	@contextlib.contextmanager
	def group(self, module, *args, **kwargs):
		self.line('{} {{', self._format_call(module, args, kwargs))
		self._indentation_level += 1
		
		yield
		
		self._indentation_level -= 1
		self.line('}}')
	
	def call(self, module, *args, **kwargs):
		self.line('{};', self._format_call(module, args, kwargs))
	
	def polygon(self, polygon : paths.Polygon):
		vertices = []
		
		def save_vertex(v):
			index = len(vertices)
			
			vertices.append(v)
			
			return index
		
		paths = [[save_vertex(j) for j in i.vertices] for i in polygon.paths]
		
		self.call('polygon', vertices, paths)

	def text(self, string : str, size = 1.0, font = 'Liberation Sans', **kwargs):
		self.call('text', string, font=font, size=size, **kwargs)

	@classmethod
	def _serialize_expression(cls, expression):
		if isinstance(expression, (int, float, numpy.number)):
			return str(expression)
		elif isinstance(expression, (tuple, list, numpy.ndarray)):
			return '[{}]'.format(', '.join(map(cls._serialize_expression, expression)))
		elif isinstance(expression, str):
			return json.dumps(expression)
		else:
			raise Exception('Unsupported expression type: {}'.format(type(expression)))
	
	@classmethod
	def _format_call(cls, module, args, kwargs):
		return '{}({})'.format(module, ', '.join([cls._serialize_expression(i) for i in args] + ['{} = {}'.format(k, cls._serialize_expression(v)) for k, v in kwargs.items()]))


@contextlib.contextmanager
def writing_asymptote_file(path):
	with util.writing_text_file(path) as file:
		yield AsymptoteFile(file)


@contextlib.contextmanager
def writing_open_scad_file(path):
	with util.writing_text_file(path) as file:
		yield OpenSCADFile(file)


def _group(iterable, count):
	accu = []
	
	for i in iterable:
		if len(accu) >= count:
			yield accu
			
			accu = []
		
		accu.append(i)
	
	if accu:
		yield accu


def polygon_to_svg_path(polygon : paths.Polygon) -> svgwrite.path.Path:
	p = svgwrite.path.Path()
	
	for i in polygon.paths:
		command = 'M'
		
		for x, y in i.vertices:
			p.push(command, x, y)
			command = 'L'
		
		p.push('Z')
	
	return p
