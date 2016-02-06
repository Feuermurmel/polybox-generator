import sys, math, numpy
from lib import polyhedra, tenon, export, util, paths, config


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))
	
	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	file = export.AsymptoteFile(sys.stdout)
	file.write('import "../_faces.asy" as _;')
	file.write('unitsize(mm);')
	
	# Both are in mm.
	scale = 20
	spacing = 100

	debug_mode = True

	polyhedron = polyhedra.Polyhedron.load_from_json(src_path, scale = scale)
	configuration = config.load_configuration('src/config.py')
	properties = configuration.apply(polyhedron)
	
	WW = tenon.WoodWorker(properties)
	
	for face, grid_pos in zip(polyhedron.faces, arrange_grid(len(polyhedron.faces))):
		polygon = polyhedra.get_planar_polygon(face)
		offset = -numpy.mean(polygon.paths[0].vertices, 0)
		cut = WW.piece(face)

		polygon = paths.move(*offset) * polygon
		cut = paths.move(*offset) * cut
		
		with file.transform('shift({} * {})', grid_pos, spacing):
			if debug_mode:
				file.write('face({});', cut)
				file.write('edges({});', polygon)
				file.write('vertices({});', polygon)
				
				file.write('face_id((0, 0), "{}");', face.face_id)
				
				for i, pos in zip(face.face_cycle, polygon.paths[0].vertices):
					file.write('vertex_id({}, "{}");', pos, i.vertex_id)
					
					for j, a, b in zip(face.face_cycle,
							   polygon.paths[0].vertices,
							   polygon.paths[0].vertices[1:] + [polygon.paths[0].vertices[0]]):
						file.write('edge_id({}, {}, "{}");', a, b, str(j.edge_id))

			# Contour for laser cut
			file.write('cut_contour({});', cut)
