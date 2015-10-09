from lib import paths, export, util


def main():
	c = paths.circle()
	p = paths.polygon([paths.vertex_at_infinity(-1, 0), (-1, 0), (0, 1), (1, 0), paths.vertex_at_infinity(1, 0)])

	with export.writing_asymptote_file('src/test-hubbel.asy') as file:
		file.write('fill({}, red + white);', paths.scale(20) * c & ~p)
		file.write('draw({}, 0.1mm + black);', paths.scale(20) * c & p)
		file.write('draw({}, 0.1mm + black);', paths.scale(20) * c)


main()
