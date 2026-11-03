"""UI integration fixture ONLY; app.py never imports this or FakeModel."""
import sys,tempfile,threading
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_system import FakeModel
from app import make_server
from store import Store

with tempfile.TemporaryDirectory() as folder:
    model=FakeModel(bad_schedule=True)
    with patch('config.settings',return_value={'key':'UI_TEST_NOT_AN_API_KEY','model':'UI_TEST_DOUBLE'}):
        server=make_server(0,model,Store(folder))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        print('http://127.0.0.1:'+str(server.server_address[1]),flush=True)
        try:sys.stdin.readline()
        finally:server.shutdown();server.server_close()
