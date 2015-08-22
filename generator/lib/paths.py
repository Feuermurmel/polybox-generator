import math, numpy


class Transformation:
	"""
	Represents a transformation which can be applied to a path.
	
	A transformation `t` can be applied to another transformation `t2` or a path `p` using `t * t2` or `t * p`.
	"""
	
	def __init__(self, m : numpy.ndarray):
		self.m = m
	
	def __mul__(self, other):
		return type(other)(numpy.dot(self.m, other.m))


def rotate(angle):
	"""
	Returns a transformation which rotates a path around the origin by the specified angle.
	"""
	
	c = math.cos(angle)
	s = math.sin(angle)
	
	return Transformation(numpy.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]))


def scale(*args, x = 1, y = 1):
	"""
	Returns a transformation which scales a path around the origin by the specified amount.
	
	`scale(s)`: Scale uniformly by `s`.
	`scale(sx, sy)`: Scale by `sx` along the x axis and by `sy` along the y axis.
	`scale(x = sx)`: Scale along the x axis only.
	`scale(y = sy)`: Scale along the y axis only.
	"""
	
	if args:
		if len(args) == 1:
			args *= 2
		
		x, y = args
	
	return Transformation(numpy.array([[x, 0, 0], [0, y, 0], [0, 0, 1]]))


def move(x = 0, y = 0):
	"""
	Returns a transformation which moves a path by the specified amounts along the x and y axes.
	"""
	
	return Transformation(numpy.array([[1, 0, x], [0, 1, y], [0, 0, 1]]))


class Path:
	"""
	Represents a closed path which can be transformed and exported to Asymptote and OpenSCAD.
	
	Two paths `p1` and `p2` can be joined using `p1 + p2`.
	"""
	
	def __init__(self, m : numpy.ndarray):
		self.m = m
	
	def __add__(self, other):
		return join_paths([self, other])
	
	def __repr__(self):
		return 'Path({})'.format(self.m)


def point(x, y):
	"""
	Returns a path containing a single point at the specified coordinate.
	"""
	
	return Path(numpy.array([[x], [y], [1]]))


def join_paths(paths):
	"""
	Join a sequence of paths.
	"""
	
	return Path(numpy.concatenate([i.m for i in paths], 1))


def to_asymptote_path(path : Path):
	return ' -- '.join('({}mm, {}mm)'.format(x, y) for x, y, _ in path.m.T) + ' -- cycle'


def to_asymptote_paths(paths : list):
	return 'new path[] {{ {} }}'.format(', '.join(to_asymptote_path(i) for i in paths))


def to_openscad_polygon(path : Path):
	return 'polygon([{}]);'.format(', '.join('[{}, {}]'.format(x, y) for x, y, _ in path.m.T))
