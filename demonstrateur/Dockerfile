FROM appbase
WORKDIR /app
COPY bootstrap.py fixtures.py health.py init.py init_verify.py server.py settings.py state.py /app/
USER 10001:10001
CMD ["python", "-B", "server.py"]
