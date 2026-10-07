"""Regression coverage for the WebUI sidebar layout rules."""

from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_sidebar_checkbox_and_categories_fit_the_available_width():
    css = (ROOT / "frontend/src/style.css").read_text()

    assert ".filters>input{width:100%" in css
    assert ".checkbox input{width:auto" in css
    assert "flex-wrap:wrap" in css.split(".category-list{", 1)[1].split("}", 1)[0]
    assert "overflow-x:hidden" in css.split(".category-list{", 1)[1].split("}", 1)[0]
    assert "white-space:normal" in css.split(".category-list button{", 1)[1].split("}", 1)[0]
