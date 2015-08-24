from lib import paths, export, util


def main():
	p1 = paths.polygon([(0, 0), (0, 2), (2, 0)])
	p2 = paths.circle()
	
	with util.writing_text_file('src/test/a.asy') as file:
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * (p1 / p2))), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * p1)), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * p2)), file = file)


main()
