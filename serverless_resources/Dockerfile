FROM public.ecr.aws/lambda/python:3.10

WORKDIR /var/task

# Copy the current directory contents into the container at /app
COPY serverless_resources/cron_lambda.py ./cron_lambda.py
COPY development_analyzer ./development_analyzer
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# run lambda handler
CMD ["cron_lambda.handler"]

