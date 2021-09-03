import os
import re


def get_future_s3_filename(filename, bucket_objects):
    """
    Allows us to get the filename to use when we upload the object in S3
    e.g if filename='temp.txt' does not exist in bucket_objects, we return temp.txt;
    if temp.txt exists but temp-(\d?).txt does not, we return temp-1.txt;
    if temp.txt and temp-1.txt exists but no other temp-(\d?).txt files exist,
    we return temp-2.txt; we do the same for temp-3.txt, temp-100.txt ...
    """
    already_exists = filename in bucket_objects
    if already_exists:
        name_without_ext, file_extension = os.path.splitext(filename)
        reg_exp = rf"{name_without_ext}-(\d+){file_extension}"
        matches = re.search(reg_exp, str(bucket_objects))
        if matches is None:
            return f"{name_without_ext}-1{file_extension}"
        else:
            next_number = int(matches.group(1)) + 1
            return f"{name_without_ext}-{next_number}{file_extension}"
    else:
        return filename
