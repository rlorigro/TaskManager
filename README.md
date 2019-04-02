# TaskManager
Monitors resources and sends notifications. Uses AWS SES to send emails (if valid credentials exist under ~/.aws). Locally, can also send email via SMTP.

## Email notifier usage

To use on AWS, you must first have your `~/.aws` credentials configured. The easiest way to do this is to run `aws configure` on your instance. If you haven't already verified your email in the AWS SES console then you also need to go find your email address in the SES email list and click "verify".

#### Recommended Usage:
Install via pip   

```pip install taskManager```

Configure setup

```taskManager configure```

Run taskManager on some program

```taskManager run -c "your --command goes --here"```


#### Optional Usage:

Use this syntax to get an email notification when your command is finished running:

```
python3 ~/software/TaskManager/run.py \
-c "your --command goes --here" \
--to recipient1@email.com,recipient2@email.com \
--from recipient1@email.com \
```

Here is how the email currently looks:

```
Process with the following arguments:
        samtools view -h GM24385.wtdbg2.bam
on instance i-0e4c60e37ccc2c13b has concluded after 67.20 minutes.
```

If you want to redirect, i.e. you would usually use a caret:

```
echo abc123 > file.txt
```

then you must instead use the `-r` flag instead of the `>`:

```
python3 ~/software/TaskManager/run.py \
-c "echo abc123" \
--to recipient1@email.com,recipient2@email.com \
--from recipient1@email.com \
-r file.txt
```

### Requirements
python3:
  - psutil
  - boto3 (for AWS compatibility)
  - py3helpers
 
### Compatibility
Tested on ubuntu 18

### Resource monitor example output
Given that a log has been created, it can then be plotted using `plot_resource_usage.py`:

![plot of log file](https://github.com/rlorigro/TaskManager/raw/master/log_2019_2_11_17_33_19_458174.png)

## Known issues

At the moment, it seems that relative paths do not function correctly when used inside the `-c` argument. The simple workaround is to specify a full absolute path (`/home/ubuntu/path/to/file`)


