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
            draw((0,0) -- (1,0), red, arrow=Arrow());
            draw((0,0) -- (0,1), red, arrow=Arrow());
            dot((0,0), red);
        }
        """
        return code
