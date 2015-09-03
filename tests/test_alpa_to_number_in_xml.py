import pytest

class TestAlphaToNumberInXml:

    def test_good_xml(self, full_xml_root):
        assert len(full_xml_root) == 3
