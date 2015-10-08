from lib import paths, export, util


def main():
    c = paths.circle()

    T = paths.rotate(turns=1/5)
    h1 = paths.half_plane((0, 0.1), (1, 0))

    # Ok
    h2 = T * h1

    # Fail
    h2 = T * T * h1

    x = h1 | h2

    with util.writing_text_file('src/angle-union.asy') as file:
        print('settings.outformat="pdf";', file = file)
        print('fill({}, (blue + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * (h2 & c))), file = file)
        print('fill({}, (red + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * (h1 & c))), file = file)
        print('fill({}, (green + white) + opacity(0.4));'.format(export.asymptote_expression(paths.scale(20) * (x & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * (h1 & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * (h2 & c))), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)

main()
