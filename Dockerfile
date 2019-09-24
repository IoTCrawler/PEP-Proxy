FROM ubuntu:18.04

RUN apt-get update

#Install python3
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install python3 -y

#Install pip3
RUN apt-get install python3-pip -y

#Install java JRE
RUN apt-get install openjdk-11-jre -y
#or 
#RUN apt install default-jre -y --> It works but is not used to have control about the version.

#Install utils
RUN apt-get install net-tools -y
RUN apt-get install vim -y
RUN apt-get install curl -y

# Establish workdir
WORKDIR /opt/PEP-Proxy

#Install requirements
COPY requirements.txt /opt/PEP-Proxy/
RUN pip3 install -r /opt/PEP-Proxy/requirements.txt

#Transfer source and neccesary files
COPY API /opt/PEP-Proxy/API
COPY certs /opt/PEP-Proxy/certs
COPY conf_files /opt/PEP-Proxy/conf_files
COPY PEP-Proxy.py UtilsPEP.py config.cfg cpabe_cipher.jar CapabilityEvaluator.jar /opt/PEP-Proxy/
COPY config /opt/PEP-Proxy/config
COPY local_dependencies /opt/PEP-Proxy/local_dependencies

# application's default port
EXPOSE 1027

# Launch app
CMD [ "python3", "/opt/PEP-Proxy/PEP-Proxy.py" ]