import pyclipper

pc = pyclipper.Pyclipper()

# Add a single line as the subject.
pc.AddPath([(-1, -1), (2, 1)], pyclipper.PT_SUBJECT, False)

# Add a square as the clipping region.
pc.AddPath([(0, 0), (1, 0), (1, 1), (0, 1)], pyclipper.PT_CLIP, True)

# Clip the line using the rectangle.
solution = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)

print([i.Contour for i in solution.Childs])
