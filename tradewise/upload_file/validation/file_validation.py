# import logging


def validate_file(file):
    file_name = file.name.lower()
    file_size = len(file.read())

    valid_extentions = ['.csv', '.xlsx', '.html', '.htm']
    is_valid_extention = any(file_name.endswith(ext) for ext in valid_extentions)
    is_within_size_limit = (file_size <= 25 * 1024 * 1024)
    is_filename_within_limit = (len(file_name) <= 255)

    if not is_filename_within_limit:
        # logging.error('Filename exceeds the maximum limit of 255 characters.')
        return False, 'Filename exceeds the maximum limit of 255 characters.'
    elif not is_valid_extention:
        # logging.error('Invalid file type. Please upload a CSV, XLSX, HTML, or HTM file.')
        return False, 'Invalid file type. Please upload a CSV, XLSX, HTML, or HTM file.'
    elif not is_within_size_limit:
        # logging.error('File size exceeds the limit of 25 MB.')
        return False, 'File size exceeds the limit of 25 MB.'
    else:
        # logging.info('Valid file type, size, and filename length.')
        return True, 'Valid file type, size, and filename length.'
