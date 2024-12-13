import pytest

from lsfm_fusion_napari._widget import (
    FusionWidget,
)


@pytest.fixture
def create_widget(make_napari_viewer):
    yield FusionWidget(make_napari_viewer())


def test_widget_creation(create_widget):
    """
    Test if the widget is created correctly
    Widget should be an instance of DestripeWidget

    Parameters
    ----------
    create_widget : DestripeWidget
        Instance of the main widget
    """
    assert isinstance(create_widget, FusionWidget)
