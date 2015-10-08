from lib import paths, export, util


def make_strip(t1, t2):
	h1 = paths.half_plane((t1, 0), (0, -1))
	h2 = paths.half_plane((t2, 0), (0.0001,  1))
	return h1 & h2

def main():
    c = paths.circle()

    # OK
    hin = 0.1

    # Fail (fixed)
    hin = 0.0

    # Bool ops
    I = paths.half_plane((0,  hin),  ( 1, 0))
    H = paths.half_plane((0,  0),    ( 1, 0))
    S = make_strip(0.1, 0.5)
    T = S / I

    V = H / T

    with util.writing_text_file('src/U-intersect.asy') as file:
        print('settings.outformat="pdf";', file = file)
        print('fill({}, (blue + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * (H & c))), file = file)
        print('fill({}, (red + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * (T & c))), file = file)
        print('fill({}, (green + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * (V & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * (V & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * (T & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)

main()
