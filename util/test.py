import os

def print_directory_contents(path, prefix=''):
    """
    This function takes the name of a directory
    and prints out its directory tree structure
    with proper indentation.
    """
    # Print the current directory
    print(f"{prefix}├── {os.path.basename(path)}/")
    
    # Increase the indentation for sub-directories
    prefix = prefix + "│   "
    
    # Get the contents of the directory
    contents = os.listdir(path)
    
    # Sort directories first, then files
    contents.sort(key=lambda x: not os.path.isdir(os.path.join(path, x)))
    
    # Recursively print the contents of sub-directories
    for item in contents:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            print_directory_contents(item_path, prefix)
        else:
            print(f"{prefix}├── {item}")

# Call the function with the path to the directory you want to print
print_directory_contents('.')

