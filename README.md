# Intelligent Trading Development 
This document describe how works the development and deployment process.

[![Build Status](https://travis-ci.org/IntelligentTrading/IntelligentTrading.svg?branch=master)](https://travis-ci.org/IntelligentTrading/IntelligentTrading)


## Configure GCP
The next steps require the **gcloud** tool, more informations: [gcloud downloads](https://cloud.google.com/sdk/downloads)


Set your account:

`$ gcloud config set account email.account@mydomain.com`

Set the project:

`$ gcloud config set project project-id`

More informations about [Google App Engine](https://cloud.google.com/appengine/docs/python/) standard environment. 


## Testing locally

### Worker Service

Install the dependencies:

`worker/$ pip3.6 install -t lib -r requirements.txt -U` 

**NOTE** if run many times the `pip` do you can insert this argument `--upgrade` 

Start the development server:

`python3.6 -m main`

Access the application:

[http://localhost:8080](http://localhost:8080)



## Deploy to App Engine

`gcloud app deploy index.yaml cron.yaml`
