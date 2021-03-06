import datetime
import json
from appcomposer.application import app as flask_app


def on_leading_bundle_updated(spec, bundle):
    """
    Reports that a leading bundle got updated. If the system is configured for it, then this method will
    forward the changes to the MongoDB database, so that the information can be easily accessed from external
    systems such as GRAASP.
    """
    async_result = None
    if flask_app.config.get("ACTIVATE_TRANSLATOR_MONGODB_PUSHES", False):
        try:
            import mongodb_pusher as pusher
            code = bundle.get_standard_code_string(bundle.lang, bundle.country, bundle.group)

            # Push the task to Celery
            async_result = pusher.push.delay(spec, code, json.dumps(bundle.get_msgs()), datetime.datetime.utcnow())

            print "[MONGODB_PUSHER]: Update reported."
        except:
            # TODO: HANDLE THIS EXCEPTION.
            print "[MONGODB_PUSHER] Failed to notify of leading bundle update"
            pass
    return async_result