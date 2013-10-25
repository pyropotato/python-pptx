# encoding: utf-8

"""
Base shape-related objects such as _BaseShape.
"""

from pptx.spec import namespaces
from pptx.oxml import _child
from pptx.text import _TextFrame
from pptx.util import to_unicode


# default namespace map for use in lxml calls
_nsmap = namespaces('a', 'r', 'p')


class _BaseShape(object):
    """
    Base class for shape objects. Both |_Shape| and |_Picture| inherit from
    |_BaseShape|.
    """
    def __init__(self, shape_element):
        super(_BaseShape, self).__init__()
        self._element = shape_element
        # e.g. nvSpPr for shape, nvPicPr for pic, etc.
        self.__nvXxPr = shape_element.xpath('./*[1]', namespaces=_nsmap)[0]

    @property
    def has_textframe(self):
        """
        True if this shape has a txBody element and can contain text.
        """
        return _child(self._element, 'p:txBody') is not None

    @property
    def id(self):
        """
        Id of this shape. Note that ids are constrained to positive integers.
        """
        return int(self.__nvXxPr.cNvPr.get('id'))

    @property
    def is_placeholder(self):
        """
        True if this shape is a placeholder. A shape is a placeholder if it
        has a <p:ph> element.
        """
        return _child(self.__nvXxPr.nvPr, 'p:ph') is not None

    @property
    def name(self):
        """Name of this shape."""
        return self.__nvXxPr.cNvPr.get('name')

    def _set_text(self, text):
        """Replace all text in shape with single run containing *text*"""
        if not self.has_textframe:
            raise TypeError("cannot set text of shape with no text frame")
        self.textframe.text = to_unicode(text)

    #: Write-only. Assignment to *text* replaces all text currently contained
    #: by the shape, resulting in a text frame containing exactly one
    #: paragraph, itself containing a single run. The assigned value can be a
    #: 7-bit ASCII string, a UTF-8 encoded 8-bit string, or unicode. String
    #: values are converted to unicode assuming UTF-8 encoding.
    text = property(None, _set_text)

    @property
    def shape_type(self):
        """
        Unique integer identifying the type of this shape, like ``MSO.CHART``.
        Must be implemented by subclasses. This one returns |None|
        unconditionally to account for shapes that haven't been implemented
        yet, like group shape and chart. Once those are done this should raise
        |NotImplementedError|.
        """
        return None
        # msg = 'shape_type property must be implemented by subclasses'
        # raise NotImplementedError(msg)

    @property
    def textframe(self):
        """
        _TextFrame instance for this shape. Raises |ValueError| if shape has
        no text frame. Use :attr:`has_textframe` to check whether a shape has
        a text frame.
        """
        txBody = _child(self._element, 'p:txBody')
        if txBody is None:
            raise ValueError('shape has no text frame')
        return _TextFrame(txBody)

    @property
    def _is_title(self):
        """
        True if this shape is a title placeholder.
        """
        ph = _child(self.__nvXxPr.nvPr, 'p:ph')
        if ph is None:
            return False
        # idx defaults to 0 when idx attr is absent
        ph_idx = ph.get('idx', '0')
        # title placeholder is identified by idx of 0
        return ph_idx == '0'