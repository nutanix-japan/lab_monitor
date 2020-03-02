From python:3.8-slim
RUN apt update && \
    apt install -y snmp && \
    apt clean
RUN pip install fastapi uvicorn
RUN pip install pymongo schedule
WORKDIR /src
COPY ./src /src
RUN chmod +x /src/start.sh
CMD ["/src/start.sh"]