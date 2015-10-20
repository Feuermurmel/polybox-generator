import sys, numpy
from lib import polyhedra


def main(src_path):
	polyhedron = polyhedra.Polyhedron.load_from_json(src_path)

	for f1 in polyhedron.edges:
		f2 = f1.opposite
		theta = polyhedra.dihedral_angle(f1, f2)
		theta = numpy.degrees(theta)
		print("%s:\t%.4f°" % (str(f1.edge_id), theta))


main(*sys.argv[1:])
