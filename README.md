# TaskManager
Monitors resources and sends notifications. Uses AWS SES to send emails (if valid credentials exist under ~/.aws). Locally, can also send email via SMTP.

### Requirements
python3:
  - psutil
  - boto3 (for AWS compatibility)

### Compatibility
Tested on ubuntu 18

### Example output
Given that a log has been created, it can then be plotted using `plot_resource_usage.py`:
![plot of log file](TaskManager/log_2019_2_11_17_33_19_458174.png)
