import os
import re
import urllib2
from BeautifulSoup import BeautifulSoup

def simple_rename(file_dir, show_name, season_number, rename=False):
    ''' Renames episodes in a folder to the friendly format
        show.name.SXX.EXX.ext
        
        if rename=False perform operation without actually renaming files
    '''
    warnings = 0
    warning_msgs = []
    
    print "New name:            Original name:"
    
    for i in os.listdir(file_dir):
        four_digit_match = re.search('%s\d\d' % season_number, i)
        text_digit_match = re.search('(?i)S%sE\d\d' % season_number,i)
        season_x_num = re.search('%sx\d\d' % season_number, i)
        # Get file extension, if none use nothing and mark as a warning
        file_ext_search = re.search('(?i)\.avi|\.mkv',i)

        if file_ext_search is not None:
            file_ext = file_ext_search.group(0)
        else:
            file_ext = ""
            warnings += 1
            warning_msgs.append("%s had no file extension" % i)
            
        if four_digit_match is not None:
            season_episode = four_digit_match.group(0)
            new_name = show_name + '.S%sE%s' % (season_number, season_episode[2:]) + file_ext
            print new_name,
            print i
            if rename is True:
                os.rename(file_dir + i, file_dir + new_name)
           
        if text_digit_match is not None:
            new_name = show_name + '.' + text_digit_match.group(0).upper() + file_ext
            print new_name,
            print i
            if rename is True:
                os.rename(file_dir + i, file_dir + new_name)
                
        if season_x_num is not None:
            season_episode = season_x_num.group(0)
            new_name = show_name + '.S%sE%s' % (season_number, season_episode[-2:]) + file_ext
            print new_name,
            print i
            if rename is True:
                os.rename(file_dir + i, file_dir + new_name)
        
        if season_number[0] == '0':
            season_ep = re.search('%s\d\d' % season_number[1], i)
            if season_ep is not None:
                season_episode = season_ep.group(0)
                new_name = show_name + '.S%sE%s' % (season_number, season_episode[1:]) + file_ext
                print new_name,
                print i
                if rename is True:
                    os.rename(file_dir + i, file_dir + new_name)
    
    # Print any warnings
    if warnings != 0:
        print "\n\n\n---------"
        for i in warning_msgs:
            print i
            
def restore_filenames():
    original_names = open('original_filenames.txt')
    for i in os.listdir(file_dir):
        print i
        os.rename(file_dir + i,file_dir + original_names.readline().strip('\n'))
    original_names.close()

def create_orig(filename):
    '''Create a txt file with the original file names of files in a folder'''
    original_names = open(filename + '.txt','w')
    for i in os.listdir(file_dir):
        print i
        original_names.write(i+'\n')
    original_names.close()

def title_rename(file_dir, names_dict, index_start, rename=False):
    for episode in os.listdir(file_dir):
        # Dictionary key is SXXEXX
        dict_key = episode[index_start:index_start+6]
        # Likely not the best way to get the file extension
        ext = episode.split('.')[-1]
        original_name = episode
        new_name = names_dict[dict_key] + '.' + ext
        if rename is not False:
            os.rename(file_dir + original_name, file_dir + new_name)
        else:
            print new_name, original_name

def generate_name_dict(txt_file, index_start):
    names = open(txt_file)
    names_dict = {}

    for i in names:
        season_ep = i[index_start:index_start+6]
        names_dict[season_ep] = i.strip('\n')
        
    return names_dict

def parseHTML(url, names_txt, show_name):        
        
        episode_file = open(names_txt, 'w')
        site = urllib2.urlopen(url)
        soup = BeautifulSoup(site)
        
        x = soup.findAll("a", "bt")
        
        for i in x:
            episode = i.contents[0].split(':')
            if len(episode) >= 2:
                episode = episode[1]
                season_num = episode[:2]
                ep_num = episode[3:5]
                title = episode[8:]
                # Hack to fix an encoding error with a silly character.
                title = title.replace(u'\u2019', '\'')
                episode_file.write("%s.S%sE%s." % (show_name, season_num,ep_num) + title.replace(' ', '.') + '\n')
                
        episode_file.close()

# File directory of episodes. Including trailing slash
file_dir = '/media/1.5TB/TV Series/American Dad/Season 6/'
# Show name - Use dots for spaces
show_name = 'American.Dad'
# Season number in XX format
season_num = '06'
index_start = len(show_name) + 1
# text file with episode names in
names_txt = 'American_Dad.txt'
# TVRage printable website with episode names on. Must be this site! 
# Most shows are available by simply changing the show title directly in the url in the same format
episode_url = 'http://www.tvrage.com/American_Dad/printable'

## !! Run the following functions in the same order as listed !! ##

# parseHTML generates the required text file with the shows episode names in. Run this function first and check this file
# for values that aren't in the required format
#       show_name.SXXEXX.title
#~ parseHTML(episode_url, names_txt, show_name)

# Generate dictionary with episode names
names_dict = generate_name_dict(names_txt, index_start)

# simple_rename renames every episode in a folder to the simple format of 
# show_name.SXXEXX.ext
# rename=False provides a trial run to check output. Change to rename=True and run again when happy
simple_rename(file_dir, show_name, season_num, rename=True)

#!! The following function requires simple_rename to have been run first !!
# title_rename renames every episode in a folder to the names specified in the names dictionary
# rename=False provides a trial run to check output by only print the results. Change to =True when happy
title_rename(file_dir, names_dict, index_start, rename=True)
