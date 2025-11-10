FROM ghcr.io/simonsobs/nextline-graphql:v0.8.1

COPY ./ nextline-rdb
RUN pip install ./nextline-rdb
RUN rm -rf ./nextline-rdb
