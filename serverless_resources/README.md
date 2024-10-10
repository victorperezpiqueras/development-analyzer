# How to deploy to AWS

You need the following:

- AWS CLI
- Docker
- Serverless Framework
- `/serverless_resources/.env.json` file with the following content:
    ```json
  {
    "sender_email": "email@email.com",
    "error_email": "email@email.com",
    "projects": "[{\"name\":\"name\",\"source\":\"source\",\"dataset\":\"dataset.csv\",\"regenerate\":true,\"max_cycle_time\":null,\"created_last\":null,\"closed_last\":90,\"need_estimate\":false,\"AIRTABLE_API_KEY\":\"AIRTABLE_API_KEY\",\"AIRTABLE_BASE\":\"AIRTABLE_BASE\",\"AIRTABLE_TABLE\":\"AIRTABLE_TABLE\",\"email_list\":[\"email@email.com\"]}]"
  }
    ```

Run `serverless deploy` to deploy the service to AWS.

## AWS resources used

- Lambda
- SES
- S3
- CloudWatch Events (cron jobs)