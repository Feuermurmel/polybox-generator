import sys
from ._helpers import *


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	write_line('use <../_util.scad>')
	
	with write_group('render()'):
		with write_group('intersection()'):
			for i in polyhedron.faces:
				write_half_space(i)


main(*sys.argv[1:])
