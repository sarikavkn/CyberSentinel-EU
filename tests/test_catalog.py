import json
from pathlib import Path
def test_catalog_shape():
    d=json.loads((Path(__file__).parents[1]/'regulatory/frameworks_and_requirements.json').read_text(encoding='utf-8'))
    assert len(d['frameworks'])>=6
    assert len(d['requirements'])>=30
