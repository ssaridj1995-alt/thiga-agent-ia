FROM guardbase
WORKDIR /guard
COPY guard.py heartbeat.py netlink.py ruleset.py policy.nft policy.expected.json /guard/
ENTRYPOINT ["python", "-B", "/guard/guard.py"]
