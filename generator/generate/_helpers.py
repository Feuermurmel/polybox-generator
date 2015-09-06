import contextlib
from lib import polyhedra, util


def write_line(line, *args):
	print(line.format(*args))


@contextlib.contextmanager
def write_group(line, *args):
	write_line('{} {{', line.format(*args))
	yield
	write_line('}}')


def write_half_space(view : polyhedra.PolyhedronView, inside = True):
	a, b, c = (i.vertex_coordinate for i in view.face_cycle[:3])
	
	write_line('_half_space_from_vertices({}, {});', ', '.join(map(str, list(a) + list(b) + list(c))), [1, -1][inside])
