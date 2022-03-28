FROM postgres:13


ENV POSTGRES_USER=mikko
ENV POSTGRES_PASSWORD=masterkey
ENV POSTGRES_DB=linkholder

COPY dbase.sql  /docker-entrypoint-initdb.d/
RUN chown postgres:postgres /docker-entrypoint-initdb.d/dbase.sql
