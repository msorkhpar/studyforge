# The shared study server: the pinned Python and the part of the studyforge library
# that serves a course, found by its imports, and nothing else.
#
# ⛔ Build it with `python3 docker/serve/build.py`, never by hand: the build stages the
# library beside this file and hands the one ARG below. No ARG has a default.
#
# ⭐ What is in it: the served runtime (no ingestion, no skill, no synthesis), no course,
# no clip and no narration. A course's site image starts FROM this image, by digest,
# adds its own files, and runs `serve /corpus --published`.
#
# ⛔ It runs as an unprivileged user and asks for no network: it reads the files under
# its corpus directory and answers on the one port the site names. A course stage that
# writes its files switches to root for that layer and back again.
#
# Pinned by tag AND digest: the digest is what makes the build reproducible.
FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

ARG SERVE_VERSION
COPY library/ /opt/studyforge/library/
ENV PYTHONPATH=/opt/studyforge/library PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
LABEL org.studyforge.serve.version="${SERVE_VERSION}"
USER 1000:1000
ENTRYPOINT ["python3", "-m", "studyforge.cli"]
