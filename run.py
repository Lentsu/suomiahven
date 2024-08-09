#!/usr/bin/env python3
import os

# Required by the script
import subprocess
import sys

# Function to get required dependencies using pip
def install_deps():
    subprocess.call(["pip3", "install", "-r", "requirements.txt"])

# If this script was called directly
if __name__ == "__main__":
    # Install the required dependencies
    install_deps()
    
    # Import the main file
    import main
    
    #Run the main function
    main.main()

