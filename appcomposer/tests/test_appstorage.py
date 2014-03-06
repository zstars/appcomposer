
import appcomposer
import tempfile
import os
from appcomposer.appstorage import create_app


class TestAppstorage:

    def setUp(self):
        appcomposer.app.config['DEBUG'] = True
        appcomposer.app.config["SECRET_KEY"] = 'secret'
        self.app = appcomposer.app.test_client()

    def tearDown(self):
        pass

    def test_create(self):
        print "DONE: " + str(self.app.get("/").data)
        pass