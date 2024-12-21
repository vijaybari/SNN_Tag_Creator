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


if __name__ == "__main__":
    main()