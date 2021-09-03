# local-backup-to-s3
This tool allows you to backup files inside a specific folder to S3.

Files are first uploaded to a specific S3 bucket (given in an environment variable), then when the upload is done, the files are deleted. If one file already exists inside the bucket, a new name with a suffix is used so as not to overwrite the existing object.

Pipelines's progress and failures can be checked via the Dagit UI. When a pipeline fails, if gmail credentials have been given, you can opt to be alerted by activating the email_on_backup_s3_pipeline_failure sensor.


# Installation
You should create a virtual environment first. Clone the project, activate optionally the virtual environment and install the dependencies by going first into the `requirements` folder and then running the following commands:

`pip install common.txt`

`pip install production.txt`

If you want to run the tests, run this command also:

`pip install tests.txt`

Finally, inside the `backup_to_s3` folder, create an environment file(.env) with the following content:

    BACKUP_FOLDER=YOUR_BACKUP_FOLDER
    S3_BUCKET_NAME=YOUR_S3_BUCKET_NAME
    INTERVAL_CHECK_SECONDS=INTERVAL_TO_WAIT_BETWEEN_SENSORS_RUNS
    EMAIL_FROM=OPTIONAL_EMAIL_FROM
    EMAIL_PASSWORD=OPTIONAL_EMAIL_PASSWORD
    EMAIL_TO=OPTIONAL_EMAIL_TO`

If you define EMAIL_FROM and EMAIL_PASSWORD, make sure to use gmail credentials.

# Usage
Go inside the `backup_to_s3` folder and run the two following commands in parallel(the two instances have to be running at the same time):

    dagit -f repo.py
    dagster-daemon run

Go to `http://localhost:3000/instance/sensors` (replace 3000 with the dagit port if you have changed it) and activate `new_files_sensor` and optionally `email_on_backup_s3_pipeline_failure`. If there's one or more files inside the backup folder, they should get picked up soon and you can see the runs launched at `http://localhost:3000/instance/runs` .


# Licence
local-backup-to-s3 is licensed under the MIT license.
