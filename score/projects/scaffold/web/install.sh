#!/bin/bash -x
. "$VENV/bin/activate"
# "$VENV/bin/pip" install score.http score.db score.css score.js \
#     score.webassets score.dbgsrv score.ctx score.tpl score.html score.svg \
#     score.auth score.session score.kvcache score.jsapi
cd "$ROOT"
"$VENV/bin/python" setup.py develop

