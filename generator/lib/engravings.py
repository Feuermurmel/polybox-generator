import abc


class Engraving(metaclass = abc.ABCMeta):
    """
    """

    @abc.abstractmethod
    def engrave(self, faceview):
        """
        """


class CoordinateEngraving(Engraving):

    def engrave(self, faceview):
        code = """
        void engrave() {
            pen b = black + 0.1mm;
            draw((0mm,0mm) -- (1mm,0mm), b, arrow=Arrow());
            draw((0mm,0mm) -- (0mm,1mm), b, arrow=Arrow());
            dot((0mm,0mm), red);
        }
        """
        return code


class FaceCutEngraving(Engraving):

    def engrave(self, faceview):
        code = """
        void engrave() {
          draw(circle((0.5mm, 0.5mm), 0.2mm), cut_pen);
          draw(circle((0.2mm, 0.2mm), 0.1mm), cut_pen);
          draw(circle((0.8mm, 0.2mm), 0.1mm), cut_pen);
          draw(circle((0.2mm, 0.8mm), 0.1mm), cut_pen);
          draw(circle((0.8mm, 0.8mm), 0.1mm), cut_pen);
        }
        """
        return code
