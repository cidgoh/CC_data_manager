#!/usr/bin/env python3

"""
Developed by CIDGOH group to backup data.

If you have any issue, please contact:
wwhsiao@sfu.ca, duanjun1981@gmai.com

"""

import argparse
import os
from datetime import date
from pathlib import Path
import sys
import subprocess
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract fasta sequences using a list of sequence IDs.')
    parser.add_argument('-i', '--input', type=str, default=None,
                        help='The directory that you want to backup')
    parser.add_argument('-o', '--output', type=str, default=None, help='The direcotry where you want to store backup file')
    return parser.parse_args()


def check_create_folder(dirname):
    if not os.path.exists(dirname):
        try:
            path = Path(dirname)
            path.mkdir(parents=True, exist_ok=True)
        except:
            print("make directory error, please check "+dirname)

if __name__ == '__main__':
    args = parse_args()
    input_dir = args.input 
    output_dir = args.output    
    today = date.today()
    data_stamp= today.strftime("%Y-%m-%d")
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%H-%M")
    output_dir=str(output_dir)+"/"+str(data_stamp)
    check_create_folder(output_dir)
    folder_name = os.path.basename(input_dir)
    gz_file = output_dir+"/"+folder_name+"_"+str(data_stamp)+"_"+timestampStr+".tar.gz"
    
    p = subprocess.run(["sudo","tar", "czvf",gz_file, input_dir],capture_output=True)
    if(p.returncode) == 0:
        print("The folder has been compressed and you can find it at "+gz_file)
    if(p.returncode) != 0:
        print( 'stderr:', p.stderr.decode() )
        sys.exit("There is some issue with compressing. Please check!")


