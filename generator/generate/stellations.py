import sys
from lib import polyhedra, util, export


@util.main
def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	
	file = export.OpenSCADFile(sys.stdout)
	file.line('use <../_util.scad>')
	
	with file.group('render'):
		for i in polyhedron.faces:
			with file.group('intersection'):
				with file.group('multmatrix', polyhedra.face_coordinate_system(i)):
					file.call('half_space')
				
				for j in i.face_cycle:
					with file.group('multmatrix', polyhedra.face_coordinate_system(j.opposite)):
						with file.group('scale', [1, 1, -1]):
							file.call('half_space')
