# -*- coding: utf-8 -*-
import os, logging
import requests
from requests.adapters import HTTPAdapter
from voxolab.decode_tools import DecodeTools
from voxolab.models import DecodeStatus, ProcessType, FileStatus
from voxolab.resilientsession import ResilientSession
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)

class Daemon:

    def __init__(self, token, output_dir, decode_conf, decode_dir, decode_phone_conf=None, decode_en_conf=None):
        self.token = token
        self.session = ResilientSession()

        self.session.headers.update({'Authentication-Token': token})
        self.output_dir = output_dir
        self.decode_conf = decode_conf
        self.decode_phone_conf = decode_phone_conf
        self.decode_en_conf = decode_en_conf
        self.decode_dir = decode_dir
        self.tools = DecodeTools()

        if (not os.path.exists(self.output_dir)):
            os.makedirs(self.output_dir)
        if (not os.path.exists(os.path.join(self.output_dir, 'results'))):
            os.makedirs(os.path.join(self.output_dir, 'results'))
        if (not os.path.exists(os.path.join(self.output_dir, 'download'))):
            os.makedirs(os.path.join(self.output_dir, 'download'))
        if (not os.path.exists(os.path.join(self.output_dir, 'done'))):
            os.makedirs(os.path.join(self.output_dir, 'done'))

    def delete_file_list(self, files_to_delete_url, update_file_url):
        """ Get the file list to decode from the server """
        # Increase max retries
        parsed_uri = urlparse(files_to_delete_url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        self.session.mount(domain, HTTPAdapter(max_retries=1))

        r = self.session.get(files_to_delete_url, allow_redirects=False, timeout=10)

        if(r.status_code == 401):
            logger.error("Wrong token provided.")
            return

        if(r.status_code == 302):
            logger.error("You need server credentials to get the file list.")
            return

        files = r.json()
    
        if(len(files) > 0):
            file = files[0]
            self.tools.clean_decoding_file(self.output_dir, file['generated_filename'])
            self.session.put(update_file_url.format(str(file['id'])), data = '{"status":' + str(FileStatus.Deleted)+'}') 

    def decode_file_list(self, file_list_url, download_url, update_process_url, upload_url):
        """ Get the file list to decode from the server """

        # Increase max retries
        parsed_uri = urlparse(download_url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        self.session.mount(domain, HTTPAdapter(max_retries=1))

        #logger.info('Calling ' + file_list_url + ' with token: ' + self.token)
        r = self.session.get(file_list_url, allow_redirects=False, timeout=10)

        if(r.status_code == 401):
            logger.error("Wrong token provided.")
            return

        if(r.status_code == 302):
            logger.error("You need server credentials to get the file list.")
            return

        files = r.json()

        # Process the first file
        if(len(files) > 0):
            file = files[0]
        #for file in files:

            # Download the file from the server
            if(self.download_file(file, download_url)):

                # Inform the server that we have started the decoding process
                self.session.put(update_process_url + str(file['id']), 
                        data = '{"status":' + str(DecodeStatus.Started)+ '}') 

                if(file['type'] == ProcessType.to_dict()[ProcessType.FullPhoneTranscription] and self.decode_phone_conf is not None):
                    conf = self.decode_phone_conf
                    system = "base"
                elif(file['type'] == ProcessType.to_dict()[ProcessType.FullEnglishTranscription] and self.decode_en_conf is not None):
                    conf = self.decode_en_conf
                    system = "dnn"
                else:
                    conf = self.decode_conf
                    system = "base"

                startTime = datetime.now()
                try:
                    return_code = 0
                    return_code = self.tools.start_decoding(
                            conf = os.path.abspath(conf), 
                            file_name = os.path.abspath(os.path.join(self.output_dir, 'download', file['file_name'])),
                            seg_file = None, 
                            scripts_dir = os.path.abspath(self.decode_dir), 
                            output_dir = os.path.abspath(os.path.join(self.output_dir, 'results')),
                            system = system,
                            status_function=lambda x,y: self.session.put(
                                update_process_url + str(file['id']), 
                                data = '{"status":' + str(DecodeStatus.Started)+ ', "progress":"' + str(x) + '"}')
                            )

                except Exception as e:
                    logger.exception(e)
                    return_code = -1

                total_duration = datetime.now()-startTime

                if(return_code == 0):
                    # Everything's fine, let's update the process with the finish state
                    basename = os.path.splitext(file['file_name'])[0]
                    output_dir = os.path.join(self.output_dir, 'results', basename)
                    srt_output_file = os.path.join(output_dir, basename + '.srt')
                    vtt_output_file = os.path.join(output_dir, basename + '.vtt')
                    ctm_output_file = os.path.join(output_dir, basename + '.ctm')
                    xml_output_file = os.path.join(output_dir, basename + '.xml')

                    self.session.post(upload_url.format(file['file_id']), files={'file': open(srt_output_file, 'rb')})
                    self.session.post(upload_url.format(file['file_id']), files={'file': open(ctm_output_file, 'rb')})
                    self.session.post(upload_url.format(file['file_id']), files={'file': open(xml_output_file, 'rb')})
                    self.session.post(upload_url.format(file['file_id']), files={'file': open(vtt_output_file, 'rb')})

                    self.session.put(update_process_url + str(file['id']), data = '{"status":' + str(DecodeStatus.Finished)+ ', "progress": 100, "duration":"' + str(total_duration) + '"}') 
                else:
                    self.session.put(update_process_url + str(file['id']), data = '{"status":' + str(DecodeStatus.Error)+ ', "duration":"' + str(total_duration) + '"}') 
                    logger.error('Error decoding ' + file['file_name'])
            else:
                self.session.put(update_process_url + str(file['id']), data = '{"status":' + str(DecodeStatus.Error)+ ', "duration":"' + str(0) +'"}') 
                logger.error('Error downloading ' + file['file_name'])



    def download_file(self, file, download_url):
        """ Download a file from the server and save it locally """

        if(not os.path.isfile(os.path.join(self.output_dir, file['file_name']))):
            #logger.info('Calling ' + download_url + ' with token: ' + self.token)

            r = self.session.get(download_url + str(file['file_id']), stream=True)
            if(r.status_code == 200):
                # Save each file locally
                with open(os.path.join(self.output_dir, 'download', file['file_name']), 'wb') as handle:

                    for block in r.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)
            else:
                logger.error('Download of file ' + file['file_name'] + ' failed: ' + str(r.status_code))
                return False
        else:
            logger.info('Skipping ' + file['file_name'] + ' because it was already downloaded.')
        return True

