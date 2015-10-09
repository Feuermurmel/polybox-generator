from lib import paths, export, util


def make_strip(t1, t2):
	h1 = paths.half_plane((t1, 0), (0, -1))
	h2 = paths.half_plane((t2, 0), (0.0001,  1))
	return h1 & h2

def main():
    c = paths.circle()

    # OK
    hin = 0.1

    # Fail
    hin = 0.0

    # Bool ops
    I = paths.half_plane((0,  hin),  ( 1, 0))
    H = paths.half_plane((0,  0),    ( 1, 0))
    S = make_strip(0.1, 0.5)
    T = S / I

    V = H / T

    with export.writing_asymptote_file('src/U-intersect.asy') as file:
        print('settings.outformat="pdf";', file = file)
        file.write('fill({}, (blue + white) + opacity(0.6));', paths.scale(20) * (H & c))
        file.write('fill({}, (red + white) + opacity(0.6));', paths.scale(20) * (T & c))
        file.write('fill({}, (green + white) + opacity(0.6));', paths.scale(20) * (V & c))
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * (V & c))
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * (T & c))
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * c)

main()
