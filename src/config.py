from lib.settings import *


def config(s : Settings):
	# 4cm side length.
	s.scale_factor(40)
	
	# 4mm.
	s.face(...).material_thickness(4)
	s.face(5).material_thickness(8)
	
	s.face(0).omit()
	
	for i in range(1, 5):
		s.face(i).engraving(ImageEngraving('str/images/pony-{}.png'.format(i)))
	
	s.edge((0, 1)).tenon(FingerTenon())
	s.edge(*s.polyhedron.face_by_id(5).face_cycle).tenon(HoleTenon())
