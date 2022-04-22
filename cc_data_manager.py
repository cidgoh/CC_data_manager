#!/usr/bin/env python3

"""
Developed by CIDGOH group to transfer a file or directory from one endpoint to another as an asynchronous task.

If you have any issue, please contact: 
wwhsiao@sfu.ca, duanjun1981@gmai.com

"""
import sys
import os
import os.path
import logging
import configparser
import inspect, os.path
import argparse
from shutil import which
from subprocess import run
import re

version = '0.2'

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
Developped by CIDGOH (https://cidgoh.ca/) to transfer a file or directory from one endpoint to another as an asynchronous task.

If you have any issue, please contact:

wwhsiao@sfu.ca or duanjun1981@gmai.com
        """)


def parse():
    parser = argparse.ArgumentParser(description='Data transfer through Globus')
    parser.add_argument('-i', '--input_dir', type=str, default=None, help='The directory you want to copy from on your local endpoint')    
    parser.add_argument('-o', '--output_dir', type=str, default=None, help='The directory you want to copy to on the remote endpoint')
    parser.add_argument('-l', '--local_endpoint', type=str, default=None,
                        help='The local endpoint you want to copy data from (Optional. It will detect local endpoint automatically!). ')
    parser.add_argument('-r', '--remote_endpoint', type=str, default=None,
                        help='The remote endpoint you want to copy data to')
    parser.add_argument('-u', '--user_id', type=str, default=None,
                        help='Emails for users that you want to grant access to (default read only)')
    parser.add_argument('-g', '--group_uuid', type=str, default=None,
                        help='Group UUID that you want to grant read access (default read only)')
    parser.add_argument('-d', '--delete', default=False, action='store_true', help='Delete destination folder if it already exists')
    parser.add_argument('-s', '--sync_level', default="checksum",help='Sync options: [exists|size|mtime|checksum(default)]')
    return parser

def check_tool(name):
    return which(name) is not None


if __name__ == '__main__':
    print_logo()
    args = parse().parse_args()
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path     = os.path.dirname(os.path.abspath(filename))
    config   = configparser.ConfigParser()
    config.read(path+'/config.ini')
    p2_exit_code = ""

    # parse email list
    email_list_all = email_list_config = email_list_input = []
    if(config['DEFAULT']['USERS']):
        email_list_config=re.split(';|,',config['DEFAULT']['USERS'])
    if(args.user_id):
        email_list_input=re.split(';|,',args.user_id)
    email_list_all = email_list_config + email_list_input
    email_all = ",".join(email_list_all)

    # parse group list
    group_list_all = group_list_config = group_list_input = []
    if(config['DEFAULT']['GROUPS']):
        group_list_config=re.split(';|,',config['DEFAULT']['GROUPS'])
    if(args.group_uuid):
        group_list_input=re.split(';|,',args.group_uuid)
    group_list_all = group_list_config + group_list_input
    group_all = ",".join(group_list_all)


    # get local endpoint id
    p0 = run(['conda', 'run', '-n','globus', 'globus', 'endpoint', 'local-id'],capture_output=True)
    if(p0.returncode!=0):
        print("\n")
        sys.exit("--- Please check your if your local Globus Connect Personal has been set up!") 
    else: 
        local_endpoint = args.local_endpoint and args.local_endpoint or p0.stdout.decode().strip() 
  
    
    remote_endpoint = args.remote_endpoint and args.remote_endpoint or config['DEFAULT']['DES_ENDPOINT']

    if(len(local_endpoint) < 1 or len(remote_endpoint) < 1):
        parse().print_help()
        sys.exit("--- Please add a local and a remote endpoint!")

    if(args.input_dir):
        if(os.path.exists(args.input_dir)):
            local_dir = os.path.abspath(args.input_dir)
        else:
            print("\n")
            sys.exit("--- Please check your if the path for your local directory is correct!") 
    else:
        parse().print_help()
        print("\n")
        sys.exit("--- Please provide a path for the local directory that you want to transfer!")  

    if(args.output_dir is None):
        parse().print_help()
        print("\n")
        sys.exit("--- Please provide a folder that you want to transfer on the remote endpoint!")  

    print('-'*75+"\n")
    print("{: >30} {: <40}".format("local endpoint:", local_endpoint))
    print("{: >30} {: <40}".format("local directory:", local_dir))
    print("{: >30} {: <40}".format("remote endpoint endpoint:", remote_endpoint))

  
    # checking local endpoint

    local_path = local_endpoint + ":"+local_dir
    remote_path = remote_endpoint+":/~/"+os.path.join(args.output_dir, '')

    print("Checking local endpoint")

    p1 = run(['conda', 'run', '-n','globus', 'globus', 'ls', local_endpoint], capture_output=True )
    p1_err_info = p1.stderr.decode()

    if(p1.returncode!=0):
        print("\n")
        sys.exit("--- Local endpoint is not currently connected to Globus. Please start it using $PATH/globusconnectpersonal -start&\n") 
    else: 
        print("Local endpoint is ready to use.")

    # checking remote endpoint

    print("Checking remote path: "+remote_path)

    if(not check_tool("globus")):  
        sys.exit("--- Please check if you have installed globus-cli!")

    p2 = run( [ 'conda', 'run', '-n','globus', 'globus', 'ls', remote_path], capture_output=True )
    p2_err_info = p2.stderr.decode()

    try:
        match = re.search(r'not found on endpoint', p2_err_info, re.DOTALL)
        if(match.group(0)):
            print("Remote folder is not found. Now trying to create one.")
            p2_exit_code = 'c1' # remote folder is not found
    except:
        print("Remote endpoint is ready to use.")        

    if(p2_exit_code == "c1"):
        p3 = run( [ 'conda', 'run', '-n','globus', 'globus', 'mkdir', remote_path], capture_output=True )
        if(p3.returncode) == 0:
            print("The directory was created successfully")
        if(p3.returncode) != 0:
            print( 'stderr:', p2.stderr.decode() )
            sys.exit()

    # start to transfer data
    p4 = run( [ 'conda', 'run', '-n','globus', 'globus', 'transfer', '--notify', 'failed,inactive,succeeded', '--recursive', '--sync-level', args.sync_level, local_path, remote_path], capture_output=True )
    if(p4.returncode!=0):
        print("\n")
        sys.exit("--- Globus transfer job is not submitted successfully. Please check the network or configuration!") 
    else: 
        print( 'stdout:', p4.stdout.decode() )


    # grant permission for users

    if(len(email_list_all) > 0):
        for tmp_email in email_list_all:            
            print("Granting user " + tmp_email + " read access to the remote directory")
            p5= run(['conda', 'run', '-n','globus', 'globus', 'endpoint', 'permission', 'create', '--provision-identity', tmp_email, '--permissions', 'r', remote_path, '--notify-email', tmp_email], capture_output=True )
            p5_err_info = p5.stderr.decode()

            try:
                match = re.search(r'This folder is already shared with this identity', p5_err_info, re.DOTALL)
                if(match.group(0)):
                    print("The remote folder is already shared with read permission to "+tmp_email+ ". Just ignore this granting permiision request!")                
            except:
                print("The read permission has been granted to "+tmp_email)     


    

    # grant permission for groups
    if(len(group_list_all) > 0):
        for tmp_group in group_list_all:  
            print("Granting group "+tmp_group + " read access to the destination directory")
            p6= run(['conda', 'run', '-n','globus', 'globus', 'endpoint', 'permission', 'create', '--group', tmp_group, '--permissions', 'r', remote_path], capture_output=True)
            p6_err_info = p6.stderr.decode()
            try:
                match = re.search(r'This folder is already shared with this identity', p6_err_info, re.DOTALL)
                if(match.group(0)):
                    print("The remote folder is already shared with read permission to "+tmp_group+ ". Just ignore this granting permiision request!")                
            except:
                print("The read permission has been granted to "+tmp_group)     


