import sys
from lib import polyhedra
from ._helpers import write_line, write_call, write_group


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	write_line('use <../_util.scad>')
	
	with write_group('render'):
		with write_group('intersection'):
			for i in polyhedron.faces:
				t = polyhedra.face_coordinate_system(i)
				
				with write_group('multmatrix', t):
					with write_group('scale', [1, 1, -1]):
						write_call('half_space')
				


main(*sys.argv[1:])
