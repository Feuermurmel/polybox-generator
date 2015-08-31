import math, abc, numpy, pyclipper
from . import util


class _Transformable(metaclass = abc.ABCMeta):
	@abc.abstractmethod
	def _transform(self, transformation : 'Transformation'): pass


class Transformation(_Transformable):
	"""
	Represents a transformation which can be applied to a path.
	
	A transformation `t` can be applied to another transformation `t2` or a path `p` using `t * t2` or `t * p`.
	"""
	
	def __init__(self, m : numpy.ndarray):
		assert m.shape == (3, 3)
		
		self.m = m
	
	def __mul__(self, other : _Transformable):
		return other._transform(self)
	
	def _transform(self, transformation):
		return type(self)(numpy.dot(transformation.m, self.m))
	
	@property
	def det(self):
		"""
		The determinant of this transformation's transformation matrix.
		"""
		
		return numpy.linalg.det(self.m)


def transform(xx, yx, tx, xy, yy, ty):
	"""
	Create a transformation which transforms a vector `(x, y)` using the following polynom:
	
	(x', y') = (xx * x + yx * y + tx, xy * x + yy * y + ty)
	"""
	
	return Transformation(numpy.array([[xx, yx, tx], [xy, yy, ty], [0, 0, 1]]))


def rotate(angle = None, *, turns = None):
	"""
	Returns a transformation which rotates a path around the origin by the specified angle.
	
	`rotate(x)`: Rotate by the angle given in radians.
	`rotate(turns = x)`: Rotate given by the angle given in multiples of full turns.
	"""
	
	if angle is None:
		angle = util.tau * turns
	
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


class Vertex(_Transformable):
	def __init__(self, x : float, y : float, finite : bool):
		self.x = x
		self.y = y
		self.finite = finite
	
	def __repr__(self):
		return 'Vertex({}, {}, finite = {})'.format(self.x, self.y, self.finite)
	
	def __add__(self, other : 'Vertex'):
		"""
		Add the coordinate of this point to the coordinate of the specified point.
		
		If one of the points is at infinity, the other point will be ignored. If both points are at infinity, an exception is raised.
		"""
		
		if self.finite:
			if other.finite:
				return type(self)(self.x + other.x, self.y + other.y, True)
			else:
				return other
		else:
			if other.finite:
				return self
			else:
				raise Exception('Cannot add two vertices at infinity.')
	
	def _transform(self, transformation):
		return path(self)._transform(transformation).vertices[0]


def vertex(x, y):
	"""
	Returns a vertex at the specified coordinates.
	"""
	
	return Vertex(x, y, True)


def vertex_at_infinity(x, y):
	"""
	Returns a vertex infinitely far away from the origin in the specified direction.
	"""
	
	assert x or y
	
	return Vertex(x, y, False)


def _cast_vertex(v):
	if not isinstance(v, Vertex):
		v = vertex(*v)
		
	return v


def _cast_direction_vertex(v):
	v = _cast_vertex(v)
	
	if v.finite:
		v = vertex_at_infinity(v.x, v.y)
	
	return v


class Path(_Transformable):
	"""
	Represents an open path which can be transformed and exported to Asymptote and OpenSCAD.
	
	You can join two paths like this:
	
	>>> p1 = path([(0, 0), (1, 1)])
	>>> p2 = path([(2, 1)])
	>>> p1 + p2
	"""
	
	def __init__(self, m : numpy.ndarray):
		s1, s2 = m.shape
		
		assert s1 == 3
		
		self.m = m
	
	def __add__(self, other):
		return join_paths([self, other])
	
	def __repr__(self):
		return 'Path({})'.format(self.m)
	
	def _transform(self, transformation):
		return type(self)(numpy.dot(transformation.m, self.m))
	
	@property
	def reversed(self):
		"""
		This path with the order of it's points reversed.
		"""
		
		return type(numpy.fliplr(self.m))
	
	@property
	def vertices(self):
		"""
		Return the vertices of this path as a list of Vertex instances.
		"""
		
		return [Vertex(x, y, bool(z)) for x, y, z in self.m.T]
	
	@property
	def finite(self):
		"""
		Returns whether none of the vertices in this path lie at infinite coordinates.
		"""
		
		return numpy.count_nonzero(self.m[2]) == self.m.shape[0]


def path(*vertices):
	"""
	Return a path using the specified coordinates.
	
	The arguments can either be `Vertex` instances or 2-tuples containing the arguments for `vertex()`.
	"""
	
	def iter_vertices():
		for v in vertices:
			v = _cast_vertex(v)
			
			yield v.x, v.y, v.finite
	
	return Path(numpy.array(list(iter_vertices())).T)


def line(anchor, direction):
	"""
	Return an infinite path representing the infinite line through the specified anchor and extending infinitely parallel to the specified direction infinitely in both directions infinitely.
	
	Infinitely.
	
	For suitable definitions of infinite.
	
	:param anchor: Vertex instance or tuple.
	:param direction: Vertex instance or tuple.
	"""
	
	anchor = _cast_vertex(anchor)
	direction = _cast_direction_vertex(direction)
	
	assert not direction.finite
	
	return path(scale(-1) * direction, anchor, direction)


def _cast_path(p):
	if not isinstance(p, Path):
		p = path(*p)
	
	return p


