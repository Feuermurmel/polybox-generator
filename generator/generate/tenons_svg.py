import sys, math, numpy, svgwrite, svgwrite.shapes
from lib import polyhedra, tenon, export, util, paths


def arrange_grid(count):
	width = math.ceil(math.sqrt(count))
	
	return [divmod(i, width) for i in range(count)]


@util.main
def main(src_path):
	# Both are in mm.
	scale = 20
	spacing = 100
	
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path, scale = scale)
	fingertenon = tenon.RegularFingerTenon(.5)
	
	d = svgwrite.Drawing()
	
	for face, grid_pos in zip(polyhedron.faces, arrange_grid(len(polyhedron.faces))):
		polygon = polyhedra.get_planar_polygon(face)
		offset = -numpy.mean(polygon.paths[0].vertices, 0)
		cut = fingertenon.tenon(face)
		
		cut = paths.move(grid_pos[0] * spacing, grid_pos[1] * spacing) * paths.move(*offset) * cut
		
		d.add(export.polygon_to_svg_path(cut))
	
	d.write(sys.stdout)
