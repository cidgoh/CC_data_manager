# Compute Canada data manager


usage: python3 ./cc_data_manager.sh -i input_folder -o remote_folder -u email_address -r remote_endpoint

Tips: You can also input recipient emails and remote endpoint ID in the config.ini file. 
  

```

CIGOH cc_data_manager version:0.2


Developped by CIDGOH (https://cidgoh.ca/) to transfer a file or directory from one endpoint to another as an asynchronous task.

If you have any issue, please contact:

wwhsiao@sfu.ca or duanjun1981@gmai.com

usage: cc_data_manager.py [-h] [-i INPUT_DIR] [-o OUTPUT_DIR] [-l LOCAL_ENDPOINT] [-r REMOTE_ENDPOINT] [-u USER_ID] [-g GROUP_UUID] [-d] [-s SYNC_LEVEL]

Data transfer through Globus

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        The directory you want to copy from on your local endpoint
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        The directory you want to copy to on the remote endpoint
  -l LOCAL_ENDPOINT, --local_endpoint LOCAL_ENDPOINT
                        The local endpoint you want to copy data from (Optional. It will detect local endpoint automatically!).
  -r REMOTE_ENDPOINT, --remote_endpoint REMOTE_ENDPOINT
                        The remote endpoint you want to copy data to
  -u USER_ID, --user_id USER_ID
                        Emails for users that you want to grant access to (default read only)
  -g GROUP_UUID, --group_uuid GROUP_UUID
                        Group UUID that you want to grant read access (default read only)
  -d, --delete          Delete destination folder if it already exists
  -s SYNC_LEVEL, --sync_level SYNC_LEVEL
                        Sync options: [exists|size|mtime|checksum(default)]

```
