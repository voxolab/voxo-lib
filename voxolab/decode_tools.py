# -*- coding: utf-8 -*-
import logging, argparse, sys, os, locale, voxolab, traceback
import shutil
from voxolab import config, tools
from voxolab.kaldi import Kaldi
from voxolab.sphinx import Sphinx
from voxolab.spk_diarization import SpkDiarization
from voxolab import convert, ctm_alpha_to_numbers


logger = logging.getLogger(__name__)

class DecodeTools:

    def __init__(self):
        pass

    def clean_decoding_file(self, output_dir, file_name):

        download_file_name = os.path.abspath(os.path.join(output_dir, 'download', file_name))

        # The project name is the audio filename without the extension
        project_name = os.path.splitext(os.path.basename(file_name))[0]
        project_dir = os.path.join(output_dir, project_name)

        logger.info('Tying to clean {} and {}'.format(download_file_name, project_dir))

        if os.path.exists(project_dir):
            logger.info('Cleaning {}'.format(project_dir))
            shutil.rmtree(project_dir)

        if os.path.exists(download_file_name):
            logger.info('Cleaning {}'.format(download_file_name))
            os.remove(download_file_name)

    def start_decoding(self, conf, file_name, seg_file, scripts_dir, output_dir, system="base", silent=True, status_function=lambda x,y: logging.info(x)):

        if(not os.path.isabs(conf) or not os.path.abspath(file_name) or not os.path.abspath(scripts_dir) or not os.path.abspath(output_dir) or (seg_file is not None and not os.path.abspath(seg_file))):
            logging.error("All the paths have to be absolute.")
            return -1

        logger.info("[Parameters]")
        logger.info("conf: " + conf)
        logger.info("file_name: " + file_name)
        logger.info("seg_file: " + str(seg_file))
        logger.info("scripts_dir: " + scripts_dir)
        logger.info("output_dir: " + output_dir)
        logger.info("system: " + system)
        logger.info("silent: " + str(silent))

        status_function(0, "start") 

        old_path = os.environ['PATH']

        try:
            with open(conf) as config_file:

                # Load config from config file
                config_array = config.load(config_file)
                config.init(config_array)

                if '-' in output_dir:
                    logger.error("The full path to the output_dir should not contain any '-'.")
                    return -1

                # Setting paths
                os.environ['PATH'] = os.environ['PATH'] + ":/usr/bin/:/bin/:{PWD}:{PWD}/bin/:{PWD}/utils/:{KALDI_ROOT}/src/bin:{KALDI_ROOT}/tools/openfst/bin:{KALDI_ROOT}/src/fstbin/:{KALDI_ROOT}/src/gmmbin/:{KALDI_ROOT}/src/featbin/:{KALDI_ROOT}/src/lm/:{KALDI_ROOT}/src/sgmmbin/:{KALDI_ROOT}/src/sgmm2bin/:{KALDI_ROOT}/src/fgmmbin/:{KALDI_ROOT}/src/latbin/:{KALDI_ROOT}/src/nnetbin:{KALDI_ROOT}/tools/sph2pipe_v2.5/:{KALDI_ROOT}/src/nnet-cpubin:{LM_TOOLS}".format(KALDI_ROOT=config_array['kaldi']['dir'], PWD=scripts_dir, LM_TOOLS=config_array['lm_tools'])
                
                # Setting correct locale
                os.environ['LC_ALL'] = "C"
                locale.setlocale(locale.LC_ALL,"C")

                # The project name is the audio filename without the extension
                project_name = os.path.splitext(os.path.basename(file_name))[0]

                if '-' in project_name:
                    logger.error("'-' are not allowed in the file name.")
                    return -1

                status_function(1, "creating directories") 

                #File needed for kaldi and sphinx
                project_dir = os.path.join(output_dir, project_name)
                pseudo_path = os.path.join(project_dir, project_name + ".pseudo")
                wav_file = os.path.join(project_dir, project_name + ".wav")
                sph_file = os.path.join(project_dir, project_name + ".sph")
                log_file = os.path.join(project_dir, project_name + ".log")
                ctm_file_numbers = os.path.join(project_dir, project_name + ".MAJ.numbers.ctm")
                ctm_file_maj = os.path.join(project_dir, project_name + ".MAJ.ctm")
                ctm_file_min = os.path.join(project_dir, project_name + ".min.ctm")
                ctm_file = os.path.join(project_dir, project_name + ".ctm")
                xml_file_maj = os.path.join(project_dir, project_name + ".MAJ.xml")
                xml_file = os.path.join(project_dir, project_name + ".xml")
                stm_file = os.path.join(project_dir, project_name + ".stm")
                srt_file = os.path.join(project_dir, project_name + ".srt")
                webvtt_file = os.path.join(project_dir, project_name + ".vtt")
                latp5_dir = os.path.join(project_dir, 'latp5', project_name)

                iv_seg_file = os.path.join(project_dir, "seg/") + project_name + ".iv.seg"
                g_seg_file = os.path.join(project_dir, "seg/") + project_name + ".g.seg"

                # If the output dir already exists, warn the user
                if (os.path.exists(project_dir) and not silent):
                    if(not tools.query_yes_no("The directory {dir} already exists, are you sure do you want to override the results?".format(dir=project_dir))):
                        return -1
                        
                # Create dirs
                dirs_to_create = ["", "working_dir", "latp2", "latp3", "latp4", "latp5", "log", "seg"]
                [tools.create_dir_if_not_exist(os.path.join(project_dir, directory)) for directory in dirs_to_create]

                status_function(3, "converting file to wav") 
                # Convert file
                convert.anything_to_wav(file_name, wav_file, config_array['sample_rate'], log_file)

                status_function(4, "converting wav to sph") 
                convert.wav_to_sph(wav_file, sph_file, config_array['sample_rate'], log_file)

                if(not os.path.isfile(wav_file)):
                    logger.error("The wav conversion has failed. Aborting.")
                    return -1


                if(not os.path.isfile(sph_file)):
                    logger.error("The sph conversion has failed. Aborting.")
                    return -1

                # Diarization
                if(not seg_file):
                    status_function(5, "segmenting file") 
                    d = SpkDiarization(os.path.join(scripts_dir, 'bin'))
                    d.run(wav_file, os.path.join(project_dir, "seg"), config_array['spk_diarization']['lib'], config_array['spk_diarization']['phase1'], config_array['spk_diarization']['phase2'], config_array['spk_diarization']['input_format'])
                    seg_file = g_seg_file
                else:
                    seg_file = seg_file

                # Create Kaldi decoding class
                k = Kaldi(config_array['kaldi']['dir'], 
                        project_dir, 
                        os.path.join(scripts_dir), 
                        config_array['kaldi']['sph2pipe'], 
                        6, 
                        os.path.join(project_dir, "lattice_mmi"),
                        pseudo_path,
                        log_file,
                        status_function
                        )
                
                if system == "dnn":
                    status_function(10, "DNN kaldi decoding") 

                    k.decode_dnn(
                            seg_file=seg_file, 
                            work_dir=project_dir + "/working_dir", 
                            audio_file=sph_file,
                            graph_dir=config_array['graph'],
                            sat_dir=config_array['sat'] + project_name,
                            mmi_dir=config_array['mmi'],
                            num_threads=config_array['num_threads'],
                            plp_conf=config_array['plp_conf'],
                            rate=config_array['sample_rate'],
                            config_file=config_array['kaldi']['config_file'],
                            lang_dir=config_array['kaldi']['lang'],
                            tri4b_dir=config_array['kaldi']['tri4b_dir'],
                            nnet_dir=config_array['kaldi']['nnet_dir'],
                            to_htk_script=config_array['to_htk'],
                            lattice_with_keep_time=config_array['kaldi']['lattice_with_keep_time']
                            )
                else:
                    status_function(10, "base kaldi decoding") 
                    # Before decoding, we should check that the name of the show in the seg file,
                    # is the same as the project_name

                    k.decode(
                            seg_file=seg_file, 
                            work_dir=project_dir + "/working_dir", 
                            audio_file=sph_file,
                            graph_dir=config_array['graph'],
                            sat_dir=config_array['sat'] + project_name,
                            mmi_dir=config_array['mmi'],
                            num_threads=config_array['num_threads'],
                            plp_conf=config_array['plp_conf'],
                            rate=config_array['sample_rate'],
                            to_htk_script=config_array['to_htk'],
                            lattice_with_keep_time=config_array['kaldi']['lattice_with_keep_time']
                            )


                # Create Sphinx decoding class
                s = Sphinx(config_array['sphinx']['lib'], 
                        project_name,
                        project_dir, 
                        os.path.join(scripts_dir), 
                        os.path.join(output_dir, project_name, "lattice_mmi"),
                        pseudo_path,
                        log_file,
                        status_function)


                status_function(90, "sphinx decoding") 
                s.decode(config_array['sphinx']['lang'], config_array['sphinx']['param'])

                status_function(95, "creating output files") 


                if system != "dnn":
                    s.make_ctm(latp5_dir, ctm_file_min)
                    convert.recase_ctm(ctm_file_min, ctm_file_maj, config_array['recasing'])
                    ctm_alpha_to_numbers.ctm_alpha_to_numbers(ctm_file_maj, os.path.join(scripts_dir,'bin/convertirAlphaEnNombre.pl'), ctm_file)
                    s.make_xml(latp5_dir, iv_seg_file, xml_file, ctm_file_maj)
                else:
                    s.make_ctm(latp5_dir, ctm_file)
                    s.make_xml(latp5_dir, iv_seg_file, xml_file, ctm_file, False, False)

                convert.ctm_to_srt(ctm_file, srt_file)
                convert.ctm_to_webvtt(ctm_file, webvtt_file)

                status_function(100, "end") 

                # Let's try to not create an infinity of redundant paths …
                os.environ['PATH'] = old_path
                return 0


        except IOError as e:
            logger.error(str(e))
            traceback.print_exc(file=sys.stderr)
            logger.error("You need to create a config.json file before. You can use the sample file 'config.json.sample'.")
            # Let's try to not create an infinity of redundant paths …
            os.environ['PATH'] = old_path
