FROM ghcr.io/nextline-dev/nextline-graphql:v0.9.1

COPY ./ nextline-rdb
RUN pip install ./nextline-rdb
RUN rm -rf ./nextline-rdb
