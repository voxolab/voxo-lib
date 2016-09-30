import pytest
from lxml import etree
from xml.dom import minidom
from voxolab.xml_alpha_to_numbers import is_number, is_well_formed_number, xml_alpha_to_numbers, convert_alpha_to_number

class TestAlphaToNumberInXmlV2:

    def test_full_transform(self, full_xml_v2_root, alpha_to_number_script, number_to_alpha_script):
        xml_alpha_to_numbers(full_xml_v2_root, alpha_to_number_script, number_to_alpha_script)

        xml_string = etree.tostring(full_xml_v2_root)
        reparsed = minidom.parseString(xml_string)
        pretty_xml = '\n'.join([line for line in reparsed.toprettyxml(indent=' '*4).split('\n') if line.strip()])
        #print(pretty_xml)

        assert len(full_xml_v2_root[0]) == 7
        assert len(full_xml_v2_root[1]) == 8

        assert full_xml_v2_root[0][6].attrib['value'] == '51'
        assert full_xml_v2_root[1][0].attrib['value'] == '38'

    def test_convert_alpha_to_number(self, alpha_to_number_script):
        assert '08' == convert_alpha_to_number(
            'zéro-huit', alpha_to_number_script, 'utf-8')

        assert '027' == convert_alpha_to_number(
            'zéro-vingt-sept', alpha_to_number_script, 'utf-8')


        assert '00' == convert_alpha_to_number(
            'zéro-zéro', alpha_to_number_script, 'utf-8')


    def test_is_well_formed_number(
            self,
            alpha_to_number_script,
            number_to_alpha_script):

        assert is_well_formed_number(
            'trois',
            alpha_to_number_script,
            number_to_alpha_script)

        assert is_well_formed_number(
            'zéro-zéro',
            alpha_to_number_script,
            number_to_alpha_script)

        assert is_well_formed_number(
            'huit-cents',
            alpha_to_number_script,
            number_to_alpha_script)


    def test_small_transform(self, small_xml_v2_root, alpha_to_number_script, number_to_alpha_script):
        xml_alpha_to_numbers(small_xml_v2_root, alpha_to_number_script, number_to_alpha_script)

        xml_string = etree.tostring(small_xml_v2_root)
        reparsed = minidom.parseString(xml_string)
        pretty_xml = '\n'.join([line for line in reparsed.toprettyxml(indent=' '*4).split('\n') if line.strip()])
        #print(pretty_xml)
