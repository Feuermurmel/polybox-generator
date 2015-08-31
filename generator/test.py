from lib import paths, export, util


def main():
	c = paths.circle()
	p = paths.polygon([(0, 0), (0, 2), (2, 0)])
	
	with util.writing_text_file('src/test/a.asy') as file:
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * (p / c))), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * p)), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)
	
	h1 = paths.half_plane([-.2, 0], [-1, 2])
	h2 = paths.half_plane([.2, 0], [1, 2])
	
	with util.writing_text_file('src/test/b.asy') as file:
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * (c & (h1 | h2)))), file = file)
		print('fill({}, blue + white);'.format(export.asymptote_expression(paths.scale(20) * (c & (h1 & h2)))), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)
	
	print(export.openscad_polygon(paths.scale(20) * (c & (h1 | h2))))


main()
