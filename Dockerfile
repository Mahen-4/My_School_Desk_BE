
FROM python:3.12

#prod, no pycache files
ENV PYTHONDONTWRITEBYTECODE=1
#get logs in prod
ENV PYTHONUNBUFFERED=1

WORKDIR /app

#system dependencies installation
RUN pip install --upgrade pip

COPY requirements.txt /app/

#python dependencies installation
RUN pip install --no-cache-dir -r requirements.txt

#code copy
COPY . .

#port 
EXPOSE 8000

#command to launch
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Commande de prod
#CMD ["gunicorn", "my_school_desk_BE.wsgi:application", "--bind", "0.0.0.0:8000"]

#CMD ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser && gunicorn my_school_desk_BE.wsgi:application --bind 0.0.0.0:8000"]
