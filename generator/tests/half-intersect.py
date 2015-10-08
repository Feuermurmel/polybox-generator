from lib import paths, export, util


def main():
    c = paths.circle()

    # OK
    h1 = paths.half_plane(( 0.5, 0), ( 1, 1))
    h2 = paths.half_plane((-0.5, 0), (-1,-1))

    h1 = paths.half_plane((-0.5, 0), (0,   -1))
    h2 = paths.half_plane(( 0.5, 0), (0.1,  1))

    h1 = paths.half_plane((-0.5, 0), (0,     -1))
    h2 = paths.half_plane(( 0.5, 0), (0.001,  1))

    h1 = paths.half_plane((-0.5, 0), (0,         -1))
    h2 = paths.half_plane(( 0.5, 0), (0.0000001,  1))

    # Fail (fixed)
    h1 = paths.half_plane((-0.5, 0), (0, -1))
    h2 = paths.half_plane(( 0.5, 0), (0,  1))

    h1 = paths.half_plane((0,  0.5), (-1, 0))
    h2 = paths.half_plane((0, -0.5), ( 1, 0))

    x = h1 & h2

    with util.writing_text_file('src/strip.asy') as file:
        print('settings.outformat="pdf";', file = file)
        print('fill({}, (blue + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * (h2 & c))), file = file)
        print('fill({}, (red + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * (h1 & c))), file = file)
        print('fill({}, (green + white) + opacity(0.4));'.format(export.asymptote_expression(paths.scale(20) * (x & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * (h1 & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * (h2 & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)

main()
