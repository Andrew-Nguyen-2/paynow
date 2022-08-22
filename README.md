# paynow
Website for organizations to collect dues

# Creating a Virtual Environment
python3 -m venv .venv

# Necessary Installations: (pip install <installation>)
django==3.2.8
django-crispy-forms==1.14.0
django-extensions==3.2.0
django-organizations==2.0.2
stripe==4.1.0
xlwt==1.3.0

# Running Locally
python src/manage.py runserver
