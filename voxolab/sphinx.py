# -*- coding: utf-8 -*-
import os, logging, sys, subprocess

logger = logging.getLogger(__name__)

class Sphinx:
    def __init__(self, sphinx_lib, project_name, project_dir, scripts_dir, lattice_mmi_dir, pseudo_path, log_file, status_function):
        self.sphinx_lib = sphinx_lib
        self.project_name = project_name
        self.project_dir = project_dir
        self.scripts_dir = scripts_dir
        self.lattice_mmi_dir = lattice_mmi_dir
        self.scripts_dir_bin = scripts_dir + "/bin/"
        self.pseudo_path = pseudo_path
        self.log_file = log_file
        self.status_function = status_function

    def script(self, script_name):
        return self.scripts_dir + "/bin/" + script_name

    def make_kaldi_sphinx_link(self, project_dir, project_name):
        logger.info("[Make kaldi sphinx link]")
        #cat ../kaldi_decode/lcp_q_gov.pseudo | etc/p1/faireLinkKaldiTer.perl /home/vjousse/usr/fac/decodeur/kaldi_decode/latticeMMI latp2/latlcp_q_gov | csh


        with open(self.log_file, "a") as output:
            cat = subprocess.Popen(['cat', self.pseudo_path], stdout=subprocess.PIPE)       
            #linkKaldi = subprocess.Popen([self.script('faireLinkKaldiTer.perl'), self.lattice_mmi_dir, os.path.join(project_dir, 'latp2', project_name)], stdin = cat.stdout, stdout=subprocess.PIPE, cwd=self.scripts_dir_bin)       
            linkKaldi = subprocess.Popen([self.script('faireLinkKaldiVince.py'), self.lattice_mmi_dir, os.path.join(project_dir, 'latp2', project_name)], stdin = cat.stdout, stdout=subprocess.PIPE, cwd=self.scripts_dir_bin)       
            bash = subprocess.Popen(['bash'], stdin=linkKaldi.stdout, stdout=output, stderr=output, cwd=self.scripts_dir_bin)       
            ret_code = bash.wait()
            output.flush()

    def make_ctm(self, lat_dir, ctm_file):
        logger.info("[Make ctm]")
        with open(ctm_file, "w") as output:

            #./bin/confus.perl lcp_q_gov/latp5/lcp_q_gov
            confus = subprocess.Popen(['confus.perl', lat_dir], stdout=output, cwd=self.scripts_dir_bin)       
            ret_code = confus.wait()
            output.flush()
            logger.info("Conversion to CTM finished. Result in '{ctm}'.".format(ctm=ctm_file))


    def make_xml(self, lat_dir, seg_file, xml_file, ctm_file_maj, recase = True, numbers = True):
        logger.info("[Make XML]")
        min_file = xml_file + '.min'
        maj_file = xml_file + '.maj'

        if(not recase and not numbers):
            min_file = xml_file

        with open(min_file, "w") as output:

            #$c = "./makeXmlAndClustering_withoutFillers.pl latp5/lat$fic/$fic files/$fic/$fic.seg.c.seg > files/$fic/$fic.xml";
            xml = subprocess.Popen(['makeXmlAndClustering_withoutFillers.pl', lat_dir, seg_file], stdout=output, cwd=self.scripts_dir_bin)       
            ret_code = xml.wait()
            output.flush()

        if(recase):
            with open(maj_file, "w") as output:
                #$c = "./remetMajDansXml.pl files/$fic/$fic.xml files/$fic/$fic.MAJ.ctm > files/$fic/$fic.MAJ.xml";
                xml = subprocess.Popen(['remetMajDansXml.pl', min_file, ctm_file_maj], stdout=output, cwd=self.scripts_dir_bin)       
                ret_code = xml.wait()
                output.flush()

        if(numbers):
            with open(xml_file, "w") as output:
                #system("./convertirAlphaEnNombreDansXml.pl files/$fic/$fic.xml > files/$fic/$fic.tmp.xml");
                xml = subprocess.Popen(['./convertirAlphaEnNombreDansXml.pl', maj_file], stdout=output, cwd=self.scripts_dir_bin)       
                ret_code = xml.wait()
                output.flush()

        logger.info("Conversion to XML finished. File in '{xml}'.".format(xml=xml_file))

    def make_decode_cmd(self, project_dir, lang_dir, sphinx_lib, sphinx_param):
        logger.info("[Make decode cmd]")
        #cat ../kaldi_decode/lcp_q_gov.pseudo | etc/p1/faire_commandeDirectpseudo.perl lcp_q_gov > lcp_q_gov.qsub

        with open(self.log_file, "a") as output:
            cat = subprocess.Popen(['cat', self.pseudo_path], stdout=subprocess.PIPE, cwd=self.scripts_dir_bin)       
            cmd = subprocess.Popen([self.script('faire_commandeDirectpseudo.perl'), project_dir, lang_dir, sphinx_lib, sphinx_param], stdin = cat.stdout, stdout=subprocess.PIPE, cwd=self.scripts_dir_bin)
            decodeCommand, err = cmd.communicate()

            logger.info(decodeCommand)

            subprocess.call(decodeCommand, shell=True, stdout=output, stderr=output)
            output.flush()

    def decode(self, lang_dir, sphinx_param):
        logger.info("Starting Sphinx decoding into directory '{dir}'.".format(dir=self.project_dir))
        self.make_kaldi_sphinx_link(self.project_dir, self.project_name)
        self.status_function(91, "sphinx decoding")
        self.make_decode_cmd(self.project_dir, lang_dir, self.sphinx_lib, sphinx_param)
