from lib import polyhedra, util
from ._helpers import write_line, write_call, write_group


@util.main
def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	write_line('use <../_util.scad>')
	
	with write_group('render'):
		for i in polyhedron.faces:
			with write_group('intersection'):
				with write_group('multmatrix', polyhedra.face_coordinate_system(i)):
					write_call('half_space')
				
				for j in i.face_cycle:
					with write_group('multmatrix', polyhedra.face_coordinate_system(j.opposite)):
						with write_group('scale', [1, 1, -1]):
							write_call('half_space')
