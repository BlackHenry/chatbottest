FROM python:2.7


RUN pip install pandas  
RUN pip install numpy  
RUN pip install webapp2

ADD webhook.py /


CMD [ "python", "./webhook.py" ]
