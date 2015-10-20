import sys
import numpy, numpy.linalg
from lib import polyhedra, stellations, export, util


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

			polygon = polyhedra.get_planar_polygon(face)
			vertices = polygon.paths[0].vertices
			center = -numpy.mean(vertices, 0)
			minr = numpy.amin([numpy.linalg.norm(v - center) for v in vertices])

			with file.group('multmatrix', t):
				with file.group('difference', None):
					with file.group('linear_extrude', thickness - gap):
						with file.group('offset', -gap / 2):
							file.polygon(cut)

					with file.group('translate', [-center[0], -center[1], 0.7 * thickness]):
						with file.group('linear_extrude', thickness):
							file.text(str(face.face_id), size=0.5 * minr, halign="center", valign="center")
