FROM centos:latest

# setup new root password
RUN echo root:pass | chpasswd

RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

COPY . /

# Reset user to root
USER root

RUN yum install -y epel-release
RUN yum install -y python3.9
RUN pip3 install genai
RUN pip3 install web.py
RUN pip3 install google-api-python-client
RUN pip3  install grpcio
RUN pip3 install google.generativeai
RUN pip3 install jsonpickle

RUN export TZ="Asia/Kuala_Lumpur"

RUN yum install -y git
RUN git config --global credential.helper store
RUN git config credential.helper 'cache --timeout=3600000'

ENTRYPOINT [ "ping","belisty.com" ]
