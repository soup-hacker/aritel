import binascii, struct, argparse, os
from datetime import datetime, timedelta
from glob import glob

def make_parser():
    """
    Creates an object, adds the 'path' argument to it. Returns the created object.
    """
    
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-p', '--path', required=False, type=str, help='The path to the $I file you wish to parse. \
        Make sure you have access to the directory it is located in. Relative paths are allowed.')

    group.add_argument('-d', '--directory', required=False, type=str, help='A directory with $I files you want to parse.')

    args = parser.parse_args()

    return args

def get_file_size(data):
    """
    Extracts the file size from the provided $I file and returns it as a string.
    """
    
    file_size = data[16:32]
    
    size = binascii.unhexlify(file_size)
    
    return str(struct.unpack("<Q", size))[1:-2]

def get_deleted_time(data):
    """
    Extracts the deletion time from the $I file. Returns it as a string in human readable format.
    """
    
    deltime = data[32:48]
    
    filetime = struct.unpack("<Q", bytes.fromhex(deltime))[0]
    
    date_time = datetime(1601, 1, 1) + timedelta(microseconds=filetime / 10)
    
    return str(date_time)

def get_file_path(data):
    """
    Extracts the original path from the $I file and returns it as a string.
    """
    
    file_path = data[56:]
    
    bytes_string = bytes.fromhex(file_path)
    
    unicode_string = bytes_string.decode("utf-16")
    
    return str(unicode_string)

def get_file_name(old_path):
    """
    Takes in the orginal path and returns the orginal file name.
    """
    if '\\' in old_path:
        name = old_path.split('\\')
        return name[-1]
    else:
        return old_path

def get_source(path):
    """
    Takes in the entered path and returns the source file name.
    """
    if '\\' in path:
        source = path.split('\\')[-1]
        
        return source
    
    else:
        source = path
    
        return source

def main():
    """
    Takes in the path of the file as input, and returns the file size, deletion time, and the original path of the file.
    """
    
    args = make_parser()

# ===== Single File Parsing ===== #
    if args.path:    
        path = args.path

        if not os.path.isfile(path):
            print("\nInvalid Path => {}".format(path) + "\n")
            
            exit()
        
        source = get_source(path)
        if source.startswith("$I"):
            with open(path, 'rb') as file:
                data = file.read().hex()
                
                file_size = get_file_size(data)

                deltime = get_deleted_time(data)

                old_path = get_file_path(data)

                file_name = get_file_name(old_path)
                
                return print(f'''\nSource: {source}\nFile Name: {file_name}\nFile Size (bytes): {file_size}\nDeletion Time: {deltime}\nOrginal Path: {old_path}\n''')

# ===== Multi File Parsing ===== #
    elif args.directory:
        directory = args.directory

        if not os.path.isdir(directory):
            print("\nInvalid Path => {}".format(path) + "\n")
            
            exit()
                
        file_list = glob(directory + '\$I*')
        #print(file_list)
        for entry in file_list:
            with open(entry, 'rb') as file:
                data = file.read().hex()
                
                file_size = get_file_size(data)

                deltime = get_deleted_time(data)

                old_path = get_file_path(data)

                file_name = get_file_name(old_path)

                source = entry.split('\\')[-1]

                print(f'''\nSource: {source}\nFile Name: {file_name}\nFile Size (bytes): {file_size}\nDeletion Time: {deltime}\nOrginal Path: {old_path}\n''')

        return

    else:
        help_message = r"""
 ______     ______     __     ______   ______     __        
/\  __ \   /\  == \   /\ \   /\__  _\ /\  ___\   /\ \       
\ \  __ \  \ \  __<   \ \ \  \/_/\ \/ \ \  __\   \ \ \____  
 \ \_\ \_\  \ \_\ \_\  \ \_\    \ \_\  \ \_____\  \ \_____\ 
  \/_/\/_/   \/_/ /_/   \/_/     \/_/   \/_____/   \/_____/ 

A Windows $I Recyble Bin file parser, written in Python.

Paths may be absolute or relative just make sure your shell has access to the directory the file(s) is/are located in.

Example Usage:> python aritel.py -p <path-to-file>

Example Usage:> python aritel.py -d <path-to-directory>

Developed by Miles Campbell, 2023
Github: @soup-hacker
"""
        return print(help_message)

main()