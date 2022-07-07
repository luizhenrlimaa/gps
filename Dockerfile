FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1
ENV ACCEPT_EULA=Y
ENV PYTHONUNBUFFERED 1
RUN apt-get update -y
RUN apt-get install apt-transport-https
RUN apt-get install -y gnupg2

# apt-get and system utilities
RUN apt-get update && apt-get install -y \
    curl apt-utils apt-transport-https debconf-utils gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install libssl - required for sqlcmd to work on Ubuntu 18.04
RUN apt-get update && apt-get install -y libssl-dev

# install SQL Server drivers
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

RUN apt-get update -y

RUN apt-get -y install binutils libproj-dev gdal-bin
RUN apt-get -y install libjpeg-dev
RUN apt-get -y install zlib1g-dev
RUN apt-get -y install cron nano curl

RUN apt-get -y install msodbcsql17
RUN apt-get -y install mssql-tools
RUN apt-get -y install unixodbc-dev

RUN apt-get update -yqq \
    && apt-get install -y --no-install-recommends openssl \
    && sed -i 's,^\(MinProtocol[ ]*=\).*,\1'TLSv1.0',g' /etc/ssl/openssl.cnf \
    && sed -i 's,^\(CipherString[ ]*=\).*,\1'DEFAULT@SECLEVEL=1',g' /etc/ssl/openssl.cnf\
    && rm -rf /var/lib/apt/lists/*


RUN mkdir /code
WORKDIR /code
ADD ./code/requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
