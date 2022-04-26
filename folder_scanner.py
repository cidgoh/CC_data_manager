#!/usr/bin/env python3

"""
Developed by CIDGOH group to check folder sizes and file numbers

If you have any issue, please contact: 
wwhsiao@sfu.ca, duanjun1981@gmai.com

"""

import os
import re
from subprocess import run
import argparse
import sys

version = '0.1'

def print_logo():
    """
    print out the logo and version information
    """
    os.system("clear")
    print("\n")
    print("""
░█████╗░██╗██████╗░░██████╗░░█████╗░██╗░░██╗
██╔══██╗██║██╔══██╗██╔════╝░██╔══██╗██║░░██║
██║░░╚═╝██║██║░░██║██║░░██╗░██║░░██║███████║
██║░░██╗██║██║░░██║██║░░╚██╗██║░░██║██╔══██║
╚█████╔╝██║██████╔╝╚██████╔╝╚█████╔╝██║░░██║
░╚════╝░╚═╝╚═════╝░░╚═════╝░░╚════╝░╚═╝░░╚═╝
    """)
    print("CIGOH cc_data_manager version:"+ version +"\n")
    print("""
Developed by CIDGOH (https://cidgoh.ca/) to check folder sizes and file numbers in order to avoid reaching inodes limit.

If you have any issue, please contact:

wwhsiao@sfu.ca or duanjun1981@gmai.com
        """)
    print("#"*100+"\n")

def parse():
    parser = argparse.ArgumentParser(description='Data transfer through Globus')
    parser.add_argument('-i', '--input', type=str, default=None, help='The path that you want to check')    
    parser.add_argument('-d', '--depth', type=int, default=2, help='The depth that you want to display for the path (default: 2)')
    parser.add_argument('-n', '--file_number', type=int, default=10, help='Threshold for the number of size numbers (default: 10)')
    parser.add_argument('-s', '--folder_size', type=int, default=0, help='Threshold for folder size (default: any folder (size >０))')
    return parser

path = "/hdd/test_transfer"

def return_folder_size(path):
    process = run(['du', '-sh', path], capture_output=True, text=True)
    size = process.stdout.split()[0]
    sizeRegex = re.compile(r'(\d+)([K|M|G])')
    matches = sizeRegex.search(size)
    size_num = matches[1]
    if(matches[2] == "K"):
        size_num = int(size_num)/1000000
    elif(matches[2] == "M"):
        size_num = int(size_num)/1000
    elif(matches[2] == "G"):
        size_num = int(size_num)
    else:
        sys.exit("There might be some issue with file size: "+path+' ('+str(size)+')')
    size_num = "{:.4f}".format(size_num)
    return size_num

def return_file_number(path):
    #return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
    totalFiles = 0
    for base, dirs, files in os.walk(path):
        for Files in files:
            totalFiles += 1
    return totalFiles

if __name__ == '__main__':
    print_logo()
    args = parse().parse_args()
    if args.input is None:
        print("no input")
        parse().print_help()
        sys.exit("Please provide with a path that you want to check!")
    path = args.input
    cutoff_depth = args.depth
    cutoff_file_number = args.file_number
    cutoff_folder_size = args.folder_size


    for dirpath, dirnames, filenames in os.walk(path):
        directory_level = dirpath.replace(path, "")
        directory_level = directory_level.count(os.sep)
        if(directory_level <= cutoff_depth):
            indent = " " * 4
            file_number = return_file_number(dirpath)
            if(file_number >= cutoff_file_number):
                folder_size = return_folder_size(dirpath)
                if(float(folder_size) > cutoff_folder_size):
                    print("{}{}/\t{}\t{}".format(indent*directory_level, os.path.basename(dirpath), folder_size +' GB', file_number))
