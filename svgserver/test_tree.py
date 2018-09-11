import pytest

from svgserver.tree import node, build_tree


@pytest.mark.parametrize(
    "layers,want",
    [
        (["a"], [node(name="a", subs=None, layer="a")]),
        (
            ["a", "b"],
            [node(name="a", subs=None, layer="a"), node(name="b", subs=None, layer="b")],
        ),
        (
            ["a_x", "a_y"],
            [
                node(
                    name="a",
                    subs=[
                        node(name="x", subs=None, layer="a_x"),
                        node(name="y", subs=None, layer="a_y"),
                    ],
                    layer=None,
                )
            ],
        ),
        (
            ["a_x", "a_y", "a", "a_z"],
            [
                node(
                    name="a",
                    subs=[
                        node(name="x", subs=None, layer="a_x"),
                        node(name="y", subs=None, layer="a_y"),
                        node(name="a", subs=None, layer="a"),
                        node(name="z", subs=None, layer="a_z"),
                    ],
                    layer=None,
                )
            ],
        ),
        (
            ["a_x", "b", "a_y"],
            [
                node(name=("a", "x"), subs=None, layer="a_x"),
                node(name="b", subs=None, layer="b"),
                node(name=("a", "y"), subs=None, layer="a_y"),
            ],
        ),
    ],
)
def test_build_tree(layers, want):
    got = build_tree(layers)
    assert got == want
