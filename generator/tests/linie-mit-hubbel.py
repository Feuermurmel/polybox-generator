from lib import paths, export, util


def main():
	c = paths.circle()
	p = paths.polygon([paths.vertex_at_infinity(-1, 0), (-1, 0), (0, 1), (1, 0), paths.vertex_at_infinity(1, 0)])

	with util.writing_text_file('src/test-hubbel.asy') as file:
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * c & ~p)), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c & p)), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)


main()
