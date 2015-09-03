import pytest
from voxolab.xml_alpha_to_numbers import is_number, is_well_formed_number, xml_alpha_to_numbers, convert_alpha_to_number

class TestAlphaToNumberInXml:

    def test_good_xml(self, full_xml_root):
        assert len(full_xml_root) == 3
        assert len(full_xml_root[0]) == 10
        assert len(full_xml_root[1]) == 2
        assert len(full_xml_root[2]) == 18

    def test_is_number(self):
        assert is_number('trois')
        assert is_number('vingt-trois')
        assert is_number('quinze')
        assert not is_number('vingt-trois-test')
        assert not is_number('trentetrois')
        assert not is_number('trente trois')

    def test_convert_alpha_to_number(self, alpha_to_number_script):
        assert '15' == convert_alpha_to_number('quinze', alpha_to_number_script, 'iso-8859-1')

    def test_is_well_formed_number(self, alpha_to_number_script, number_to_alpha_script):
        assert is_well_formed_number('trois', alpha_to_number_script, number_to_alpha_script)
        assert is_well_formed_number('zéro-trois', alpha_to_number_script, number_to_alpha_script)
        assert is_well_formed_number('zéro-zéro', alpha_to_number_script, number_to_alpha_script)
        assert is_well_formed_number('quinze', alpha_to_number_script, number_to_alpha_script)
        assert not is_well_formed_number('trois-quarante', alpha_to_number_script, number_to_alpha_script)

    def test_full_transform(self, full_xml_root, alpha_to_number_script, number_to_alpha_script):
        xml_alpha_to_numbers(full_xml_root, alpha_to_number_script, number_to_alpha_script)
        assert len(full_xml_root[0]) == 8
        assert len(full_xml_root[1]) == 2
        assert len(full_xml_root[2]) == 12

        assert full_xml_root[0][7].attrib['sel'] == '2004'
        assert full_xml_root[2][3].attrib['sel'] == '06'
        assert full_xml_root[2][4].attrib['sel'] == '51'
        assert full_xml_root[2][5].attrib['sel'] == '00'
        assert full_xml_root[2][6].attrib['sel'] == '73'
        assert full_xml_root[2][7].attrib['sel'] == '76'
        assert full_xml_root[2][8].attrib['sel'] == 'à'
        assert full_xml_root[2][11].attrib['sel'] == '15'
