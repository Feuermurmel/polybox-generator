import sys
from lib import polyhedra, util, export


@util.main
def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	file = export.OpenSCADFile(sys.stdout)
	file.line('use <../_util.scad>')
	
	with file.group('render'):
		with file.group('intersection'):
			for i in polyhedron.faces:
				t = polyhedra.face_coordinate_system(i)
				
				with file.group('multmatrix', t):
					with file.group('scale', [1, 1, -1]):
						file.call('half_space')
