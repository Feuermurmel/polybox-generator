import numpy
import numpy.linalg

parallel_eps = 1e-6


norm = numpy.linalg.norm


def normalize(v):
	"""
	Normalize the vector v.
	"""
	return v / numpy.linalg.norm(v)


def projector(basis):
	"""
	Projection onto a subspace with given basis, assuming the basis is orthonormal.
	"""

	K = numpy.column_stack(basis)
	P = numpy.dot(K, K.T)
	return P


def intersect(P1, P2):
	"""
	Compute the intersection line of two planes P1 and P2 in parametric form.
	"""
	# P1 := [s, r1, r2]
	# P2 := [s, r1, r2]
	p1s, p1r1, p1r2 = P1
	p2s, p2r1, p2r2 = P2

	# Normal vectors
	n1 = normalize(numpy.cross(p1r1, p1r2))
	n2 = normalize(numpy.cross(p2r1, p2r2))

	# Direction
	n3 = normalize(numpy.cross(n1, n2))

	# Distances
	d1 = -numpy.dot(p1s, n1)
	d2 = -numpy.dot(p2s, n2)

	# Intersection point
	p0 = numpy.cross(d2*n1 - d1*n2, numpy.cross(n1,n2)) / numpy.linalg.norm(numpy.cross(n1, n2))**2

	return p0, n3


def rot_cw(v):
	return numpy.array([ v[1],
			    -v[0]])

def rot_ccw(v):
	return numpy.array([-v[1],
			     v[0]])
