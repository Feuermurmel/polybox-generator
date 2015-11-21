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
