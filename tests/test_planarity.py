import os
import tempfile
from unittest import SkipTest

import planarity

class TestPlanarity:
    @classmethod
    def setup_class(self):
        self.k5_adj_symmetric = {0: {1: {}, 2: {}, 3: {}, 4: {}},
                     1: {0: {}, 2: {}, 3: {}, 4: {}},
                     2: {0: {}, 1: {}, 3: {}, 4: {}},
                     3: {0: {}, 1: {}, 2: {}, 4: {}},
                     4: {0: {}, 1: {}, 2: {}, 3: {}}}

        self.k5_adj = {0: {1: {}, 2: {}, 3: {}, 4: {}},
                     1: {2: {}, 3: {}, 4: {}},
                     2: {3: {}, 4: {}},
                     3: {4: {}},
                     4: {}}

        self.k5_adj_set = {0: set([1,2,3,4]),
                         1: set([2,3,4]),
                         2: set([3,4]),
                         3: set([4]),
                         4: set([])}

        self.k5_adj_list = {0: list([1,2,3,4]),
                         1: list([2,3,4]),
                         2: list([3,4]),
                         3: list([4]),
                         4: list([])}

        self.k5_edgelist = [(0, 1),
                          (0, 2),
                          (0, 3),
                          (0, 4),
                          (1, 2),
                          (1, 3),
                          (1, 4),
                          (2, 3),
                          (2, 4),
                          (3, 4)]

        self.p4_adj = {0: {1: {}},
                     1: {0: {}, 2: {}},
                     2: {1: {}, 3: {}},
                     3: {2: {}}}

        self.p4_edgelist = [(0, 1), (1, 2), (2, 3)]


    def test_is_planar_edgelist_input(self):
        P = planarity.PGraph(self.p4_edgelist)
        assert P.is_planar() is True
        P = planarity.PGraph(self.k5_edgelist)
        assert P.is_planar() is False

    def test_is_planar_edgelist_input_function(self):
        assert planarity.is_planar(self.k5_edgelist) is False

    def test_is_planar_adj_input(self):
        P = planarity.PGraph(self.p4_adj)
        assert P.is_planar() is True
        P=planarity.PGraph(self.k5_adj)
        assert P.is_planar() is False

    def test_is_planar_adj_input_function(self):
        assert planarity.is_planar(self.k5_adj) is False

    def test_is_planar_adj_symmetric(self):
        P = planarity.PGraph(self.k5_adj_symmetric)
        assert P.is_planar() is False

    def test_is_planar_adj_set(self):
        P = planarity.PGraph(self.k5_adj_set)
        assert P.is_planar() is False

    def test_is_planar_adj_list(self):
        P = planarity.PGraph(self.k5_adj_list)
        assert P.is_planar() is False

    def test_goldner_harary(self):
        # goldner-harary graph
        # http://en.wikipedia.org/wiki/Goldner%E2%80%93Harary_graph
        # a maximal planar graph
        e = [(1,2), ( 1,3 ),( 1,4 ),( 1,5 ),( 1,7 ),( 1,8 ),( 1,10 ),
            (1,11 ),( 2,3 ),( 2,4 ),( 2,6 ),( 2,7 ),( 2,9 ),( 2,10 ),
            ( 2,11 ),( 3,4 ),( 4,5 ),( 4,6 ),( 4,7 ),( 5,7 ),( 6,7 ),
            ( 7,8 ),( 7,9 ),( 7,10 ),( 8,10 ),( 9,10 ),( 10,11)]
        P = planarity.PGraph(e)
        assert P.is_planar() is True

    def test_kuratowski_k5(self):
        P = planarity.PGraph(self.k5_edgelist)
        edges = P.kuratowski_edges()
        assert frozenset(frozenset(x) for x in edges) == frozenset(frozenset(x) for x in self.k5_edgelist)

    def test_kuratowski_k5_function(self):
        edges = planarity.kuratowski_edges(self.k5_edgelist)
        assert frozenset(frozenset(x) for x in edges) == frozenset(frozenset(x) for x in self.k5_edgelist)

    def test_no_kuratowski_k5m(self):
        edges = self.k5_edgelist[:]
        edges.remove((0,1))
        P = planarity.PGraph(edges)
        edges = P.kuratowski_edges()
        assert frozenset(edges) == frozenset()

    def test_draw_text(self):
        e = ([1,2],)
        P = planarity.PGraph(e)
        s = P.ascii()#.decode()
        assert s == '1\n|\n2\n \n'

    def test_write_adjlist(self):
        e = ([1,2],)
        P = planarity.PGraph(e)
        fname = tempfile.mktemp()
        P.write(fname)
        d = open(fname).read()
        answer = 'N=2\n1: 2 0\n2: 1 0\n'
        assert d == answer
        os.unlink(fname)

    def test_write_adjmatrix(self):
        e = ([1,2],)
        P = planarity.PGraph(e)
        fname = tempfile.mktemp()
        P.write(fname, planarity.WRITE_ADJMATRIX)
        d = open(fname).read()
        answer = '2\n 1\n  \n'
        assert d == answer
        os.unlink(fname)

    def test_write_g6(self):
        e = ([1,2],)
        P = planarity.PGraph(e)
        fname = tempfile.mktemp()
        P.write(fname, planarity.WRITE_G6)
        d = open(fname).read()
        answer = '>>graph6<<A_\n'
        assert d == answer
        os.unlink(fname)

    def test_write_function_g6(self):
        e = ([1,2],)
        fname = tempfile.mktemp()
        planarity.write(e, fname, planarity.WRITE_G6)
        d = open(fname).read()
        answer = '>>graph6<<A_\n'
        assert d == answer
        os.unlink(fname)

    @staticmethod
    def _get_pyplot_agg():
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except ImportError:
            raise SkipTest('matplotlib not available.')
        return plt

    @staticmethod
    def _capture_savefig(plt, monkeypatch):
        captured = {}

        def fake_savefig(*args, **kwargs):
            captured.update(kwargs)

        monkeypatch.setattr(plt, 'savefig', fake_savefig)
        return captured

    # This is commented out because it shows promise for testing the padding
    # because it reads the actual image, but it does not currently work.
    # Also, mktemp() is deprecated and should be replaced with using
    # tmp_path and a specific name (see test_draw_colors.py).
    # 
    # def test_draw_pad_inches_controls_output_padding(self):
    #     plt = self._get_pyplot_agg()
    #     P = planarity.PGraph(self.p4_edgelist)
    #     zero_fname = tempfile.mktemp(suffix='.png')
    #     half_fname = tempfile.mktemp(suffix='.png')
    #     try:
    #         P.draw(outfileName=zero_fname, pad_inches=0.0)
    #         P.draw(outfileName=half_fname, pad_inches=0.5)
    #         zero = plt.imread(zero_fname)
    #         half = plt.imread(half_fname)
    #         # With pad_inches=0.0, the drawing extends to the borders of
    #         # the image.
    #         nonwhite = (zero[:, :, :3] < 0.999).any(axis=2)
    #         rows = nonwhite.any(axis=1).nonzero()[0]
    #         cols = nonwhite.any(axis=0).nonzero()[0]
    #         h, w = nonwhite.shape
    #         margins = (cols.min(), w - 1 - cols.max(),
    #                    rows.min(), h - 1 - rows.max())
    #         assert max(margins) <= 2
    #         # A pad_inches of 0.5 adds 0.5 inches of padding per side at
    #         # the default figure dpi of 100.
    #         assert abs((half.shape[0] - zero.shape[0]) - 100) <= 2
    #         assert abs((half.shape[1] - zero.shape[1]) - 100) <= 2
    #     finally:
    #         os.unlink(zero_fname)
    #         os.unlink(half_fname)


