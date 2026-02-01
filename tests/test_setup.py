import ast
import os


def _parse_setup_keywords(path):
    src = open(path, 'r', encoding='utf-8').read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, 'id', None) or getattr(func, 'attr', None)
            if name == 'setup':
                return {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords}
    return {}


def test_setup_metadata():
    path = os.path.join(os.path.dirname(__file__), '..', 'setup.py')
    kws = _parse_setup_keywords(path)
    assert kws.get('name') == 'ci-sanity'
    assert kws.get('version') == '0.1.0'
    install_requires = kws.get('install_requires', []) or []
    assert any('pyyaml' in r for r in install_requires)