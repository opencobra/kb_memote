FROM kbase/kbase:sdkbase.latest
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update

RUN mkdir -p /kb/module
RUN wget https://files.pythonhosted.org/packages/45/ae/8a0ad77defb7cc903f09e551d88b443304a9bd6e6f124e75c0fbbf6de8f7/pip-18.1.tar.gz -O /kb/module/pip.tar.gz
RUN tar -xvf /kb/module/pip.tar.gz -C /kb/module
RUN cd /kb/module/pip-18.1 && python setup.py install

# Here we install a python coverage tool and an
# https library that is out of date in the base image.

#RUN pip is
#RUN pip install coverage

# update security libraries in the base image
#RUN pip install cffi --upgrade \
#    && pip install pyopenssl --upgrade \
#    && pip install ndg-httpsclient --upgrade \
#    && pip install pyasn1 --upgrade \
#    && pip install requests --upgrade \
#    && pip install 'requests[security]' --upgrade

# -----------------------------------------

RUN pip install -I cobra
RUN pip install -I memote
RUN pip install -I cobrakbase

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
