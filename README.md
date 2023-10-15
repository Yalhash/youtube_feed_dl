# Offline Youtube Feed
This program polls different channels you are interested in and downloads the latest files on them.  

## Why?
To avoid scrolling on youtube so much, to have access to videos offline, to streamline the youtube dl process for a specific use case I had.

## Usage:
Run the main file. For basic functionality, it expects a channels.txt file with each line being a url to the xml feed for a youtube channel.
It will output all the latest content from that channel (Note the feed only goes back ~10 videos.) and in subsequent runs, it will only find videos after the latest.  
By default the files will go into a folder in the current directory based on the channel name.  
You can change the location using the -o flag, and you can make the output not split by using the -f flag.  
you can also change the input file with the -i flag.  


## Future Improvements
1. Split this into more manageable files  
2. Offer a better way to delete old files... Perhaps check file info like modification date? As of now we just delete everything  
3. Similar to above, but offer a better interface for the date information. Currently the given input file is modified. Pretty dumb



