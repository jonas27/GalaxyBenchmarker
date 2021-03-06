FROM python:3.7

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip uninstall bioblend -y
RUN git clone https://github.com/galaxyproject/bioblend.git && cd bioblend && python setup.py install

RUN cd / && git clone https://github.com/usegalaxy-eu/workflow-testing.git