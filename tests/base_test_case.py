from unittest import TestCase
from tempfile import TemporaryDirectory
import os
from application.app import app, db


class BaseTempDBTestCase(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.tmp_dir = TemporaryDirectory()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(tmp_dir, 'tmp.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        del self.tmp_dir
