# -*- coding: utf-8 -*-
import os, logging, sys, subprocess, datetime, json, re, time, codecs
import xml.etree.ElementTree as etree

logger = logging.getLogger(__name__)

def anything_to_wav(source, destination, rate = "16000", log_file = None):
    """
    Convert any media file that ffmpeg can read to a wav file.
    """

    #ffmpeg -i $1  -vn -acodec pcm_s16le -ac 1 $2
    command = ['ffmpeg', "-y", "-i", source, "-vn", "-acodec", "pcm_s16le", "-ar", rate, "-ac", "1", destination]

    if(log_file is not None):
        logger.info("Logging to " + log_file)

        with open(log_file, "a") as output:
            ffmpeg = subprocess.Popen(command, stdout=output, stderr=output)
            ret_code = ffmpeg.wait()
            output.flush()
    else:
        ffmpeg = subprocess.Popen(command)       
        ret_code = ffmpeg.wait()

    return ret_code

def video_to_mp4(source, destination):
    #Todo
    #ffmpeg -i 411423.mp4 -vcodec h264 -acodec aac -threads 8 -strict -2 411423.h264.mp4
    pass

def video_to_webm(source, destination):
    #Todo
    #ffmpeg  -i "fichier source" -codec:v libvpx -quality good -cpu-used 0 -b:v 600k -maxrate 600k -bufsize 1200k -qmin 10 -qmax 42 -vf scale=-1:480 -threads 8 -codec:a libvorbis -b:a 128k sortie_480p.webm
    pass

def wav_to_sph(source, destination, rate = "16000", log_file = None):
    """
    Convert a wav to a sph (NIST Sphere format) using sox.
    """

    #sox lcp_q_gov.wav -r16000 lcp_q_gov.sph
    command = ['sox', source, ("-r" + rate), destination]

    if(log_file is not None):
        logger.info("Logging to " + log_file)

        with open(log_file, "a") as output:
            sox = subprocess.Popen(command, stdout=output, stderr=output)       
            ret_code = sox.wait()
            output.flush()
    else:
        sox = subprocess.Popen(command)       
        ret_code = sox.wait()

    return ret_code

def get_duration(source, seconds = False):
    """
    Extract the duration from a media file.
    Returns a tuple with the duration in a human readable format
    and in seconds
    """

    command = ['ffmpeg', "-i", source]
    cmd = subprocess.Popen(command, stderr=subprocess.PIPE)
    infos, err = cmd.communicate()
    output = err.decode("utf-8")
    match = re.match(r'.*Duration: (\S*), .*', output, re.DOTALL)

    duration = "00:00:00.00"

    if(match):
        duration = match.group(1)

    d = time.strptime(duration, '%H:%M:%S.%f')
    seconds = datetime.timedelta(hours=d.tm_hour,minutes=d.tm_min,seconds=d.tm_sec).total_seconds()

    return (duration, seconds)

def seconds_to_srt_format(seconds):
    """
    Utility function to convert seconds to the time format used in srt files.
    Example format is 19:09:55,080
    """
    start_seconds="{time:.3f}".format(time = seconds).split('.')
    start_str = str(datetime.timedelta(seconds=int(start_seconds[0]), milliseconds=int(start_seconds[1])))

    # Hours should alway be on 2 digits
    parts = start_str.split(':')
    if(len(parts[0]) == 1):
            start_str = "0{}".format(start_str)

    # If they are decimals, truncate it from 6 to 3 decimals
    # Otherwise add three 000
    if('.' in start_str):
        start_str = start_str.replace(' ', '')[:-3]
    else:
        start_str += '.000'

    return start_str

def xml_to_txt(source, destination, source_encoding='utf-8'):
    entries = xml_to_entries(source, destination, source_encoding)
    return write_txt(entries, destination)

def xml_to_srt(source, destination, source_encoding='utf-8'):
    entries = xml_to_entries(source, destination, source_encoding)
    return write_subtitle(entries, destination, 'srt')

