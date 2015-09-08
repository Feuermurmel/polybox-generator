import numpy
import numpy.linalg


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
