# 安装构建时候必要的工具
FROM jenkins/jenkins:lts 
USER root
RUN apt-get update && apt-get install -y python-pip \
    && pip install virtualenv