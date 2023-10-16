import os
import argparse
import logging
import requests
import xml.etree.ElementTree as ET


from datetime import datetime
from requests import HTTPError
from yt_dlp import YoutubeDL, DownloadError

# create logging formatter
logFormatter = logging.Formatter(fmt=' [%(name)s] %(message)s')


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process input data")

    parser.add_argument('-j', '--jobs', type=int, help="number of jobs/threads", default=8)
    parser.add_argument('-f', '--flatten', action='store_true', help="Output to the current directory.", default=False)
    parser.add_argument('-d', '--delete', action='store_true', help="Delete the data", default=False)
    parser.add_argument('-o', '--output_dir', type=str, help="Output directory", default=".")
    parser.add_argument('-i', '--input', default='channels.txt', type=str, help="Input file (default: channels.txt), formatted as one channel on each line, with a comma separated 'last updated' date (optional)")

    args = parser.parse_args()
    return args

def get_video_urls(url, last_date=None):
    logging.info("Requesting from:", url)
    try:
        xml_str = requests.get(url).text
        root = ET.fromstring(xml_str)
    except Exception as e:
        logging.error(f"Error parsing xml from url, {e})")
        exit(1)

    # For some reason they all have this namespace thing so this is the cleanest way to get around it I think
    ns = {"ns" : "http://www.w3.org/2005/Atom"}

    channel_name = root.find('ns:title', namespaces=ns).text
    
    logging.info("Parsing channel:", channel_name)

    most_recent_date = None
    videos = []
    for entry in root.findall('ns:entry', namespaces=ns):
        video_title = entry.find('ns:title', namespaces=ns).text
        video_uri = entry.find('ns:link[@rel="alternate"]', namespaces=ns).attrib['href']
        published_date = datetime.fromisoformat(entry.find('ns:published', namespaces=ns).text)
        if most_recent_date is None or published_date > most_recent_date:
            most_recent_date = published_date

        if last_date is None or last_date < published_date:
            logging.info("\tAdding video:", video_title)
            videos.append(video_uri)
        else:
            logging.info("\tSkipping video:", video_title)

    if last_date is not None and (most_recent_date is None or last_date > most_recent_date):
        most_recent_date = last_date

    return ( videos, channel_name, most_recent_date)

def youtubeDlHook(d):
    # if d['status'] == 'downloading':
    #     print('Downloading video!')
    if d['status'] == 'finished':
        logging.info('\nDownloaded!')

if __name__ == '__main__':
    args = parse_arguments()
    # 1. Read from input file and collect the videos to be downloaded
    # As well as latest timestamps
    if not os.path.exists(args.input):
        logging.info("Necessary file", args.input, "doesn't exist!")
        exit(1)

    if args.jobs < 1:
        logging.info("Invalid value for --jobs!")
        exit(1)

    base_output_dir = args.output_dir


    new_channel_urls = []
    videos = {}
    with open(args.input, "r") as input_channels:
        
        for line_num, line in enumerate(input_channels.readlines()):
            split_line = line.split(',')
            last_date = None
            if len(split_line) == 1:
                url = split_line[0]
            elif len(split_line) == 2:
                url = split_line[0]
                last_date = datetime.fromisoformat(split_line[1])
            else:
                logging.error("Channel file is ill formatted at line:", line_num)
                exit(1)

            # Get all the video urls after the last date.
            new_video_urls, channel_name, latest_date = get_video_urls(url, last_date)
            videos[channel_name] = new_video_urls

            new_channel_urls.append((url, latest_date))

    get_output_dir = lambda c_name: args.output_dir if args.flatten else os.path.join(args.output_dir, c_name)

    # 2. make any directories if necessary (could do while downloading but whatever)
    for channel_name in videos:
        dir_path = get_output_dir(channel_name)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            continue
        # 3. delete any files in those directories if we are deleting
        if args.delete:
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                # Avoid deleting subdirs
                if os.path.isfile(file_path):
                    logging.info("Deleting old file:", file_path)
                    os.remove(file_path)

    youtubeDl_opts = {
        "continue": True,
        "progress_hooks": [youtubeDlHook],
        "check_formats": "selected"
    }

    # 4. Download all of the files.
    for channel_name in videos:
        starting_dir = os.getcwd()
        output_dir = get_output_dir(channel_name)
        os.chdir(output_dir)
        try:
            with YoutubeDL(youtubeDl_opts) as ydl:
                ydl.download(videos[channel_name])
        except HTTPError as e:
            logging.error(f"got http error {e}")
        except DownloadError as e:
            logging.error(f"got download error: {e}")

        os.chdir(starting_dir)

    # 5. Update the input file
    logging.info(f"new channel urls {new_channel_urls}")
    with open(args.input, "w") as input_channels:
        input_channels.writelines(map(lambda url, date: url + "," + date.isoformat(), new_channel_urls))


    



