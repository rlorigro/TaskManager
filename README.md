[![Build Status](https://travis-ci.com/rlorigro/TaskManager.svg?branch=master)](https://github.com/rlorigro/TaskManager)

# TaskManager
Monitors resources and sends notifications. Uses AWS SES to send emails (if valid credentials exist under ~/.aws). Locally, can also send email via SMTP or gmail.

### Automated Reports

By wrapping your commands with taskmanager, you can automatically notify youself when the job finishes via email. User specified recipients are sent an email which looks like the following:

```
Process with the following arguments:
        samtools view -h GM24385.wtdbg2.bam
on instance i-0e4c60e37ccc2c13b has concluded after 67.20 minutes.
```
If you decided to monitor the compute resources a graph of your resource usage will be attached to the email.

You can plot log files to generate the same image using `plot_resource_usage.py`:

![plot of log file](https://github.com/rlorigro/TaskManager/raw/master/log_2019_2_11_17_33_19_458174.png)

## Requirements
python3:
  - psutil
  - boto3 (for AWS compatibility)
 
### Compatibility
- ubuntu 18
- osx

## Email notifier usage

To use on AWS, you must first have your `~/.aws` credentials configured. The easiest way to do this is to run `aws configure` on your instance. If you haven't already verified your email in the AWS SES console then you also need to go find your email address in the SES email list and click "verify".

#### Recommended Usage:
Install via pip   

```pip install taskManager```

Configure setup

```taskManager configure```

You will be prompted to configure taskManager  
* Set your sender email  
`Sender Email[None]: someEmail@gmail.com` 
* Set the recipient email  
`Recipient Email:[None]:someEmail2@gmail.com` 
* Optionally get promted to add more recipient emails  
`Add more emails? [y/n] n`
* If an aws server, you need to register an email with [SES](https://aws.amazon.com/ses/)  
`Is this an aws server? [y/n] n`
* If you just click enter for the next two steps you will send emails via SMTP but if you want send emails via gmail you 
can set your email address and password. __WARNING__: The config file is __NOT__ secure and the password will be stored as a simple text file  
`Source email address[None]:someEmail@gmail.com`  
`Source password[None]:password`  
* Option to monitor resources while program is running (Recommended)  
`Monitor Compute Resources? [y/n] y`  
    * Location to write log files and log images: clicking enter uses default (Recommended)  
`Output dir: [/Users/andrewbailey/.taskmanager/resource_manager_output]:`  
    * How often the resource monitor will check IO,cpu,memory usage in seconds  
`Access compute resources interval: [5]:` 
* Option to upload logs to s3  
`Upload to S3? [y/n] y` 
    * S3 bucket  
`S3 Upload Bucket: [None]:some_bucket`
    * Default location in bucket (Recommended)  
`S3 Upload Path: [logs/resource_monitor/{date}_{instance_id}/]:` 
    * How often you upload log file to s3 in seconds  
`S3 Upload Interval: [300]:`   



Run some program with taskManager

```taskManager run -c "your --command goes --here"```


If you want to redirect stdout, you would usually use a caret:

```
echo abc123 > file.txt
```

For `taskManager run` you use the `-r` flag to redirect stdout and `-e` to redirect stderr:

```
taskManager run -c "echo abc123" -r std.txt -e stderr.txt
```

Although the config file holds most information needed to run taskManager, if you want to override options in the config file you can get all options for taskManager with the following command

```taskManager run -h```



## Known issues

At the moment, it seems that relative paths do not function correctly when used inside the `-c` argument. The simple workaround is to specify a full absolute path (`/home/ubuntu/path/to/file`)


