import os
import re
import shutil
import hashlib

def remove_duplicates(directory, method="filename"):
    print(f"Scanning for duplicates in '{directory}'...")
    filedict = {}

    if method == "filename":
        for root, _, files in os.walk(directory):
            for filename in files:
                basename, ext = os.path.splitext(filename)
                primary_name = f"{basename}{ext}"
                if primary_name not in filedict:
                    filedict[primary_name] = [filename]
                else:
                    filedict[primary_name].append(filename)

    elif method == "content":
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                with open(filepath, 'rb') as f:
                    filehash = hashlib.md5(f.read()).hexdigest()
                if filehash not in filedict:
                    filedict[filehash] = [filepath]
                else:
                    filedict[filehash].append(filepath)

    elif method == "combined":
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                basename, ext = os.path.splitext(filename)
                primary_name = f"{basename}{ext}"
                with open(filepath, 'rb') as f:
                    filehash = hashlib.md5(f.read()).hexdigest()
                combined_key = f"{primary_name}_{filehash}"
                if combined_key not in filedict:
                    filedict[combined_key] = filepath
                else:
                    if get_user_confirmation(f"Delete duplicate '{filepath}'? (y/n): "):
                        os.remove(filepath)
                        print(f"Deleted duplicate file: {filepath}")

    else:
        print(f"Invalid method: {method}. Choose from 'filename', 'content', or 'combined'.")
def clean_temp_files(directories, extensions):
    print("Cleaning temporary files...")
    for directory in directories:
        expanded_dir = os.path.expandvars(directory)
        try:
            for dirpath, _, filenames in os.walk(expanded_dir):
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in extensions):
                        filepath = os.path.join(dirpath, filename)
                        try:
                            os.remove(filepath)
                            print(f"Removed: {filepath}")
                        except PermissionError:
                            print(f"Permission denied: {filepath}, skipping...")
                        except FileNotFoundError:
                            print(f"File not found: {filepath}, skipping...")
                        except Exception as e:
                            print(f"Error deleting {filepath}: {e}")
        except FileNotFoundError:
            print(f"Directory not found: {expanded_dir}")

def clean_windows_temp_folder():
    print("Cleaning Windows Temp Folder...")
    temp_dirs = [os.environ.get('TEMP'), r'C:\Windows\Temp']
    for temp_dir in temp_dirs:
        try:
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(filepath) or os.path.islink(filepath):
                        os.remove(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                    print(f"Removed: {filepath}")
                except PermissionError:
                    print(f"Permission denied: {filepath}, skipping...")
                except FileNotFoundError:
                    print(f"File not found: {filepath}, skipping...")
                except Exception as e:
                    print(f"Failed to clean {filepath}: {e}")
        except Exception as e:
            print(f"Failed to clean directory {temp_dir}: {e}")
def organize_downloads(directory, categories):
    print(f"Organizing files in '{directory}'...")
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return
    # Create a mapping from extensions to category folders
    extension_to_category = {}
    for category, extensions in categories.items():
        for extension in extensions:
            extension_to_category[extension] = category
    # Process each file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            extension = os.path.splitext(filename)[1].lower()
            if extension in extension_to_category:
                category_dir = os.path.join(directory, extension_to_category[extension])
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir)
                shutil.move(filepath, os.path.join(category_dir, filename))
                print(f"Moved '{filename}' to '{category_dir}'")
            else:
                print(f"No category defined for extension '{extension}'. Skipping '{filename}'.")

def get_user_confirmation(message):
    response = input(f"{message} (y/N): ").lower()
    return response in ('y', 'yes')

def main():
    temp_directories = [r"C:\Windows\Temp", r'%TEMP%']
    extensions = ['.log', '.tmp', '.dmp', '.cache']
    categories = {
        "Image": [".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp", ".eps"],
        "Code": [".ipynb",".py", ".js", ".html", ".css", ".php", ".cpp", ".h", ".java"],
        "Document": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx"],
        "Audio": [".mp3", ".wav", ".aac", ".ogg"],
        "Video": [".mp4", ".avi", ".mov", ".flv", ".wmv", ".mpeg"],
        "Photoshop": [".psd"],
        'Archives': [".zip"] ,
        'Software' : [".exe" ,".msi" ],
    }
    remove_duplicates(os.path.expanduser("~/Downloads"), method="combined")
    clean_temp_files(temp_directories, extensions)
    organize_downloads(os.path.expanduser("~/Downloads"), categories)
    clean_windows_temp_folder()

    print("Cleanup completed.")

if __name__ == "__main__":
    main()
