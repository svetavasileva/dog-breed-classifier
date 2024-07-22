import io
import os
import tempfile
import pytest  # type: ignore
from app import app


@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            pass
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_upload_form(client):
    """Test that the upload form is accessible"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Upload Image' in rv.data


def test_upload_file(client):
    """Test file upload"""
    data = {
        'file': (io.BytesIO(b"11111"), 'test.png')
    }
    rv = client.post('/upload', data=data, follow_redirects=True)
    assert rv.status_code == 200


def test_upload_no_file(client):
    """Test uploading with no file"""
    rv = client.post('/upload', data={}, follow_redirects=True)
    assert rv.status_code == 405
    assert b'File type not allowed' not in rv.data
