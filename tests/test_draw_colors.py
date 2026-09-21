"""Exercise color controls on real artists and rendered PNGs."""

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.colors import to_rgba
from PIL import Image
import pytest

import planarity


EDGES = [('a', 'c'), ('a', 'd'), ('a', 'e'), ('b', 'c'), ('b', 'd'),
         ('b', 'e'), ('c', 'd'), ('c', 'e'), ('d', 'e')]


@pytest.fixture(autouse=True)
def isolated_figures():
    with matplotlib.rc_context():
        yield
    plt.close('all')


@pytest.fixture(params=['function', 'method'])
def draw(request):
    if request.param == 'function':
        return lambda **kwargs: planarity.draw(EDGES, **kwargs)
    return lambda **kwargs: planarity.PGraph(EDGES).draw(**kwargs)


@pytest.mark.parametrize('option,color', [
    ('facecolor', '#abcdef'),
    ('vertex_facecolor', 'gold'),
    ('vertex_bordercolor', (0.3, 0.2, 0.8)),
    ('vertex_label_facecolor', 'lightgreen'),
    ('vertex_label_bordercolor', '#aabbcc'),
    ('edge_linecolor', 'magenta'),
])
def test_individual_colors_reach_artists(draw, option, color):
    draw(**{option: color})
    ax = plt.gca()
    if option == 'facecolor':
        actual = [plt.gcf().get_facecolor()]
    elif option.startswith('vertex_label_'):
        method = ('get_facecolor' if option.endswith('facecolor')
                  else 'get_edgecolor')
        actual = [getattr(text.get_bbox_patch(), method)() for text in ax.texts]
        assert len(actual) == 5
    elif option.startswith('vertex_'):
        vertices = next(c for c in ax.collections if isinstance(c, PatchCollection))
        actual = (vertices.get_facecolors() if option.endswith('facecolor')
                  else vertices.get_edgecolors())
    else:
        actual = [c.get_colors()[0] for c in ax.collections
                  if isinstance(c, LineCollection)]
        assert len(actual) == 9
    assert len(actual) > 0
    for rgba in actual:
        assert tuple(rgba) == pytest.approx(to_rgba(color))


@pytest.mark.parametrize('transparent', [False, True])
def test_png_background_and_transparency(draw, tmp_path, transparent):
    output = tmp_path / 'colors.png'
    # A user's savefig style must not override an explicit draw() facecolor.
    matplotlib.rcParams['savefig.facecolor'] = 'red'
    draw(outfileName=str(output), facecolor='#abcdef', transparent=transparent,
         figsize=(4, 3), dpi=100)
    with Image.open(output) as image:
        # The tight bounding box (Issue #100) crops the saved image to the
        # drawing plus pad_inches, so it is strictly smaller than the
        # nominal figsize canvas at the given dpi.
        width, height = image.size
        assert width == 400
        assert height == 300
        rgba = image.convert('RGBA')
        if transparent:
            assert rgba.getpixel((0, 0))[3] == 0
            assert rgba.getextrema()[3][1] == 255  # Graph remains visible.
        else:
            assert rgba.getpixel((0, 0)) == (171, 205, 239, 255)
    assert plt.gcf().get_facecolor() == pytest.approx(to_rgba('#abcdef'))


def test_color_controls_combine_without_labels(draw, tmp_path):
    draw(labels=False, outfileName=str(tmp_path / 'no-labels.png'),
         facecolor='white', transparent=True, vertex_facecolor='yellow',
         vertex_bordercolor='black', vertex_label_facecolor='pink',
         vertex_label_bordercolor='green', edge_linecolor='red')
    assert not plt.gca().texts
    vertices = next(c for c in plt.gca().collections if isinstance(c, PatchCollection))
    assert tuple(vertices.get_facecolors()[0]) == pytest.approx(to_rgba('yellow'))
    assert tuple(vertices.get_edgecolors()[0]) == pytest.approx(to_rgba('black'))


def test_default_background_resets_after_custom_draw(draw):
    draw(facecolor='red')
    draw()
    assert plt.gcf().get_facecolor() == pytest.approx(to_rgba('#ffffff'))
    for text in plt.gca().texts:
        assert text.get_bbox_patch().get_facecolor() == to_rgba('white')
        assert text.get_bbox_patch().get_edgecolor() == to_rgba('black')


def test_existing_figure_options(draw):
    draw(figsize=(4, 3), dpi=120)
    assert tuple(plt.gcf().get_size_inches()) == pytest.approx((4, 3))
    assert plt.gcf().dpi == 120


def test_unknown_keyword_still_rejected(draw):
    with pytest.raises(ValueError, match='not a supported draw'):
        draw(vertex_colour='red')


def test_invalid_color_rejected(draw):
    with pytest.raises(ValueError, match='not-a-color'):
        draw(vertex_facecolor='not-a-color')
