# TaskManager
Monitors resources and sends notifications. Uses AWS SES to send emails (if valid credentials exist under ~/.aws). Locally, can also send email via SMTP.

### Requirements
python3:
  - psutil
  - boto3 (for AWS compatibility)

### Compatibility
Tested on ubuntu 18
