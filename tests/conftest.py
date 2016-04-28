import pytest
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')


@pytest.fixture
def full_xml_root(full_xml_string):
    from lxml import etree
    root = etree.fromstring(full_xml_string)
    return root


@pytest.fixture
def alpha_to_number_script():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..',
        'bin',
        'convertirAlphaEnNombre.pl')


@pytest.fixture
def number_to_alpha_script():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..',
        'bin',
        'convertirNombreEnAlpha.pl')


@pytest.fixture
def full_xml_v2_root(full_xml_v2_string):
    from lxml import etree
    root = etree.fromstring(full_xml_v2_string)
    return root


@pytest.fixture
def full_xml_v2_string():
    return """
<show name="demo_1_dc79942a_c6ee_4d24_bfd8_b6f61344987c">
  <sentence gender="Female" speaker="S0" type="Studio">
    <word length="0.35" score="1.00" start="0.63" value="zéro"/>
    <word length="0.35" score="0.96" start="0.98" value="deux"/>
    <word length="0.36" score="1.00" start="1.68" value="quatre"/>
    <word length="0.18" score="1.00" start="2.04" value="vingt"/>
    <word length="0.61" score="1.00" start="2.22" value="seize"/>
    <word length="0.49" score="1.00" start="3.12" value="quarante"/>
    <word length="0.47" score="1.00" start="3.61" value="huit"/>
    <word length="0.52" score="1.00" start="4.47" value="cinquante"/>
    <word length="0.16" score="1.00" start="4.99" value="et"/>
    <word length="0.23" score="1.00" start="5.15" value="un"/>
    <word length="0.42" score="1.00" start="5.87" value="zéro"/>
    <word length="0.66" score="1.00" start="6.29" value="six"/>
    <word length="0.50" score="0.99" start="8.63" value="zéro"/>
    <word length="0.21" score="0.96" start="9.13" value="un"/>
    <word length="0.61" score="1.00" start="9.75" value="cinquante"/>
  </sentence>
  <sentence gender="Female" speaker="S0" type="Studio">
    <word length="0.59" score="1.00" start="10.36" value="et"/>
    <word length="0.59" score="1.00" start="10.36" value="un"/>
    <word length="0.41" score="1.00" start="11.19" value="trente"/>
    <word length="0.50" score="1.00" start="11.60" value="huit"/>
    <word length="0.22" score="1.00" start="12.51" value="dix"/>
    <word length="0.53" score="1.00" start="12.73" value="sept"/>
    <word length="0.44" score="1.00" start="13.65" value="trente"/>
    <word length="0.34" score="0.99" start="14.09" value="deux"/>
    <word length="0.38" score="1.00" start="15.81" value="zéro"/>
    <word length="0.57" score="1.00" start="16.19" value="neuf"/>
    <word length="0.67" score="1.00" start="17.03" value="soixante"/>
    <word length="0.48" score="1.00" start="17.70" value="douze"/>
    <word length="0.33" score="1.00" start="18.53" value="trente"/>
    <word length="0.58" score="1.00" start="18.86" value="sept"/>
    <word length="0.31" score="1.00" start="19.62" value="quatre"/>
    <word length="0.15" score="0.99" start="19.93" value="vingt"/>
    <word length="0.16" score="1.00" start="20.08" value="dix"/>
    <word length="0.53" score="1.00" start="20.24" value="sept"/>
    <word length="0.53" score="1.00" start="20.87" value="cinquante"/>
    <word length="0.46" score="1.00" start="21.40" value="trois"/>
  </sentence>
</show>"""


