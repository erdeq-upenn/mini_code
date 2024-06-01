"""
Usage:
------
python process_file.py myfile.txt -o processed_content.md

This will process myfile.txt with uppercase conversion 
and save the result as a Markdown file 
named processed_content.md
"""
import re
from IPython.display import Markdown
import argparse

def read_file(filename):
    with open(filename,encoding='utf-8') as f:
        data = f.read()
    f.close()
    return data

def extract_stress_parts(md_text):
    # Define the regex pattern to match stress parts with Chinese characters
    # pattern = r'\*\*([\w\s,\.，。—“”\u4e00-\u9fff]+)\*\*'
    pattern = r'\*\*(.*?)\*\**'
    
    # Find all matches
    matches = re.findall(pattern, md_text, re.UNICODE)
    matches = [i.strip() for i in matches]
    return matches

def show_main(file,output_file):
    """
    This function reads a file line by line, 
    distill it with ** ** 
    and writes the processed content to a new Markdown file.

    Args:
    -----
    filename: The path to the file to process.
    output_file: The path to the Markdown file where the processed content 
                    is saved (optional, defaults to None).
    """
    lines = read_file(file)
    lines = lines.replace('\u3000','')
    # Extract stress parts
    stress_parts = extract_stress_parts(lines)
    # Output the extracted stress parts
    print("There are %s main points"%len(stress_parts))
    md_bullet_points = "\n".join([f"- {item}" for item in stress_parts])
    if output_file:
        with open(output_file, 'w') as f:
            f.writelines(md_bullet_points)
    print(*md_bullet_points,sep='')
    return Markdown(md_bullet_points)
    

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process a file")

    # Add a required argument for the filename
    parser.add_argument('filename', type=argparse.FileType('r'),
                        help="The file to process")
    # Add an optional flag for converting to uppercase
    parser.add_argument('-o', '--output', type=str,
                        help="The filename (with .md extension) to save processed content (optional)")
    # Parse the arguments from the command line
    args = parser.parse_args()

    # Ensure output filename has .md extension
    if args.output and not args.output.endswith('.md'):
        args.output += '.md'  # Add .md extension if missing
    
    # Call the process_file function with the parsed arguments    
    show_main(args.filename.name,args.output)

if __name__ == '__main__':
    main()