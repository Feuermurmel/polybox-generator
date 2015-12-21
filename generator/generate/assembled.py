import sys, numpy
from lib import polyhedra, tenon, export, util, configs



@util.main
def main(src_path):
	thickness = 0.08
	gap = 0.005
	FILE = export.OpenSCADFile(sys.stdout)

	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)
	cfg = configs.load_from_json("src/example.json")
	WW = tenon.WoodWorker(cfg)

	with FILE.group('render'):
		for face in polyhedron.faces:
			if cfg.omitted(face):
				continue

			cut = WW.piece(face)
			t = polyhedra.face_coordinate_system(face)

			polygon = polyhedra.get_planar_polygon(face)
			vertices = polygon.paths[0].vertices
			center = -numpy.mean(vertices, 0)
			minr = numpy.amin([numpy.linalg.norm(v - center) for v in vertices])

			with FILE.group('multmatrix', t):
				with FILE.group('difference'):
					with FILE.group('linear_extrude', thickness - gap):
						with FILE.group('offset', -gap / 2):
							FILE.polygon(cut)

					with FILE.group('translate', [-center[0], -center[1], 0.7 * thickness]):
						with FILE.group('linear_extrude', thickness):
							fid = str(face.face_id)

							if all(i in '0689' for i in fid):
								fid += '.'

							FILE.text(fid, size=0.3 * minr, halign='center', valign='center')

					with FILE.group('translate', [-center[0], -center[1], 0]):
						with FILE.group('translate', [-0.56,-0.5,0]):
							with FILE.group('linear_extrude', thickness):
								FILE.call('import', file='/data/CCC/repos/polybox-generator/generator/lib/hole.dxf')
