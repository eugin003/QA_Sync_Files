"""

REPLICA will be modified to match SOURCE, changes in SOURCE will reflect on REPLICA but not vice-versa
A scheduled interval for synchronization will be used
Logging every file creation, modification or deletion (to log_file and console)
Command Line Arguments that are accepted:
--source      ->  Path to the source folder
--replica     ->  Path to replica folder
--interval    ->  Interval between synchronization operations (in seconds)
--log         ->  Path to log file

Check if source and replica folder exists
Traverse the source directory recursively:
    If file exists in source but not in replica, copy it to replica
    If file exist in both, compare their contents (file hashes)
    If file deleted from source, delete it from replica
Log each operation to both log file and console


"""

import os                           #For directory and file operations
import shutil                       #For copying and removing files
import time
import hashlib                      #For calculation MD5 file hashes
import argparse                     #For command line argument parsing
from datetime import datetime       #For setting up periodic synchronization


def calculate_md5(file_path):  #Calculate MD5 hash of file_path
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for c in iter(lambda: f.read(4096), b""):
            hash_md5.update(c)
    return hash_md5.hexdigest()

def log_op(log_file, message):  #Log the operation to the log file and console
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - {message}"
    print(log_message)
    with open(log_file, 'a') as log:
        log.write(log_message + '\n')

def sync_folders(src, replica,log_file):  #Synchronize source folder with replica folder 
    for dirpath, dirnames, filenames in os.walk(src):
        rel_path = os.path.relpath(dirpath, src)
        replica_dir = os.path.join(replica, rel_path)

        if not os.path.exists(replica_dir):
            os.makedirs(replica_dir)
            log_op(log_file, f"Directory created: {replica_dir}")

        for filename in filenames:
            source_file = os.path.join(dirpath, filename)
            replica_file = os.path.join(replica_dir, filename)

            if not os.path.exists(replica_file):
                # Copy new files from source to replica
                shutil.copy2(source_file, replica_file)
                log_op(log_file, f"File copied: {source_file} -> {replica_file}")
            else:
                # Check if file contents are different using MD5 hash
                if calculate_md5(source_file) != calculate_md5(replica_file):
                    shutil.copy2(source_file, replica_file)
                    log_op(log_file, f"File updated: {source_file} -> {replica_file}")

    # Walk through the replica directory to find and remove extra files and directories
    for dirpath, dirnames, filenames in os.walk(replica):
        # Construct relative path
        rel_path = os.path.relpath(dirpath, replica)
        source_dir = os.path.join(src, rel_path)

        # Remove directories that exist in replica but not in source
        for dirname in dirnames:
            replica_subdir = os.path.join(dirpath, dirname)
            source_subdir = os.path.join(source_dir, dirname)
            if not os.path.exists(source_subdir):
                shutil.rmtree(replica_subdir)
                log_op(log_file, f"Directory removed: {replica_subdir}")

        # Remove files that exist in replica but not in source
        for filename in filenames:
            replica_file = os.path.join(dirpath, filename)
            source_file = os.path.join(source_dir, filename)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                log_op(log_file, f"File removed: {replica_file}")    


"""

WHILE TRUE - The program will keep running always updating/checking both folders in intervals of --interval seconds

"""
def main():
    #Parse command line arguments
    parser = argparse.ArgumentParser(description="Folder Synchronization Script")
    parser.add_argument('--source', required=True)
    parser.add_argument('--replica', required=True)
    parser.add_argument('--interval', type=int, required=True)
    parser.add_argument('--log', required=True)
    args = parser.parse_args()

    source = args.source
    replica = args.replica
    interval = args.interval
    log_file = args.log

    #Check if source directory exists
    if not os.path.exists(source):
        print(f"Error: Source folder '{source}' does not exist.")
        return

    #Check if replica directory exists
    if not os.path.exists(replica):
        os.makedirs(replica)
        log_op(log_file, f"Replica folder created: {replica}")

    #Perform periodic synchronization
    while True:
        sync_folders(source, replica, log_file)
        time.sleep(interval)

if __name__ == '__main__':
    main()

