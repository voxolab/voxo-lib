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
        print(pretty_xml)

        assert len(full_xml_v2_root[0]) == 7
        assert len(full_xml_v2_root[1]) == 8

        assert full_xml_v2_root[0][6].attrib['value'] == '51'
        assert full_xml_v2_root[1][0].attrib['value'] == '38'
