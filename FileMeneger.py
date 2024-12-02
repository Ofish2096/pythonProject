import chardet

from myLogger import write_error_line, write_info_line
import os

class style:
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    RESET = '\033[0m'


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)  # Read the first 10,000 bytes for encoding detection
        result = chardet.detect(raw_data)
        return result['encoding']



def read_line_from_file(file_path, line_number):
    try:

        # Get the current working directory
        current_directory = os.getcwd()

        write_info_line(f"Current directory: {current_directory}")
        full_path = os.path.join(current_directory, file_path)
        write_info_line(f"Current directory: {full_path}")

        line = "🍕"
        encoding = detect_encoding(full_path)




        write_info_line(f"try open {full_path}")
        with open(full_path, 'r', encoding=encoding) as file:
            lines = enumerate(file, start=1)
            for current_line_number,line in lines: # line in enumerate(file, start=1):
                if current_line_number == line_number:
                    # print(f"line.strip() {line.strip()}")
                    line = line.strip()
                    break
            if  line == "🍕":
                write_error_line(f"Error: Line number {line_number} is out of range.")
    except FileNotFoundError:
        write_error_line(f"Error: The file {file_path} does not exist.")
    except Exception as e:
        write_error_line(f"An error occurred:\n {e}")
    return line