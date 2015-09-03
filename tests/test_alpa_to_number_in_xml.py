import pytest
from voxolab.xml_alpha_to_numbers import is_number

class TestAlphaToNumberInXml:

    def test_good_xml(self, full_xml_root):
        assert len(full_xml_root) == 3

    def test_is_number(self):
        assert is_number('trois')
        assert is_number('vingt-trois')
        assert not is_number('vingt-trois-test')
        assert not is_number('trentetrois')
        assert not is_number('trente trois')