def xml_to_webvtt(source, destination, source_encoding='utf-8'):
    entries = xml_to_entries(source, destination, source_encoding)
    return write_subtitle(entries, destination, 'webvtt')

def xml_to_entries(source, destination = None, source_encoding='utf-8'):

    # We load the full tree in memory as files should not be too big
    # another solution could be to use the iterparse function
    # Cf. http://effbot.org/zone/element-iterparse.htm
    tree = etree.parse(source)
    root = tree.getroot()
    entries=[]
    should_cut = False
    for sentence in root:
        sa = sentence.attrib
        for word in sentence:
            wa = word.attrib

            # Remove space after ', and attach the word on the previous line
            if(len(entries) > 0):
                last_word, last_time, last_gender, last_quality, last_speaker, last_should_cut = entries[-1]
                if(last_word.endswith("'")):
                    entries[-1]=(last_word + wa['value'], last_time, sa['gender'], sa['type'], sa['speaker'], last_should_cut)
                    continue

            entries.append((wa['value'], float(wa['start']), sa['gender'], sa['type'], sa['speaker'], should_cut))
            should_cut = False

        should_cut = True


    return entries


def ctm_to_subtitle(source, destination = None, seg = None, stm = None, sub_format='srt', source_encoding='ISO-8859-1'):

    """
    Convert a ctm file to the srt subtitle format. 
    Srt files are used by programs like VLC for example
    """

    # Read segmentation information if any

    frames = {}
    if seg:
        seg_file = codecs.open(seg, 'r', encoding = source_encoding)

        try:
            # For each frame, we will create an entry in a dictionnary
            # It will help the lookup later on
            # We don't really care about memory issues here, should we?
            for line in seg_file:
                if line.startswith(';;'):
                    continue

                values = line.split()
                start = int(values[2])
                duration = int(values[3])

                for i in range(start, start + duration):
                    frames[i] = values[4], values[5], values[7]
        finally:
            seg_file.close()

    # Read stm segmentation if any (to cut subtitles)
    cuts = []
    if stm:
        stm_file = codecs.open(stm, 'r', encoding = source_encoding)

        try:
            # For each frame, we will create an entry in a dictionnary
            # It will help the lookup later on
            # We don't really care about memory issues here, should we?
            for line in stm_file:
                if line.startswith(';;'):
                    continue

                values = line.split()
                start = int(float(values[3])*100)
                cuts.append(start)
        finally:
            stm_file.close()

    gender=quality=speaker=None

    # Read the ctm file and do some pre-processing
    entries=[]
    cut_index = 0
    nb_cuts = len(cuts)
    with open(source, "r", encoding=source_encoding) as f:
        content = f.readlines()
        for line in content:
            parts = line.split(' ')
            word = parts[4]
            time = float(parts[2])
            # Use the same start format than in the .seg file
            start_frame = int(time*100)

            if(start_frame in frames):
                gender, quality, speaker = frames[start_frame] 

            should_cut = False

            if(cut_index < nb_cuts):
                if(start_frame > cuts[cut_index]):
                    should_cut = True 
                    cut_index += 1

            # Remove space after ', and attach the word on the previous line
            if(len(entries) > 0):
                last_word, last_time, last_gender, last_quality, last_speaker, last_should_cut = entries[-1]
                if(last_word.endswith("'")):
                    entries[-1]=(last_word + word, last_time, gender, quality, speaker, last_should_cut)
                    continue

            entries.append((word, time, gender, quality, speaker, should_cut))

    write_subtitle(entries, destination, sub_format)

