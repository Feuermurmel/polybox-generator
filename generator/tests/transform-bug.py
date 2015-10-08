from lib import paths, export, util


def main():
    c = paths.circle()

    S = paths.square()

    # OK
    t = paths.transform(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Fail (fixed)
    t = paths.transform(-1.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    St = t * S

    with util.writing_text_file('src/transform-bug.asy') as file:
        print('settings.outformat="pdf";', file = file)
        print('fill({}, (blue + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * S)), file = file)
        print('fill({}, (red + white) + opacity(0.6));'.format(export.asymptote_expression(paths.scale(20) * St)), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * S)), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * St)), file = file)
        print('draw({}, 0.1mm + black);'.format(export.asymptote_expression(paths.scale(20) * c)), file = file)

main()
