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
        pen b = black + 0.1mm;
        draw((0mm,0mm) -- (1mm,0mm), b, arrow=Arrow());
        draw((0mm,0mm) -- (0mm,1mm), b, arrow=Arrow());
        dot((0mm,0mm), red);
        """
        return code


class FaceCutEngraving(Engraving):

    def engrave(self, faceview):
        code = """
        draw(circle((0.5mm, 0.5mm), 0.2mm), cut_pen);
        draw(circle((0.2mm, 0.2mm), 0.1mm), cut_pen);
        draw(circle((0.8mm, 0.2mm), 0.1mm), cut_pen);
        draw(circle((0.2mm, 0.8mm), 0.1mm), cut_pen);
        draw(circle((0.8mm, 0.8mm), 0.1mm), cut_pen);
        """
        return code


class TextureEngraving(Engraving):

    def __init__(self, filepath=None, transformation={}, **kwargs):
        """
        :param filepath: Path to the image file.
        :param transformation: Dictionary of tranformation specifications.
                               Possible keys are:
                               - shift
                               - scale
                               - rotate
        """
        super().__init__()
        self._filepath = filepath
        self._shift = tuple(transformation.get("shift", (0,0)))
        self._scale = transformation.get("scale", 1)
        self._rotate = transformation.get("rotate", 0)


    def engrave(self, faceview):
        code = """
        picture engraving;
        // Scale postscript point (1/72 inch) to millimeter
        // Note: tex point (1 / 72.27) is wrong here
        //transform s = scale(72 / 25.4);
        transform tm = shift(%s);
        transform ts = scale(%f);
        transform tr = rotate(%f);
        // Load graphics file
        Label L = Label(graphic("%s"), embed=Scale);
        // Make a label of proper scale and alignment
        label(engraving, tm*ts*tr*L, (0mm,0mm), align=Align);
        add(engraving);
        // Ensure remaining things are drawn on top
        layer();
        """ % (self._shift, self._scale, self._rotate, self._filepath)
        return code