@pytest.fixture
def full_xml_string():
    return """
<show name="test">
    <sentence start="0.00" end="19.02" locuteur="S0" type="Tel" sexe="Female">
        <word sel="bonjour" start="0.11" length="0.31" scoreConfiance="1.00">
            <prop mot="bonjour" scoreProp="1.00"/>
        </word>
        <word sel="Thierry" start="0.42" length="0.3" scoreConfiance="0.969">
            <prop mot="thierry" scoreProp="0.969"/>
            <prop mot="tiret" scoreProp="0.0315"/>
        </word>
        <word sel="c'" start="0.71" length="0.13" scoreConfiance="0.881">
            <prop mot="c'" scoreProp="0.881"/>
            <prop mot="s'" scoreProp="0.0473"/>
        </word>
        <word sel="est" start="0.71" length="0.37" scoreConfiance="0.928">
            <prop mot="est" scoreProp="0.928"/>
            <prop mot="ces" scoreProp="0.0339"/>
            <prop mot="ses" scoreProp="0.0264"/>
        </word>
        <word sel="Fabrice" start="1.08" length="0.5" scoreConfiance="0.988">
            <prop mot="fabrice" scoreProp="0.988"/>
        </word>
        <word sel="et" start="0.65" length="0.13" scoreConfiance="0.946">
            <prop mot="et" scoreProp="0.946"/>
            <prop mot="est" scoreProp="0.0513"/>
        </word>
        <word sel="en" start="0.78" length="0.11" scoreConfiance="1.00">
            <prop mot="en" scoreProp="1.00"/>
        </word>
        <word sel="deux" start="0.89" length="0.14" scoreConfiance="1.00">
            <prop mot="deux" scoreProp="1.00"/>
        </word>
        <word sel="mille" start="1.03" length="0.21" scoreConfiance="1.00">
            <prop mot="mille" scoreProp="1.00"/>
        </word>
        <word sel="quatre" start="1.24" length="0.48" scoreConfiance="0.999">
            <prop mot="quatre" scoreProp="0.999"/>
        </word>
    </sentence>
    <sentence start="2.95" end="5.24" locuteur="S0" type="Studio" sexe="Male">
        <word sel="j'" start="3.2" length="0.12" scoreConfiance="0.965">
            <prop mot="j'" scoreProp="0.965"/>
        </word>
        <word sel="allais" start="3.2" length="0.43" scoreConfiance="0.959">
            <prop mot="allais" scoreProp="0.959"/>
            <prop mot="allez" scoreProp="0.0122"/>
            <prop mot="jallet" scoreProp="0.0111"/>
        </word>
    </sentence>
    <sentence start="25.32" end="30.07" locuteur="S0" type="Tel" sexe="Female">

        <word sel="le" start="25.32" length="0.760000000000001" scoreConfiance="0.708">
            <prop mot="le" scoreProp="0.708"/>
            <prop mot="locaux" scoreProp="0.233"/>
        </word>
        <word sel="au" start="25.61" length="0.380000000000001" scoreConfiance="0.767">
            <prop mot="au" scoreProp="0.767"/>
        </word>
        <word sel="au" start="25.71" length="0.37" scoreConfiance="0.980">
            <prop mot="au" scoreProp="0.980"/>
        </word>
        <word sel="zéro" start="26.08" length="0.3" scoreConfiance="1.00">
            <prop mot="zéro" scoreProp="1.00"/>
        </word>
        <word sel="six" start="26.38" length="0.32" scoreConfiance="1.00">
            <prop mot="six" scoreProp="1.00"/>
        </word>
        <word sel="cinquante" start="26.62" length="0.359999999999999" scoreConfiance="0.996">
            <prop mot="cinquante" scoreProp="0.996"/>
        </word>
        <word sel="et" start="26.98" length="0.04" scoreConfiance="0.771">
            <prop mot="et" scoreProp="0.771"/>
        </word>
        <word sel="un" start="26.91" length="0.31" scoreConfiance="0.772">
            <prop mot="un" scoreProp="0.772"/>
            <prop mot="quinze" scoreProp="0.229"/>
        </word>
        <word sel="zéro" start="27.22" length="0.25" scoreConfiance="1.00">
            <prop mot="zéro" scoreProp="1.00"/>
        </word>
        <word sel="zéro" start="27.47" length="0.33" scoreConfiance="1.00">
            <prop mot="zéro" scoreProp="1.00"/>
        </word>
        <word sel="soixante" start="27.86" length="0.479999999999999" scoreConfiance="1.00">
            <prop mot="soixante" scoreProp="1.00"/>
        </word>
        <word sel="treize" start="28.34" length="0.390000000000001" scoreConfiance="1.00">
            <prop mot="treize" scoreProp="1.00"/>
        </word>
        <word sel="soixante" start="28.83" length="0.41" scoreConfiance="1.00">
            <prop mot="soixante" scoreProp="1.00"/>
        </word>
        <word sel="seize" start="29.24" length="0.290000000000001" scoreConfiance="1.00">
            <prop mot="seize" scoreProp="1.00"/>
        </word>
        <word sel="à" start="29.63" length="0.199999999999999" scoreConfiance="0.611">
            <prop mot="à" scoreProp="0.611"/>
            <prop mot="a" scoreProp="0.0386"/>
            <prop mot="et" scoreProp="0.0221"/>
        </word>
        <word sel="plus" start="29.64" length="0.4" scoreConfiance="0.907">
            <prop mot="plus" scoreProp="0.907"/>
            <prop mot="appliquant" scoreProp="0.0425"/>
            <prop mot="impliquant" scoreProp="0.0123"/>
        </word>
        <word sel="tard" start="29.68" length="0.389999999999999" scoreConfiance="0.907">
            <prop mot="tard" scoreProp="0.907"/>
            <prop mot="quand" scoreProp="0.0147"/>
            <prop mot="picard" scoreProp="0.0132"/>
        </word>
        <word sel="quinze" start="29.68" length="0.389999999999999" scoreConfiance="0.907">
            <prop mot="quinze" scoreProp="0.907"/>
        </word>
    </sentence>

    <sentence start="0.00" end="12.09" locuteur="S0" type="Tel" sexe="Female">

        <word sel="zéro" start="9.35" length="0.33" scoreConfiance="1.00">
            <prop mot="zéro" scoreProp="1.00"/>
        </word>
        <word sel="un" start="9.68" length="0.120000000000001" scoreConfiance="1.00">
            <prop mot="un" scoreProp="1.00"/>
        </word>
        <word sel="soixante" start="9.8" length="0.51" scoreConfiance="1.00">
            <prop mot="soixante" scoreProp="1.00"/>
        </word>
        <word sel="et" start="10.31" length="0.0800000000000001" scoreConfiance="1.00">
            <prop mot="et" scoreProp="1.00"/>
        </word>
        <word sel="un" start="10.39" length="0.19" scoreConfiance="1.00">
            <prop mot="un" scoreProp="1.00"/>
        </word>
        <word sel="trente" start="10.69" length="0.48" scoreConfiance="1.00">
            <prop mot="trente" scoreProp="1.00"/>
        </word>
        <word sel="quatre" start="11.28" length="0.32" scoreConfiance="0.998">
            <prop mot="quatre" scoreProp="0.998"/>
        </word>
        <word sel="vingt" start="11.6" length="0.27" scoreConfiance="0.673">
            <prop mot="vingt" scoreProp="0.673"/>
            <prop mot="vingts" scoreProp="0.326"/>
        </word>
    </sentence>

</show>"""
