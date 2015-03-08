# -*- coding: utf-8 -*-
import json, logging, os, sys

import voxolab.tools

logger = logging.getLogger(__name__)

def check_and_load(config_file, file_format='json'):

    config = load(config_file, file_format)

    directories_to_check = [link["source"] for link in config['kaldi']['symlinks']]

    # Each directory must exist
    return (all(map(voxolab.tools.check_directory_exists, directories_to_check)), 
            config)

def load(config_file, file_format='json'):

    if(file_format == "json"):
        return json.load(config_file)
    else:
        return None

def init(config):

    # Create symlinks
    [voxolab.tools.override_symlink(link["source"], link["dest"]) for link in config['kaldi']['symlinks']]

