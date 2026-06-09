#!/usr/bin/env python3

"""
Developed by CIDGOH group to transfer a file or directory from one endpoint to another as an asynchronous task.

Updated for Globus CLI v4+ and pip-based virtual environments (no conda required).

If you have any issue, please contact: 
wwhsiao@sfu.ca, duanjun1981@gmai.com

"""

import sys
import os
import os.path
import configparser
import inspect
import argparse
from shutil import which
from subprocess import run
import re

version = '0.3'

def print_logo():
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
    print("CIGOH cc_data_manager version:" + version + "\n")
    print("""
Developed by CIDGOH (https://cidgoh.ca/) to transfer a file or directory from one endpoint to another as an asynchronous task.

If you have any issue, please contact:

wwhsiao@sfu.ca or duanjun1981@gmai.com
        """)

def parse():
    parser = argparse.ArgumentParser(description='Data transfer through Globus')
    parser.add_argument('-i', '--input_dir', type=str, default=None,
                        help='The directory you want to copy from on your local endpoint')
    parser.add_argument('-o', '--output_dir', type=str, default=None,
                        help='The directory you want to copy to on the remote endpoint')
    parser.add_argument('-l', '--local_endpoint', type=str, default=None,
                        help='The local endpoint you want to copy data from (Optional. It will detect local endpoint automatically!)')
    parser.add_argument('-r', '--remote_endpoint', type=str, default=None,
                        help='The remote endpoint you want to copy data to')
    parser.add_argument('-u', '--user_id', type=str, default=None,
                        help='Emails for users that you want to grant access to (default read only)')
    parser.add_argument('-g', '--group_uuid', type=str, default=None,
                        help='Group UUID that you want to grant read access (default read only)')
    parser.add_argument('-d', '--delete', default=False, action='store_true',
                        help='Delete destination folder on remote endpoint before transfer')
    parser.add_argument('-s', '--sync_level', default="checksum",
                        help='Sync options: [exists|size|mtime|checksum(default)]')
    return parser

def get_globus_cmd():
    """Return the path to the globus command (from PATH or virtual environment)."""
    # First, try to find 'globus' in the same directory as this script (for bundled venv)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_globus = os.path.join(script_dir, 'globus_venv', 'bin', 'globus')
    if os.path.exists(venv_globus):
        return venv_globus
    # Then check system PATH
    globus_path = which('globus')
    if globus_path:
        return globus_path
    sys.exit("Error: 'globus' command not found. Please activate your virtual environment or install globus-cli.")

