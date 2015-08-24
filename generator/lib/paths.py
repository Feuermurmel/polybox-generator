import math, abc, numpy, pyclipper
from . import util


class _Transformable(metaclass = abc.ABCMeta):
	@abc.abstractmethod
	def _transform(self, m : numpy.ndarray): pass


class Transformation(_Transformable):
	"""
	Represents a transformation which can be applied to a path.
	
	A transformation `t` can be applied to another transformation `t2` or a path `p` using `t * t2` or `t * p`.
	"""
	
	def __init__(self, m : numpy.ndarray):
		assert m.shape == (3, 3)
		
		self.m = m
	
	def __mul__(self, other : _Transformable):
		return other._transform(self.m)
	
	def _transform(self, m : numpy.ndarray):
		return type(self)(numpy.dot(m, self.m))


def transform(xx, yx, tx, xy, yy, ty):
	"""
	Create a transformation which transforms a vector `(x, y)` using the following polynom:
	
	(x', y') = (xx * x + yx * y + tx, xy * x + yy * y + ty)
	"""
	
	return Transformation(numpy.array([[xx, yx, tx], [xy, yy, ty], [0, 0, 1]]))


def rotate(angle):
	"""
	Returns a transformation which rotates a path around the origin by the specified angle.
	"""
	
	c = math.cos(angle)
	s = math.sin(angle)
	
	return transform(c, -s, 0, s, c, 0)


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
	
	return transform(x, 0, 0, 0, y, 0)


def move(x = 0, y = 0):
	"""
	Returns a transformation which moves a path by the specified amounts along the x and y axes.
	"""
	
	return transform(1, 0, x, 0, 1, y)


class Path(_Transformable):
	"""
	Represents an open path which can be transformed and exported to Asymptote and OpenSCAD.
	
	You can join two paths like this:
	
	>>> p1 = path([(0, 0), (1, 1)])
	>>> p2 = point([(2, 1)])
	>>> p1 + p2
	"""
	
	def __init__(self, m : numpy.ndarray):
		assert m.shape[0] == 3
		
		self.m = m
	
	def __add__(self, other):
		return join_paths([self, other])
	
	def __repr__(self):
		return 'Path({})'.format(self.m)
	
	def _transform(self, m : numpy.ndarray):
		return type(self)(numpy.dot(m, self.m))
	
	@property
	def vertices(self):
		"""
		A list of 2-tuples containing the coordinates of all points in this path.
		"""
		
		return [(x, y) for x, y, _ in self.m]


def _point(x, y, z):
	"""
	Returns a Path instance containing a single point at the specified coordinate.
	"""
	
	return Path(numpy.array([[x], [y], [z]]))


def point(x, y):
	"""
	Returns a Path instance containing a single point at the specified coordinate.
	"""
	
	return _point(x, y, 1)


def point_at_infinity(x, y):
	"""
	Returns a Path instance with a point located at an infinite distance of the origin in the direction specified by the vector `(x, y)`.
	"""
	
	return _point(x, y, 0)


def path(coordinates):
	"""
	Return a path using the specified coordinates.
	
	:param coordinates: An interable of 2-tuples of floats.
	"""
	
	return join_paths(point(*i) for i in coordinates)


def join_paths(paths):
	"""
	Join a sequence of paths.
	"""
	
	return Path(numpy.concatenate([i.m for i in paths], 1))


# def _project_infinities(coordinates):
	


class Polygon(_Transformable):
	"""
	Represents a polygon or set of polygons which can be transformed and operated on with some boolean and morphological operations and exported to Asymptote and OpenSCAD.
	
	You can operate on the area within the set of polygons like this:
	 
	>>> p1 = circle()
	>>> p2 = square()
	>>> p1 | p2 # Take the union.
	>>> p1 & p2 # Take the intersection.
	>>> p1 / p2 # Subtract p2 from p1.
	>>> p1 ^ p2 # Take the exclusive intersection.
	"""
	
	def __init__(self, paths):
		assert isinstance(paths, list)
		
		self.paths = paths
	
	def __or__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_UNION)
	
	def __and__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_INTERSECTION)
	
	def __xor__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_XOR)
	
	def __truediv__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_DIFFERENCE)
	
	def _combine(self, other : 'Polygon', operation):
		def scale_to(x):
			return round(x * (1 << 32))
		
		def scale_from(x):
			return x / (1 << 32)
		
		def scale(coordinates, fn):
			return [(fn(x), fn(y)) for x, y in coordinates]
		
		pc = pyclipper.Pyclipper()
		
		for i in self.paths:
			pc.AddPath(scale(i.vertices, scale_to), pyclipper.PT_SUBJECT, True)
		
		for i in other.paths:
			pc.AddPath(scale(i.vertices, scale_to), pyclipper.PT_CLIP, True)
		
		solution = pc.Execute(operation, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
		
		return type(self)([path(scale(i, scale_from)) for i in solution])
	
	def _transform(self, m : numpy.ndarray):
		return type(self)([i._transform(m) for i in self.paths])
	
	@property
	def finite(self):
		"""
		Returns whether none of the vertices of this polygon lie at infinite coordinates.
		"""
		
		return all(i.finite for i in self.paths)


def polygon(*paths):
	"""
	Create a polygon from a set of paths.
	
	Each of the specified paths is interpreted as being closed. If some of the polygons formed from paths overlap or a path self-intersects, a even-odd unwinding rule is applied to decide which parts belong to the area inside the final polygon.
	
	The arguments can either be Path instances or iterables of tuples. Any non-Path instance first wrapped using path().
	"""
	
	return Polygon([(i if isinstance(i, Path) else path(i)) for i in paths])


def circle(n = 64):
	"""
	Return a polygon approximating a circle using a regular polygon with the specified number of sides.
	"""
	
	def iter_points():
		for i in range(n):
			t = i * util.tau / n
			
			yield math.cos(t), math.sin(t)
	
	return polygon(iter_points())


def square():
	"""
	Return a unit square with the lower left corner placed at the origin.
	"""
	
	return polygon([(0, 0), (1, 0), (1, 1), (0, 1)])


def half_plane(anchor_x, anchor_y, normal_x, normal_y):
	"""
	Return a Polygon instance representing the half-plane which is delimited by the line through `(anchor_x, anchor_y)` and `(anchor_x - normal_y, anchor_y + normal_x)`. The specified normal is pointing outward of the polygon from that line.
	"""
	
	return point_at_infinity(-normal_y, normal_x) + point(anchor_x, anchor_y) + point_at_infinity(normal_y, -normal_x) + point_at_infinity(-normal_y, -normal_x)
