# -*- coding: utf-8 -*-
import os, logging, sys

logger = logging.getLogger(__name__)

def check_directory_exists(path):
    if os.path.isdir(path) and os.path.exists(path):
        return True
    else:
        logger.info("Directory {dir} doesn't exist.".format(dir=path))
        return False

def check_file_exists(path):
    if os.path.isfile(path):
        return True
    else:
        logger.info("File {file} doesn't exist.".format(file=path))
        return False

def create_dir_if_not_exist(path):
    if (not os.path.isdir(path) and not os.path.exists(path)):
        os.mkdir(path)

def override_symlink(source, dest):
    try:
        os.remove(dest)
    except OSError as err:
        logger.info("Symlink error {err}.".format(err=err))

    os.symlink(source, dest)

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True, "y":True, "ye":True, "no":False, "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")