def join_paths(*paths):
	"""
	Join multiple paths into a single one.
	
	The arguments can either be `Path` instances or iterables of vertices. The vertices can be anything accepted by `path()`.
	"""
	
	return Path(numpy.concatenate([_cast_path(i).m for i in paths], 1))


# See http://www.angusj.com/delphi/clipper/documentation/Docs/Overview/Rounding.htm
_clipper_range = (1 << 62) - 1

# Chosen by fair dice roll.
_clipper_scale = 1 << 31
_clipper_infinity = _clipper_range / _clipper_scale


def _contains_point_at_infinity(m : numpy.ndarray):
	return numpy.count_nonzero(m[2]) < m.shape[0]


_infinity_quadrant_intersections = [
	(lambda px, py, dx, dy: (_clipper_infinity, py + (_clipper_infinity - px) * dy / dx), (_clipper_infinity, _clipper_infinity)),
	(lambda px, py, dx, dy: (px + (_clipper_infinity - py) * dx / dy, _clipper_infinity), (-_clipper_infinity, _clipper_infinity)),
	(lambda px, py, dx, dy: (-_clipper_infinity, py - (_clipper_infinity + px) * dy / dx), (-_clipper_infinity, -_clipper_infinity)),
	(lambda px, py, dx, dy: (px - (_clipper_infinity + py) * dx / dy, -_clipper_infinity), (_clipper_infinity, -_clipper_infinity))]


def _get_infinity_quadrant(x, y):
	"""
	Partitions the plane into 4 quadrants, rotated by tau / 8 relative to the quadrants of the coordinate system. Quadrants are numbered 0 through 3 and specify the four cones in the direction of the positive x axis, the positive y axis, the negative x axis and the negative y axis respectively.
	"""
	
	# Did I say that I like compact code?
	return 3 * (x < -y) ^ (x < y)


def _project_infinity(quadrant, point, direction):
	fn, _ = _infinity_quadrant_intersections[quadrant]
	px, py = point
	dx, dy = direction
	
	return fn(px, py, dx, dy)


def _get_infinity_quadrant_corner(quadrant):
	_, corner = _infinity_quadrant_intersections[quadrant]
	
	return corner


def _transform_to_clipper(m : numpy.ndarray):
	def iter_vertices():
		infos = [((x, y), None if finite else _get_infinity_quadrant(x, y)) for x, y, finite in m.T]
		
		for (p1, q1), (p2, q2) in zip(infos, infos[1:] + infos[:1]):
			if q2 is None:
				if q1 is not None:
					yield _project_infinity(q1, p2, p1)
				
				yield p2
			else:
				if q1 is None:
					yield _project_infinity(q2, p1, p2)
				else:
					# Iterate from q1 to q2 cyclically.
					for i in range(q1, (q2 - q1) % 4 + q1):
						yield _get_infinity_quadrant_corner(i % 4)
	
	def scale(x):
		# TODO: We should instead probably throw an exception if we get a value out of range here.
		return max(-_clipper_range, min(_clipper_range, round(_clipper_scale * x)))
	
	return [(scale(x), scale(y)) for x, y in iter_vertices()]


def _transform_from_clipper(vertices : list):
	def iter_coordinates():
		for x, y in vertices:
			px = x / _clipper_scale
			py = y / _clipper_scale
			finite = -_clipper_range < x < _clipper_range and -_clipper_range < y < _clipper_range
			
			yield px, py, finite
	
	return numpy.array(list(iter_coordinates())).T


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
	>>> ~p1 # Take the complement.
	"""
	
	def __init__(self, paths):
		assert isinstance(paths, list)
		
		self._paths = paths
	
	def __invert__(self):
		return plane() / self
	
	def __or__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_UNION)
	
	def __and__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_INTERSECTION)
	
	def __xor__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_XOR)
	
	def __truediv__(self, other : 'Polygon'):
		return self._combine(other, pyclipper.CT_DIFFERENCE)
	
	def _combine(self, other : 'Polygon', operation):
		pc = pyclipper.Pyclipper()
		
		for i in self.paths:
			pc.AddPath(_transform_to_clipper(i.m), pyclipper.PT_SUBJECT, True)
		
		for i in other.paths:
			pc.AddPath(_transform_to_clipper(i.m), pyclipper.PT_CLIP, True)
		
		solution = pc.Execute(operation, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
		
		return type(self)([Path(_transform_from_clipper(i)) for i in solution])
	
	def _transform(self, transformation):
		paths = [i._transform(transformation) for i in self.paths]
		
		if transformation.det < 0:
			# This transformation would change the winding direction of paths and would this invert parts of the polygon which have points at infinity. Thus we reverse all paths here.
			paths = [i.reversed for i in paths]
		
		return type(self)(paths)
	
	@property
	def paths(self):
		"""
		List of paths describing the boundaries of all disconnected parts of this polygon.
		"""
		
		return self._paths
	
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
	
	The arguments can either be `Path` instances or iterables of vertices. The vertices can be anything accepted by `path()`.
	"""
	
	return Polygon([_cast_path(i) for i in paths])


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


def half_plane(anchor, direction):
	"""
	Return a Polygon instance representing the half-plane which is delimited by the line through the specified anchor and running parallel to the specified direction. In the specified direction, the polygon is to the left of that line. 
	"""
	
	return polygon(line(anchor, direction))


def plane():
	"""
	The everything.
	"""
	
	return polygon([vertex_at_infinity(1, 0), vertex_at_infinity(-1, 0)])
