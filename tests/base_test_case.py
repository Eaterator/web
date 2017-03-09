from unittest import TestCase
from tempfile import TemporaryDirectory
import os
from application.app import app, db


class BaseTempDBTestCase(TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.tmp_dir = TemporaryDirectory()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(self.tmp_dir.name, 'tmp.db')
        self.app = app.test_client()
        self.db = db
        self.db.session.close()
        self.db.drop_all()
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        del self.tmp_dir
