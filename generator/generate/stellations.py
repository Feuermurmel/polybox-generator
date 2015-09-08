import sys
from ._helpers import *


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	write_line('use <../_util.scad>')
	
	with write_group('render()'):
		for i in polyhedron.faces:
			with write_group('intersection()'):
				write_half_space(i, False)
				
				for j in i.face_cycle:
					write_half_space(j.opposite)


main(*sys.argv[1:])
