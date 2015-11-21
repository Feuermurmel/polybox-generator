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


class TextureEngraving(Engraving):

    def engrave(self, faceview):
        code = """
        void engrave() {
          picture engraving;
          // Scale postscript point (1/72 inch) to millimeter
          // Note: tex point (1 / 72.27) is wrong here
          transform s = scale(72 / 25.4);
          // Load graphcs file
          Label L = Label(graphic("/data/CCC/repos/polybox-generator/generator/lib/texture.eps"), embed=Scale);
          // Make a label of proper scale and alignment
          label(engraving, s*L, (0mm,0mm), align=Align);
          add(engraving);
          // Ensure remaining things are drawn on top
          layer();
        }
        """
        return code
