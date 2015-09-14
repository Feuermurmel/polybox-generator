import os, numpy, enum
from lib import polyhedra


class Orientation(enum.Enum):
	all_inside = 'all_inside'
	all_outside = 'all_outside'
	concave = 'concave'


def get_polyhedron_orientation(polyhedron : polyhedra.Polyhedron):
	has_inside_vertices = False
	has_outside_vertices = False

	for i in polyhedron.faces:
		# All possible views of all vertices of this face.
		vertex_views = { k for j in i.face_cycle for k in j.vertex_cycle }
		transform_from_face = numpy.linalg.inv(polyhedra.face_coordinate_system(i))

		vertex_set = set(polyhedron.vertices) - vertex_views
		V = numpy.ones((4,len(vertex_set)))
		for j, v in enumerate(vertex_set):
			V[:3,j] = v.vertex_coordinate

		R = numpy.dot(transform_from_face, V)

		if numpy.any(R[2,:]) > 0:
			has_outside_vertices = True
		else:
			has_inside_vertices = True

	if not has_outside_vertices:
		return Orientation.all_inside
	elif not has_inside_vertices:
		return Orientation.all_outside
	else:
		return Orientation.concave


def main():
	dir = 'src/polyhedra'

	for i in os.listdir(dir):
		if i.endswith('.json'):
			path = os.path.join(dir, i)

			try:
				polyhedron = polyhedra.Polyhedron.load_from_json(path)
			except Exception as e:
				print('{}: {}'.format(path, repr(e)))
			else:
				print(path, get_polyhedron_orientation(polyhedron))


main()
