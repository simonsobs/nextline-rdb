FROM ghcr.io/simonsobs/nextline-graphql:v0.7.6

COPY ./ nextline-rdb
RUN pip install ./nextline-rdb
RUN rm -rf ./nextline-rdb
