# Welcome to my personal web page

This webpage is built using Python, Flask, Gunicorn, Docker and Cloud Run (Google Cloud Platform)

Web service is available at [https://erdemuenal.com/](https://erdemuenal.com/)

## Development

Clone the project

```git clone https://github.com/erdemunal35/personal-website.git```
```cd personal-website/```

Establish the Python3 virtual environment

```python3 -m virtualenv .env```

Activate the environment

```source .env/bin/activate```

Install the dependencies

```pip install -r requirements.txt```

Launch the Gunicorn server

```gunicorn --workers 1 --threads 1 --bind 0.0.0.0:7000 --reload app:app```

## Deployment 
```gcloud config set project PROJECT_ID```

```gcloud run deploy```

## References
Source of the HTML template: [https://www.tooplate.com/view/2115-marvel](https://www.tooplate.com/view/2115-marvel)
