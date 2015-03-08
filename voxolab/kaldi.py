# -*- coding: utf-8 -*-
import os, logging, sys, subprocess

logger = logging.getLogger(__name__)

class Kaldi:

    def __init__(self, kaldi_dir, project_dir, scripts_dir, sph2pipe_path, mmi_number, lattice_mmi_dir, pseudo_path, log_file, status_function):
        self.kaldi_dir = kaldi_dir
        self.project_dir = project_dir
        self.scripts_dir = scripts_dir
        self.scripts_dir_bin = scripts_dir + "/bin/"
        self.sph2pipe_path = sph2pipe_path
        self.mmi_number = mmi_number
        self.latice_mmi_dir = lattice_mmi_dir
        self.pseudo_path = pseudo_path
        self.log_file = log_file
        self.status_function = status_function

    def script(self, script_name):
        return self.scripts_dir + "/bin/" + script_name

    def make_graph(self, mmi_dir, graph_dir, to_htk_script, lattice_with_keep_time):
        logger.info("[Making graph {}]".format(mmi_dir + str(self.mmi_number)))
        #./faireGraphe.csh decode/anthoRepere/mmi/decrep1ref.6 ./decode/langue/anthoRepere/Graphe30kV5/ latticeMMI

        with open(self.log_file, "a") as output:
            command = [self.script('faireGraphe.sh'), mmi_dir + str(self.mmi_number), graph_dir, self.latice_mmi_dir, to_htk_script, lattice_with_keep_time]
            print(command)
            graph = subprocess.Popen(command, stdout=output, stderr=output, cwd=self.scripts_dir, env = os.environ)
            ret_code = graph.wait()
            output.flush()

    def make_mllr(self, work_dir, graph_dir, sat_dir, num_threads=1, config_file=None):
        logger.info("[Making mllr]")

        with open(self.log_file, "a") as output:

            if config_file:
                command = ['steps/decode_fmllr.sh', '--nj', '1', '--num-threads', str(num_threads), '--cmd', '"run.pl"', '--config', config_file, graph_dir, work_dir, sat_dir]
            else:
                command = ['steps/decode_fmllr.sh', '--nj', '1', '--num-threads', str(num_threads), '--cmd', '"run.pl"', graph_dir, work_dir, sat_dir]

            logger.info(" ".join(command))

            mllr = subprocess.Popen(command, stdout=output, stderr=output, cwd=self.scripts_dir)       
            ret_code = mllr.wait()
            output.flush()

    def align_fmllr(self, work_dir, lang_dir, tri4b_dir, align_dir, num_threads=1, config_file=None):
        logger.info("[Align fmllr]")

        with open(self.log_file, "a") as output:

            #print "Dev fMLLR alignment.\n";
            #system("$c{steps}/align_fmllr.sh --nj $c{dev_nj} --cmd \"$c{train_cmd}\" $c{data_dir}/$c{dev_name} $c{lang} $s0{dir} $s0{final_ali}_$c{dev_name}");

            command = ['steps/align_fmllr.sh', '--nj', '1', '--cmd', '"run.pl"', work_dir, lang_dir, tri4b_dir, align_dir]
            logger.info(" ".join(command))

            fmllr = subprocess.Popen(command, stdout=output, stderr=output, cwd=self.scripts_dir)       
            ret_code = fmllr.wait()
            output.flush()

    def make_fmllr_feats(self, work_dir, tri4b_dir, align_dir, num_threads=1, config_file=None):
        logger.info("[Make fmllr feats]")

        with open(self.log_file, "a") as output:

            #print "Making dev fMLLR features, you need a dev decode from tri4b.\n";
            #system("$c{steps}/make_fmllr_feats.sh --nj $c{dev_nj} --cmd \"$c{train_cmd}\" --transform-dir $s1{dev_dec_dir} $s0{fmllr_feats}/$c{dev_name} $c{data_dir}/$c{dev_name} $s0{dir} $s0{fmllr_feats}/$c{dev_name}/log $s0{fmllr_feats}/$c{dev_name}/data");
            command = ['steps/make_fmllr_feats.sh', '--nj', '1', '--cmd', '"run.pl"', '--transform-dir', align_dir, align_dir + "/fmllr_feats", work_dir, tri4b_dir, align_dir + "/fmllr_feats/log", align_dir + "/fmllr_feats/data"]
            logger.info(" ".join(command))

            fmllr = subprocess.Popen(command, stdout=output, stderr=output, cwd=self.scripts_dir)       
            ret_code = fmllr.wait()
            output.flush()

    def decode_nnet(self, work_dir, nnet_dir, graph_dir, align_dir, num_threads=1, acwt=0.10, config_file=None):
        logger.info("[Decoding using nnet]")

        with open(self.log_file, "a") as output:
		#system("$c{steps}/decode_nnet.sh --nj $c{dev_nj} --cmd \"$c{decode_cmd}\" --acwt $s1{acwt} --config $c{conf_file} --nnet $s1{dir}_sMBR_final/$i.nnet $s0{dir}/$c{graph} $s0{fmllr_feats}/$c{dev_name} $s1{dir}_sMBR_final/$c{decode}_$i && touch $s1{dir}_sMBR_final/.done.$c{decode}_$i");

            command = ['steps/decode_nnet.sh', '--nj', '1', '--num-threads', str(num_threads), '--cmd', '"run.pl"', '--acwt', str(acwt), '--nnet', nnet_dir + "4.nnet", graph_dir, align_dir + "/fmllr_feats", nnet_dir + "4"]

            if config_file:
                command.insert(1,config_file)
                command.insert(1,'--config')

            logger.info(" ".join(command))

            nnet = subprocess.Popen(command, stdout=output, stderr=output, cwd=self.scripts_dir)
            ret_code = nnet.wait()
            output.flush()

    def make_mmi(self, work_dir, graph_dir, sat_dir, mmi_dir, num_threads=1, config_file=None, iter=True):
        logger.info("[Making mmi]")

        with open(self.log_file, "a") as output:
            command=['steps/decode_fmmi.sh', '--nj', '1', '--num-threads', str(num_threads), '--cmd', '"run.pl"', '--transform-dir', sat_dir, graph_dir, work_dir, mmi_dir+str(self.mmi_number)]
            if iter:
                command.insert(1,str(self.mmi_number))
                command.insert(1,'--iter')
            if config_file:
                command.insert(1,config_file)
                command.insert(1,'--config')

            mmi = subprocess.Popen(command, stdout=output, stderr=output, cwd=self.scripts_dir)
            ret_code = mmi.wait()
            output.flush()

    def make_plp(self, work_dir, plp_conf):
        logger.info("[Making plp]")
        with open(self.log_file, "a") as output:
            plp = subprocess.Popen([self.script('fairePlpDev.sh'), work_dir, plp_conf], stdout=output, stderr=output, cwd=self.scripts_dir)       
            ret_code = plp.wait()
            output.flush()

    def prepare_files(self, seg_file, work_dir, audio_file, rate = "16000"):
        logger.info("[Preparing files for rate {} ...]".format(rate))

        self.create_pseudo(self.pseudo_path, seg_file)
        self.create_tmp_files(self.pseudo_path, work_dir, audio_file, self.sph2pipe_path, rate)
        self.sort_files(work_dir)
        self.spk2utt(os.path.join(work_dir, 'utt2spk'), work_dir)

    def spk2utt(self, source, dest_dir):
        with open(os.path.join(dest_dir, 'spk2utt'), "w") as output:
            spk2utt = subprocess.Popen([self.script('utt2spk_to_spk2utt.pl'), source], stdout=output, stderr=output, cwd=self.scripts_dir_bin)
            ret_code = spk2utt.wait()
            output.flush()

    def create_tmp_files(self, pseudo_path, work_dir, audio_file, sph2pipe_path, rate="16000"):
        logger.info("Creating tmp files with 02kaldi.perl")
        #cat testdebreuil2.pseudo | ./02kaldi.perl testdebreuil2 testdebreuil2 sph2pipePath

        with open(self.log_file, "a") as output:
            cat = subprocess.Popen(['cat', pseudo_path], stdout=subprocess.PIPE)       
            kaldiPerl = subprocess.Popen([self.script('02kaldi.perl'), work_dir, audio_file, sph2pipe_path, rate], stdin = cat.stdout, stdout=output, stderr=output, cwd=self.scripts_dir_bin)
            ret_code = kaldiPerl.wait()
            output.flush()

    def sort_files(self, directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        for f in files:
            lines = []

            with open(os.path.join(directory, f), "r") as aFile:
                # omit empty lines and lines containing only whitespace
                lines = [line for line in aFile if line.strip()]

            lines.sort()

            with open(os.path.join(directory, f), "w") as aFile:
                logger.info("Sorting file {file}".format(file=f))
                # omit empty lines and lines containing only whitespace
                aFile.writelines(lines)

    def create_pseudo(self, path, seg_file):
        logger.info("Creating .pseudo file")
        with open(path, "w") as log:
            # cat testdebreuil2/seg/testdebreuil2.g.seg | ./51meignier2ctm.perl > testdebreuil2.pseudo
            cat = subprocess.Popen(['cat', seg_file], stdout=subprocess.PIPE)       
            meignier2ctm = subprocess.Popen([self.script('51meignier2ctm.perl')], stdin = cat.stdout, stdout=log, stderr=log, cwd=self.scripts_dir_bin)
            ret_code = meignier2ctm.wait()
            log.flush()

    def decode(self, seg_file, work_dir, audio_file, graph_dir, sat_dir, mmi_dir, num_threads, plp_conf, to_htk_script, lattice_with_keep_time, rate="16000"):
        logger.info("Starting Kaldi decoding into directory '{dir}'.".format(dir=self.project_dir))
        self.prepare_files(seg_file, work_dir, audio_file, rate)

        self.status_function(10, "plp")
        self.make_plp(work_dir, plp_conf)

        self.status_function(10, "mllr")
        self.make_mllr(work_dir, graph_dir, sat_dir, num_threads)

        self.status_function(60, "mmi")
        self.make_mmi(work_dir, graph_dir, sat_dir, mmi_dir, num_threads)

        self.status_function(90, "graph")
        self.make_graph(mmi_dir, graph_dir, to_htk_script, lattice_with_keep_time)


    def decode_dnn(self, seg_file, work_dir, audio_file, graph_dir, sat_dir, mmi_dir, num_threads, plp_conf, to_htk_script, lattice_with_keep_time, rate="16000", config_file=None, lang_dir=None, tri4b_dir=None, nnet_dir=None):
        logger.info("Starting Kaldi DNN decoding into directory '{dir}'.".format(dir=self.project_dir))
        self.prepare_files(seg_file, work_dir, audio_file, rate)

        self.status_function(10, "plp")
        self.make_plp(work_dir, plp_conf)

        self.status_function(10, "mllr")
        self.make_mllr(work_dir, graph_dir, sat_dir, num_threads, config_file)

        self.status_function(10, "make fmllr feats")
        self.make_fmllr_feats(work_dir, tri4b_dir, sat_dir)

        self.status_function(11, "decoding using nnet")
        self.decode_nnet(work_dir, nnet_dir, graph_dir, sat_dir, num_threads=num_threads, config_file=config_file)


        self.status_function(90, "graph")
        self.mmi_number=4
        self.make_graph(nnet_dir, graph_dir, to_htk_script, lattice_with_keep_time)
