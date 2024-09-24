"""Convert RIS to CSV."""

import sys, os
import csv
import re


def test_ris_file_exists(ris_path):
    """Test if an RIS file exists.

    Returns:
        True -- if file can be opened
        False -- if file cannot be opened

    """
    if ris_path.endswith(".ris"):
        try:
            open(ris_path, 'r', encoding = 'utf-8')
            return True
        except IOError:
            print("That path appears invalid. Please try again.\n")
            return False
    else:
        print("Please end your path with '.ris'\n")
        return False

def blank_row():
    """Create and return a blank, 80 item long list."""
    row = []
    for i in range(0, 81, 1):  # pylint: disable=W0612
        row.append(None)
    return row

def get_csv_path():
    print("""
    Please enter the relative or full path to the location you would like your 
    new csv saved, as well as the filename for the new csv file. 
    
    Eg. "~/Documents/ris_report.csv" (without the quotation marks)
          """)
    csv_path = input("> ")
    if csv_path.endswith(".csv"):
        return csv_path
    else:
        print("Please end your path designation with '.csv'.")
        csv_path = get_csv_path()
        return csv_path

def main(): # pylint: disable=R0914
    """Open RIS file, take data, convert to CSV using REGEX."""
    print("""
    Please enter the relative or full path to the RIS file you would 
    like to convert to a CSV file.
          """)
    ris_path = input("> ")

    if test_ris_file_exists(ris_path) is False:
        
        main()
        exit(0)

    csv_path = get_csv_path()
    
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        application_path = sys.executable
        application_path2 = sys._MEIPASS
        application_path = application_path.replace(".exe", "")
        application_path2 = application_path2.replace(".exe", "")
        try:
            print("here1")
            std_path = application_path.replace("ris_converter", 
                                                "RIS_stds.csv")
            ris_std = open(std_path, 'r', encoding = 'utf-8')
        except:
            print("here2")
            std_path = application_path2 + "/RIS_stds.csv"
            ris_std = open(std_path, 'r', encoding = 'utf-8')
    else:
        print("here3")
        application_path = os.path.dirname(os.path.abspath(__file__))
        std_path = application_path + "/RIS_stds.csv"
        ris_std = open(std_path, 'r', encoding = 'utf-8')

    
    csv_file = open(csv_path, 'w', newline='', encoding = 'utf-8')  
    # ^ 'newline=""' is required to not print a space after each row in 
    # windows. 
    writer = csv.writer(csv_file, dialect='excel')
    column_num = {}
    row = blank_row()
    for i, line in enumerate(ris_std):
        line_token_list = line.split(",")
        column_num[line_token_list[0]] = int(line_token_list[2]) - 1
        row[i] = "{0} ({1})".format(line_token_list[1], line_token_list[0])
    ris_std.close()
    writer.writerow(row)
    row = blank_row()


    ris_file = open(ris_path, 'r', encoding = 'utf-8')
    ris_text = ris_file.read()
    ris_text = ris_text.replace("\n", " ")
    ris_file.close()
    regex = re.compile(
        r'(?<=([A-Z][A-Z0-9]  - ))(.*?)(?=([A-Z][A-Z0-9]  - ))')
    # ^ This uses a "positive lookbehind" [(?<=...)] to start the match after
    # '...', then uses a non-greedy (?) wildcard to iteratively move forward
    # until BEFORE the final matched expression , which is done with a
    # positive lookahead [(?=...)]
    matches = re.findall(regex, ris_text)  # Create a list with .findall()
    print("Here are all the matches for your regex: ")
    for match in matches:
        ris_id = match[0][0] + match[0][1]
        ris_data = match[1]
        try:
            row[column_num[ris_id]] = ris_data
        except KeyError:
            print(f"Warning: Unrecognized RIS tag '{ris_id}' found and skipped.")
            
        print("""
        ris_id = {0}
        ris_data = {1}
              """.format(ris_id, ris_data))
        if ris_id == "AU":
            row_au_values.append(ris_data) # Append "AU" value to the list
        elif ris_id == "ER":
            # Assign the "AU" values to the "Author" column
            row[column_num["AU"]] = ', '.join(row_au_values)
            writer.writerow(row)
            row = blank_row()
            row_au_values = [] # Reset the "AU" values list for the next row
        else:
            row[column_num[ris_id]] = ris_data
    csv_file.close()
    print("""
    Conversion process complete. 
    
    Your new file is located here: {0}
    
    """.format(os.path.abspath(csv_path)))

    return


if __name__ == "__main__":
    print("Welcome to the RIS>CSV Converter.")
    try:
        main()
    except:
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
    finally:
        print("Press <return> or <enter> to close the program.")
        input()
