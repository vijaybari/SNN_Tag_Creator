# Summary:
# This script manages the creation and copying of folders within a Subversion (SVN) repository based on XML configurations.
# It allows the user to select a configuration, parses the associated XML file, creates a tag in SVN, 
# and copies the specified folders to that tag.

# Imports:
import os
import xml.etree.ElementTree as ET
import subprocess
import sys

# Directory setup
CURRENT_DIR = os.getcwd()
XML_BASE_DIR = os.path.join(CURRENT_DIR, 'input_xml_files')

# Define options and corresponding input XML files
bm_options = {
    1: "01_BEV_SP21_7k4W.xml",
    2: "02_BEV_SP21_22kW.xml"
}

# Section: User Input
def get_user_selection():
    """Prompt user to select a BM line and return the corresponding XML file name."""
    print("Select a BM line:")
    for option, name in bm_options.items():
        print(f"{option}. {name.replace('.xml', '')}")
    
    selection = int(input("\nEnter your choice: "))
    if selection in bm_options:
        return bm_options[selection]
    else:
        print("Invalid choice. Exiting.")
        exit()

# Section: XML Parsing
def parse_xml_config(file_name):
    """Parse the specified XML file to extract configuration details."""
    tree = ET.parse(file_name)
    root = tree.getroot()

    root_tag = root.find('root_tag').attrib['name']
    root_svn_path = root.find('root_svn_path').text
    source_url = root.find('root_source').attrib['svn_path']
    
    # Collect BM folders and their revisions
    bm_folders = []
    for folder in root.findall('.//BM/folder'):
        name = folder.attrib['name']
        revision = folder.attrib['revision']
        bm_folders.append((name, revision))

    return root_tag, root_svn_path, source_url, bm_folders

# Section: SVN Folder Creation
def create_svn_folder(tag_url):
    """Create a new folder in SVN using the provided tag URL."""
    try:
        command = ['svn', 'mkdir', tag_url, '-m', f"Creating BM-tag at {tag_url}"]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully created BM-tag folder:\n{tag_url}\n")
    
    except subprocess.CalledProcessError as e:
        print(f"SVN Error: {e.stderr.decode()}")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

# Section: SVN Copy
def svn_copy(source_url, destination_url, revision, commit_message):
    """Copy a folder in SVN from source to destination using the specified revision."""
    try:
        command = [
            'svn', 'cp',
            f'{source_url}@{revision}',  # Source URL with specified revision
            destination_url,              # Destination URL
            '-m', commit_message           # Commit message
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f"Successfully copied from {source_url}@{revision} to {destination_url}")
            print(result.stdout)
        else:
            print(f"Failed to copy from {source_url}@{revision} to {destination_url}")
            print(result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

# Section: Main Function
def main():
    while True:
        try:
            # Get user selection and construct the XML file path
            xml_file_path = os.path.join(XML_BASE_DIR, get_user_selection())

            if os.path.exists(xml_file_path):
                print(f"Selected input XML file:\n{xml_file_path}\n")
                break
            else:
                print(f"\033[91mError: The file '{xml_file_path}' was not found. Please check if the file exists.\033[0m")
        except ValueError:
            print(f"\033[91mInvalid input: Please enter a number between 1 and {len(bm_options)}.\033[0m")

    # Parse the XML configuration
    root_tag, root_svn_path, source_url, bm_folders = parse_xml_config(xml_file_path)

    # Create the TAG folder URL
    tag_url = f'{root_svn_path}/{root_tag}'
    create_svn_folder(tag_url)  # Attempt to create the SVN folder (BM-TAG)

    # Copy BM folders from source to target
    for folder_name, revision in bm_folders:
        commit_message = f'Copying BM "{folder_name}" from revision "{revision}" to Tag "{root_tag}".'
        destination_url = f'{root_svn_path}/{root_tag}/{folder_name}'

        # Specify log file path and ensure directory exists
        log_file_path = os.path.join(XML_BASE_DIR, 'BM_log')
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        # Log the copying action
        with open(log_file_path, 'a') as log_file:
            folder_parts = folder_name.split('_', 2)
            part_of_folder_name = folder_parts[-1] if len(folder_parts) == 3 else folder_name
            log_entry = f'{part_of_folder_name} : {destination_url}\n'
            log_file.write(log_entry)

        # Execute the SVN copy command
        svn_copy(source_url, destination_url, revision, commit_message)
    
    with open(log_file_path, 'a') as log_file:
        log_entry = f'\n'
        log_file.write(log_entry)

    print(f"BM Tag Creation Successful:\n{tag_url}\n")
    
if __name__ == "__main__":
    main()