from lib import paths, export, util


def main():
    c = paths.circle()

    S = paths.square()

    # OK:
    #t = paths.transform(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Fail:
    t = paths.transform(-1.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    St = t * S

    with export.writing_asymptote_file('src/transform-bug.asy') as file:
        print('settings.outformat="pdf";', file = file)
        file.write('fill({}, (blue + white) + opacity(0.6));', paths.scale(20) * S)
        file.write('fill({}, (red + white) + opacity(0.6));', paths.scale(20) * St)
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * S)
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * St)
        file.write('draw({}, 0.1mm + black);', paths.scale(20) * c)

main()
