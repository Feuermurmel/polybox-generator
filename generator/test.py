import functools, operator
from lib import paths, export, util


def main():
	c = paths.circle()
	p = paths.polygon([(0, 0), (0, 2), (2, 0)])
	
	with util.writing_text_file('src/test/a.asy') as file:
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * (p / c))), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * p)), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)
	
	h = [paths.rotate(util.tau * i / 25) * paths.half_plane((-.02, 0), (0, 1)) for i in range(25)]
	
	with util.writing_text_file('src/test/b.asy') as file:
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * (c & functools.reduce(operator.__xor__, h)))), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)
	
	with util.writing_text_file('src/test/c.asy') as file:
		x = paths.half_plane((10, 0), (1, 1)) | paths.half_plane((10, 0), (1, -1))
		
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * c & x)), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)
	
	with util.writing_text_file('src/test/d.asy') as file:
		p = [paths.half_plane((i, 0), (0, 1)) for i in range(-10, 11)]
		a = functools.reduce(operator.xor, p)
		n = 5
		x = functools.reduce(operator.xor, (paths.rotate(turns = i / n) * a for i in range(n)))
		
		print('fill({}, red + white);'.format(export.asymptote_expression(paths.scale(20) * c & x)), file = file)
		print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)


main()
