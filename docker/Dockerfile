FROM centos:centos7
MAINTAINER jamiesun <jamiesun.net@gmail.com>


ADD docker/toughlogger.conf /etc/toughlogger.conf
ADD docker/supervisord.conf /etc/supervisord.conf
ADD docker/toughlogger /usr/bin/toughlogger

# install nginx
RUN rpm -Uvh http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm
RUN yum install -y nginx --nogpgcheck
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/nginx.conf
ADD docker/nginx.conf /etc/nginx/nginx.conf
ADD docker/toughlogger-nginx.conf /etc/nginx/conf.d/toughlogger-nginx.conf

RUN chmod +x /usr/bin/toughlogger
RUN mkdir -p /var/toughlogger/data

RUN yum update -y
RUN yum install -y libffi-devel openssl openssl-devel git gcc crontabs python-devel python-setuptools
RUN yum clean all

RUN easy_install pip
RUN pip install supervisor
RUN pip install treq
RUN pip install pymongo
RUN pip install txmongo
RUN pip install cyclone
RUN pip install requests
RUN pip install Mako==0.9.0
RUN pip install Beaker==1.6.4
RUN pip install MarkupSafe==0.18
RUN pip install PyYAML==3.10
RUN pip install SQLAlchemy==0.9.8
RUN pip install Twisted==14.0.2
RUN pip install autobahn==0.9.3-3
RUN pip install bottle==0.12.7
RUN pip install six==1.8.0
RUN pip install tablib==0.10.0
RUN pip install zope.interface==4.1.1
RUN pip install pycrypto==2.6.1
RUN pip install pyOpenSSL>=0.14
RUN pip install service_identity

RUN git clone -b master https://github.com/talkincode/toughlogger.git /opt/toughlogger
RUN ln -s /opt/toughlogger/toughctl /usr/bin/toughctl && chmod +x /usr/bin/toughctl
RUN /opt/toughlogger/toughctl --initdb

EXPOSE 1820

ENTRYPOINT ["/usr/bin/toughlogger","start"]