def write_txt(entries, destination = None):
    """Generic function to write a txt output based on data generated 
    before (by reading a ctm, seg, xml, whatever)

    :entries: list of tuples (word, time, gender, quality, speaker, should_cut)
    :destination: the destination file
    :returns: nothing, write to the destination file

    """

    # Write to a file if provided, otherwise write to stdout
    output = codecs.open(destination, 'w', encoding = 'utf-8') if destination else sys.stdout

    # Init some defaults
    nb_entries = len(entries)
    words=[]
    start_time=0
    current_time=0
    new_line=False
    previous_speaker=None
    display_speakers=True
    nb_chars=0
    next_word= next_time= next_gender= next_quality= next_speaker= next_should_cut = ""
    content = ''

    for i, entry in enumerate(entries):
        (word, time, gender, quality, speaker, should_cut) = entry

        if(i!=nb_entries -1):
            (next_word, next_time, next_gender, next_quality, next_speaker, next_should_cut) = entries[i+1]

        # Should I create a new line

        #print(should_cut)
        if(should_cut or (speaker != previous_speaker and previous_speaker is not None)):
            content = content + "\n\n"

        content += word + ' '
        # Keep trace of the previous speaker
        previous_speaker = speaker


    print(content, file=output)

    if output is not sys.stdout:
        output.close()


def write_subtitle(entries, destination = None, sub_format='srt'):
    """Generic function to write a subtitle file (srt, webvtt) based on
    data that was generated before (by reading a ctm, seg, xml, whatever)

    :entries: list of tuples (word, time, gender, quality, speaker, should_cut)
    :destination: the destination file
    :sub_format: the format to write to, srt or webvtt
    :returns: nothing, write to the destination file

    """

    def display_subtitle_line(start_time, time, sub_format, srt_number, words, output):
        """
        Utility function to display a subtitle
        """

        start_str = seconds_to_srt_format(start_time)
        end_str = seconds_to_srt_format(time)

        # If the format is .srt, we should print the 
        # subtitle number
        if(sub_format == 'srt'):
            print(str(srt_number), file=output)

        # If .srt format, the decimals are separated with ,
        if(sub_format == 'srt'):
            start_str = start_str.replace('.', ',')
            end_str = end_str.replace('.', ',')

        # Display the start/end time
        print("{start} --> {end}".format(start=start_str, end=end_str), file=output)

        # Add the words to the content
        content_to_add = ' '.join(words).replace('\n ', '\n')
        print(content_to_add+"\n", file=output)


    # Write to a file if provided, otherwise write to stdout
    output = codecs.open(destination, 'w', encoding = 'utf-8') if destination else sys.stdout

    # Init some defaults
    nb_entries = len(entries)
    words=[]
    start_time=0
    current_time=0
    srt_number=0
    new_subtitle=False
    previous_speaker=None
    srt_content=''
    max_subtitle_size=36
    display_speakers=True
    line_number=0
    nb_chars=0
    next_word= next_time= next_gender= next_quality= next_speaker= next_should_cut = ""
    
    if(sub_format=='webvtt'):
        print('WEBVTT\n', file=output)

    for i, entry in enumerate(entries):
        (word, time, gender, quality, speaker, should_cut) = entry

        if(i!=nb_entries -1):
            (next_word, next_time, next_gender, next_quality, next_speaker, next_should_cut) = entries[i+1]

        if(i == 0):
            start_time = time

        # Should I create a new subtitle entry?
        if(new_subtitle):

            time = time-0.2
            display_subtitle_line(start_time, time, sub_format, srt_number, words, output)

            # Reset start time
            start_time=time
            # Reset the new_subtitle flag
            new_subtitle = False
            # Reset the next words to display
            words=[]
            # Reset the line number
            line_number = 0
            # Reset the char counter
            nb_chars = 0

        # Append the words

        # Capitalize the first word and add a – for a speaker change
        if(i == 0 or (previous_speaker is not None and previous_speaker != speaker)):
            word = word.capitalize()
            if(display_speakers and speaker is not None and not re.match(r'^S\d+', speaker)):
                display_speaker = speaker.replace('_',' ').lower().title()
                word = '— <v {}><i><b>{}</b></i> : {}</v>'.format(display_speaker, display_speaker, word)
            else:
                word = '— {}'.format(word)

        words.append(word)
        # +1 because we will add a space to the word
        nb_chars += len(word) + 1

        next_size = nb_chars + len(next_word)

        # Split the subtitle every 5 line
        if(next_size > 36):
            if(line_number == 0):
                words.append('\n')
                line_number = 1
            else:
                line_number = 2
            nb_chars = 0

        # Conditions to create a new subtitle entry
        if(line_number == 2 or (next_speaker != speaker)):
            srt_number+=1
            new_subtitle=True

        # Keep trace of the previous speaker
        previous_speaker = speaker


    # Last line
    if(len(words) > 0):
        display_subtitle_line(start_time, time, sub_format, srt_number + 1, words, output)

    if output is not sys.stdout:
        output.close()



