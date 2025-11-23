from wptools.exporter import to_php


def test_to_php_generates_nested_array():
    data = {
        "site": {"name": "Demo", "is_public": True, "count": 3},
        "posts": [
            {"title": "Hello", "status": "publish"},
            {"title": "Draft", "status": "draft"},
        ],
        "tags": None,
    }

    php = to_php(data)

    assert "'site' => array(" in php
    assert "'name' => 'Demo'" in php
    assert "'is_public' => true" in php
    assert "'count' => 3" in php
    assert "'posts' => array(" in php
    assert php.strip().startswith("array(")
    assert php.strip().endswith(")")
