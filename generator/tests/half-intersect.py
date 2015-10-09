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

    # Wrong!
    # h1 = paths.half_plane((-0.5, 0), (0, -1))
    # h2 = paths.half_plane(( 0.5, 0), (0,  1))

    # h1 = paths.half_plane((0,  0.5), (-1, 0))
    # h2 = paths.half_plane((0, -0.5), ( 1, 0))

    x = h1 & h2

    with export.writing_asymptote_file('src/strip.asy') as file:
        print('settings.outformat="pdf";', file = file)
        file.write('fill({}, (blue + white) + opacity(0.6));', paths.scale(20) * (h2 & c))
        file.write('fill({}, (red + white) + opacity(0.6));', paths.scale(20) * (h1 & c))
        file.write('fill({}, (green + white) + opacity(0.4));', paths.scale(20) * (x & c))
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * (h1 & c))
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * (h2 & c))
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * c)

main()
