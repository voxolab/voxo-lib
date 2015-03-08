# -*- coding: utf-8 -*-
import os, logging, sys, subprocess

logger = logging.getLogger(__name__)

class SpkDiarization:

    def __init__(self, scripts_dir):
        self.scripts_dir = scripts_dir
        pass

    def script(self, script_name):
        return self.scripts_dir + "/" + script_name

    def run(self, wav_file, working_dir, jar_file, phase1_dir, phase2_dir, input_format):
        logger.info("[Diarization of {audio_file}]".format(audio_file=wav_file))
        command = [self.script('diarization.sh'), wav_file, working_dir, jar_file, phase1_dir, phase2_dir, input_format]
        spk = subprocess.Popen(command)       
        ret_code = spk.wait()
