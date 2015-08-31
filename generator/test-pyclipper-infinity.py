import pyclipper

_clipper_scale = 1 << 31
_clipper_range = ((1 << 62) - 1) / _clipper_scale
x = round(_clipper_scale * _clipper_range) - 1

subj = ((-x, -x), (x, -x), (x, x))
clip = ((190, 210), (240, 210), (240, 130), (190, 130))

pc = pyclipper.Pyclipper()
pc.AddPath(subj, pyclipper.PT_SUBJECT, True)
pc.AddPath(clip, pyclipper.PT_CLIP, True)

solution = pc.Execute2(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

print([i.Contour for i in solution.Childs])
