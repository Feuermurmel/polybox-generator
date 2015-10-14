import functools, operator
from lib import paths, export, util


def main():
	c = paths.circle()
	p = paths.polygon([(0, 0), (0, 2), (2, 0)])
	
	with export.writing_asymptote_file('src/test/a.asy') as file:
		file.write('fill({}, red + white);', paths.scale(20) * (p / c))
		file.write('draw({}, 0.1mm + black);', paths.scale(20) * p)
		file.write('draw({}, 0.1mm + black);', paths.scale(20) * c)
	
	h = [paths.rotate(util.tau * i / 25) * paths.half_plane((-.02, 0), (0, 1)) for i in range(25)]
	
	with export.writing_asymptote_file('src/test/b.asy') as file:
		file.write('fill({}, red + white);', paths.scale(20) * (c & functools.reduce(operator.__xor__, h)))
		file.write('draw({}, 0.1mm + black);', paths.scale(20) * c)
	
	with export.writing_asymptote_file('src/test/c.asy') as file:
		x = paths.half_plane((10, 0), (1, 1)) | paths.half_plane((10, 0), (1, -1))
		
		file.write('fill({}, red + white);', paths.scale(20) * c & x)
		file.write('draw({}, 0.1mm + black);', paths.scale(20) * c)
	
	p = [paths.half_plane((i, 0), (0, 1)) for i in range(-10, 11)]
	a = functools.reduce(operator.xor, p)
	n = 8
	x = paths.scale(20) * c & functools.reduce(operator.xor, (paths.rotate(turns = i / (2 * n)) * a for i in range(n)))
	
	with export.writing_asymptote_file('src/test/d.asy') as file:
		file.write('fill({}, red + white);', x)


main()
