import sys, math, numpy
from lib import polyhedra, stellations, paths, export, util


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))
	
	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	thickness = 0.08
	gap = 0.005
	file = export.OpenSCADFile(sys.stdout)
	
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	with file.group('render'):
		for face in polyhedron.faces:
			cut = stellations.stellation_over_face(face)
			t = polyhedra.face_coordinate_system(face)
			
			with file.group('multmatrix', t):
				with file.group('linear_extrude', thickness - gap):
					with file.group('offset', -gap / 2):
						file.polygon(cut)
