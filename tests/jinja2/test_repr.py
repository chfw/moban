from moban.plugins.jinja2.filters.repr import repr as repr_function


def test_string():
    me = "abc"
    expected = repr_function(me)
    assert expected == "'abc'"


def test_list():
    me = [1, 2, 3]
    expected = repr_function(me)
    assert expected == ["'1'", "'2'", "'3'"]
