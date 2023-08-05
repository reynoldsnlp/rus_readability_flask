FROM ubuntu:22.04

RUN apt-get update && apt-get install -y git python3 python3-pip wget
RUN wget https://apertium.projectjj.com/apt/install-nightly.sh && chmod ug+x install-nightly.sh && ./install-nightly.sh
RUN apt-get update && apt-get install -y python3-hfst cg3

WORKDIR /app

COPY requirements.txt ./

RUN cd .. && pip install -r app/requirements.txt && cd app

COPY . .

EXPOSE 5000

# SCRIPT_NAME is used by gunicorn to add prefix to paths, e.g. 0.0.0.0:5000/rus-readability
ENV SCRIPT_NAME=/rus-readability

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "rrf:app"]
