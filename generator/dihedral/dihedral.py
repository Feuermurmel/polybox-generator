import sys, numpy
from lib import polyhedra


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)

	for i, f1 in enumerate(polyhedron.edges):
		f2 = f1.opposite
		theta = polyhedra.dihedral_angle(f1, f2)
		theta = numpy.degrees(theta)
		print("%d:\t%.4f" % (i, theta))


main(*sys.argv[1:])
