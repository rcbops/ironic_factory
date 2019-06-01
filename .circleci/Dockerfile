FROM centos:centos7

RUN yum update -y -q -e 0
RUN yum install -y -q -e 0 openscap-utils
RUN yum install -y -q -e 0 libguestfs
RUN yum install -y -q -e 0 libguestfs-tools
RUN yum install -y -q -e 0 atomic
RUN yum install -y -q -e 0 wget lynx

RUN wget https://oval.cisecurity.org/repository/download/5.11.2/all/oval.xml