if __name__ == '__main__':
    print_logo()
    args = parse().parse_args()

    # Locate config.ini in the same directory
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    script_path = os.path.dirname(os.path.abspath(filename))
    config = configparser.ConfigParser()
    config.read(os.path.join(script_path, 'config.ini'))

    globus_cmd = get_globus_cmd()

    # Parse email list from config and command line
    email_list_all = []
    if config['DEFAULT'].get('USERS'):
        email_list_config = re.split(';|,', config['DEFAULT']['USERS'])
        email_list_all.extend(email_list_config)
    if args.user_id:
        email_list_input = re.split(';|,', args.user_id)
        email_list_all.extend(email_list_input)

    # Parse group list
    group_list_all = []
    if config['DEFAULT'].get('GROUPS'):
        group_list_config = re.split(';|,', config['DEFAULT']['GROUPS'])
        group_list_all.extend(group_list_config)
    if args.group_uuid:
        group_list_input = re.split(';|,', args.group_uuid)
        group_list_all.extend(group_list_input)

    # Get local endpoint ID (auto-detect if not provided)
    p0 = run([globus_cmd, 'endpoint', 'local-id'], capture_output=True, text=True)
    if p0.returncode != 0:
        print("\n")
        sys.exit("--- Please check if your local Globus Connect Personal has been set up (and run 'globus login').")
    else:
        local_endpoint = args.local_endpoint if args.local_endpoint else p0.stdout.strip()

    remote_endpoint = args.remote_endpoint if args.remote_endpoint else config['DEFAULT']['DES_ENDPOINT']

    if len(local_endpoint) < 1 or len(remote_endpoint) < 1:
        parse().print_help()
        sys.exit("--- Please provide both local and remote endpoints (via config or command line)!")

    if args.input_dir:
        if os.path.exists(args.input_dir):
            local_dir = os.path.abspath(args.input_dir)
        else:
            print("\n")
            sys.exit("--- Local directory not found. Please check the path!")
    else:
        parse().print_help()
        print("\n")
        sys.exit("--- Please provide a local directory to transfer!")

    if args.output_dir is None:
        parse().print_help()
        print("\n")
        sys.exit("--- Please provide a remote destination folder!")

    print('-'*75 + "\n")
    print("{: >30} {: <40}".format("local endpoint:", local_endpoint))
    print("{: >30} {: <40}".format("local directory:", local_dir))
    print("{: >30} {: <40}".format("remote endpoint:", remote_endpoint))
    print("{: >30} {: <40}".format("remote directory:", args.output_dir))

    # Build Globus paths
    local_path = f"{local_endpoint}:{local_dir}"
    # FIX: Ensure remote directory path ends with '/' (required for permission creation)
    remote_path = f"{remote_endpoint}:/~/{args.output_dir.rstrip('/') + '/'}"

    # --- Delete remote directory if requested ---
    if args.delete:
        print(f"\nDeleting existing remote directory: {remote_path}")
        del_proc = run([globus_cmd, 'rm', '--recursive', remote_path], capture_output=True, text=True)
        if del_proc.returncode == 0:
            print("Remote directory removed successfully.")
        else:
            err_msg = del_proc.stderr
            if "No such file or directory" not in err_msg and "not found" not in err_msg:
                print(f"Warning: could not delete remote directory: {err_msg}")

    # --- Check local endpoint connectivity ---
    print("\nChecking local endpoint...")
    p1 = run([globus_cmd, 'ls', local_endpoint], capture_output=True, text=True)
    if p1.returncode != 0:
        print("\n")
        sys.exit("--- Local endpoint is not connected. Please start Globus Connect Personal and run 'globus login'.")
    else:
        print("Local endpoint is ready.")

    # --- Check/create remote directory ---
    print(f"\nChecking remote path: {remote_path}")
    p2 = run([globus_cmd, 'ls', remote_path], capture_output=True, text=True)
    if p2.returncode != 0:
        err = p2.stderr
        if "not found" in err or "No such file" in err:
            print("Remote folder not found. Creating it now...")
            p3 = run([globus_cmd, 'mkdir', remote_path], capture_output=True, text=True)
            if p3.returncode == 0:
                print("Directory created successfully.")
            else:
                print(f"Failed to create directory: {p3.stderr}")
                sys.exit(1)
        else:
            print(f"Unexpected error checking remote path: {err}")
            sys.exit(1)
    else:
        print("Remote path exists and is accessible.")

    # --- Submit transfer task ---
    print("\nSubmitting transfer task...")
    p4 = run([globus_cmd, 'transfer',
              '--notify', 'failed,succeeded',
              '--recursive',
              '--sync-level', args.sync_level,
              local_path, remote_path], capture_output=True, text=True)
    if p4.returncode != 0:
        print("\n")
        sys.exit(f"Globus transfer submission failed:\n{p4.stderr}")
    else:
        print(p4.stdout)

    # --- Grant user permissions (read-only) ---
    for email in email_list_all:
        if not email.strip():
            continue
        print(f"\nGranting user {email} read access to the remote directory...")
        p5 = run([globus_cmd, 'endpoint', 'permission', 'create',
                  '--identity', email,
                  '--permissions', 'r',
                  remote_path], capture_output=True, text=True)
        if p5.returncode == 0:
            print(f"Read permission granted to {email}.")
        else:
            err = p5.stderr
            if "already shared" in err or "already exists" in err:
                print(f"Permission already exists for {email}, ignoring.")
            else:
                print(f"Failed to grant permission to {email}: {err}")

    # --- Grant group permissions ---
    for group in group_list_all:
        if not group.strip():
            continue
        print(f"\nGranting group {group} read access...")
        p6 = run([globus_cmd, 'endpoint', 'permission', 'create',
                  '--group', group,
                  '--permissions', 'r',
                  remote_path], capture_output=True, text=True)
        if p6.returncode == 0:
            print(f"Read permission granted to group {group}.")
        else:
            err = p6.stderr
            if "already shared" in err:
                print(f"Group permission already exists for {group}, ignoring.")
            else:
                print(f"Failed to grant group permission: {err}")

    print("\nAll done. Transfer task is running asynchronously. Check Globus web interface for progress.")