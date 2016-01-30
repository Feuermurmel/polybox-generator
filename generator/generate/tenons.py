import sys, math, numpy
from lib import polyhedra, tenon, export, util, configs


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))

	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	file = export.AsymptoteFile(sys.stdout)
	file.write('import "../_faces.asy" as _;')

	polyhedron = polyhedra.Polyhedron.load_from_json(src_path, scale=10)
	cfg = configs.load_from_json("src/example.json")
	WW = tenon.WoodWorker(cfg)

	debug_mode = False

	for face, (c, r) in zip(polyhedron.faces, arrange_grid(len(polyhedron.faces))):
		if cfg.omitted(face):
			continue

		polygon = polyhedra.get_planar_polygon(face)
		centerx, centery = numpy.mean(polygon.paths[0].vertices, 0)
		cut = WW.piece(face)

		with file.transform('shift(({}, {}) * 9.5mm) * scale(1)', c, r):
			file.write('transform t = shift(({}, {}) * 1mm);', -centerx, -centery)

			if debug_mode:
				file.write('face({}, t);', cut, c, r)
				file.write('edges({}, t);', polygon, c, r)
				file.write('vertices({}, t);', polygon, c, r)

				file.write('face_id(({}mm, {}mm), "{}", t);', centerx, centery, face.face_id)

				for i, (x, y) in zip(face.face_cycle, polygon.paths[0].vertices):
					file.write('vertex_id(({}mm, {}mm), "{}", t);', x, y, i.vertex_id)

					for i, (ax, ay), (bx, by) in zip(face.face_cycle,
									 polygon.paths[0].vertices,
									 polygon.paths[0].vertices[1:] + [polygon.paths[0].vertices[0]]):
						file.write('edge_id(({}mm, {}mm), ({}mm, {}mm), "{}", t);', ax, ay, bx, by, i.edge_id)

			# Contour for laser cut
			file.write('cut_contour({}, t);', cut, c, r)
