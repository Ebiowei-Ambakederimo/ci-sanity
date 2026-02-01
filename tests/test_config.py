import os
import sys
import yaml
from textwrap import dedent

# Ensure src is on sys.path for imports during tests
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Support both repository layouts: either src/ or ci-sanity/src/
candidates = [
    os.path.join(project_root, 'ci-sanity', 'src'),
    os.path.join(project_root, 'src'),
]
src_dir = next((p for p in candidates if os.path.isdir(p) and os.path.exists(os.path.join(p, 'ci_sanity'))), None)
if not src_dir:
    # Fallback to project root (helps some test runners)
    src_dir = project_root
sys.path.insert(0, src_dir)

from ci_sanity.config import Config


def test_defaults():
    cfg = Config()
    assert cfg.platform == 'github'
    assert cfg.secrets == []
    assert cfg.strict is False


def test_set_strict():
    cfg = Config()
    cfg.set_strict(True)
    assert cfg.strict is True
    cfg.set_strict(False)
    assert cfg.strict is False


def test_read_yaml_file(tmp_path):
    data = {'platform': 'gitlab', 'secrets': ['S1', 'S2'], 'strict': True}
    p = tmp_path / 'cfg.yml'
    p.write_text(dedent(yaml.dump(data)))

    cfg = Config(str(p))
    assert cfg.platform == 'gitlab'
    assert cfg.secrets == ['S1', 'S2']
    assert cfg.strict is True


def test_secrets_are_list_and_isolated():
    cfg = Config()
    assert isinstance(cfg.secrets, list)
    cfg.secrets.append('NEW')
    # New config instances shouldn't see changes made to another instance's secrets
    cfg2 = Config()
    assert 'NEW' not in cfg2.secrets