def ctm_to_srt(source, destination, seg = None, stm = None, source_encoding='ISO-8859-1'):
    return ctm_to_subtitle(source, destination, seg, stm, 'srt', source_encoding)

def ctm_to_webvtt(source, destination, seg = None, stm = None, source_encoding='ISO-8859-1'):
    return ctm_to_subtitle(source, destination, seg, stm, 'webvtt', source_encoding)


def seg_ctm_to_json(seg_ctm_path, destination, source_encoding='ISO-8859-1'):
    """
    Convert a special ctm file (with the segmentation information in it) to a 
    json file used for the web demo
    """

    output = {} 
    word_list = []
    with open(seg_ctm_path, "r", encoding=source_encoding) as seg_ctm_f:
        seg_ctm_content = seg_ctm_f.readlines()

        for line in seg_ctm_content:
            parts = line.rstrip('\n').split(' ')
            word_list.append({
                "start":parts[2],
                "word":parts[4],
                "spk":{
                "id":parts[8],
                "gender":parts[6]
                }
            })


    output['content'] = word_list

    transcriptions = []
    transcriptions.append(output)
    with open(destination, "w", encoding='utf-8') as output_f:
        output_f.write(json.dumps(transcriptions))

def recase_ctm(source, destination, recasing_path, log_file=None, file_encoding='ISO8859-1'):
    """
    Add case to a ctm file
    """

    #sox lcp_q_gov.wav -r16000 lcp_q_gov.sph
    command = ['java', '-ea', '-cp', os.path.join(recasing_path, 'sphinx4.jar'), ('-Dfile.encoding=' + file_encoding), 'edu.cmu.sphinx.tools.batch.BatchMajuscule', os.path.join(recasing_path,'majuscule.config.xml'), source, destination]

    return run_command(command, log_file, recasing_path)

def xmlv1_to_v2(source, destination, log_file=None, input_encoding='ISO8859-1', output_encoding='utf-8'):
    """
    Convert the old messy format (legacy of the first system) to a cleaner one
    """
    print("Converting {} {} to {} {}".format(source, input_encoding, destination, output_encoding))


    output = []
    with open(source, "r", encoding=input_encoding) as xmlv1:
        content = xmlv1.readlines()

        for line in content:
            line = re.sub('ISO-8859-1', 'utf-8', line)
            line = re.sub('locuteur=', 'speaker=', line)
            line = re.sub('sexe=', 'gender=', line)
            line = re.sub('scoreConfiance=', 'score=', line)
            line = re.sub('scoreProp=', 'score=', line)
            line = re.sub('mot=', 'value=', line)
            line = re.sub('sel=', 'value=', line)
            output.append(line)

    output.insert(1,"""<!DOCTYPE SHOW PUBLIC "-//VOXOLAB//DTD XML v2.0//EN"
      "http://docs.voxolab.com/voxolab-xmlv2.dtd">\n""")

    with open(destination, "w", encoding=output_encoding) as output_f:
        output_f.write("".join(output))


def run_command(command, log_file=None, cwd = None):
    """
    Run a system command and log to a file if provided
    """


    if(log_file is not None):
        with open(log_file, "a") as output:
            if(cwd is not None):
                p = subprocess.Popen(command, stdout=output, stderr=output, cwd=cwd)       
            else:
                p = subprocess.Popen(command, stdout=output, stderr=output)       
            ret_code = p.wait()
            output.flush()
    else:
        if(cwd is not None):
            p = subprocess.Popen(command, cwd=cwd)       
        else:
            p = subprocess.Popen(command)       

        ret_code = p.wait()

    return ret_code
