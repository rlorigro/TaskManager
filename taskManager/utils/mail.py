from email.mime.base import MIMEBase
from email import encoders
import os


def parse_paths_as_list(arg):
    """
    Allow singular path string or list of path strings
    :param arg: This could be a string... or it could be a list of strings! Who knows what could happen?
    :return: List of strings
    """
    invalid_argument = False

    if type(arg) is str:
        arg = [arg]

    elif type(arg) is list:
        for item in arg:
            if type(item) is not str:
                invalid_argument = True

    else:
        invalid_argument = True

    if invalid_argument:
        exit("ERROR: invalid attachment argument. Must be string or list of strings, but found: %s" % str(arg))

    return arg


def encode_attachment(attachment_path):
    # Open the file to be sent
    filename = os.path.basename(attachment_path)
    attachment_file = open(attachment_path, "rb")

    attachment = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    attachment.set_payload(attachment_file.read())

    # Encode into base64
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # Close file
    attachment_file.close()

    return attachment
