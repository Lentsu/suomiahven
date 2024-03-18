#!/usr/bin/env python3

# Required by the script
import subprocess
import sys

# Local imports
import main

# Function to get required dependencies using pip
def install_deps():
    subprocess.check_call([sys.executable, "-r", "pip3", "install", "requirements.txt"])

# If this script was called directly
if __name__ == "__main__":
    install_deps() # Install the required dependencies
    main()         # Run the main function 
    
