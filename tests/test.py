import json
import unittest


class Geo2TopoTest(unittest.TestCase):
    """Compares output with the reference implementation"""
    def setUp(self):
        from topojson import topojson
        self.candidate = topojson('brazil.geo.json')
        self.reference = json.load(open('brazil.topo.json'))

    def test_transform(self):
        c = self.candidate.get('transform', None)
        r = self.candidate.get('transform')
        self.assertIsNotNone(c, 'transform element should be present.')
        self.assertIsNotNone(c.get('scale', None), 'transform must have a scale element.')
        self.assertIsNotNone(c.get('translate', None), 'transform must have a translate element.')
        self.assertEqual(c['transform']['scale'], r['transform']['scale'], "transform['scale'] don't match.")
        self.assertEqual(c['transform']['translate'], r['transform']['translate'], "transform['translate'] don't match.")

    def test_compare_arcs(self):
        c = self.candidate.get('arcs', None)
        r = self.reference.get('arcs')
        self.assertIsNotNone(c, 'The arcs element should be present.')
        self.assertEqual(len(c), len(r), "Arc shold have the same length")
        self.assertEqual(c, r, "Arcs should be equal?")

    def test_compare_keys(self):
        """Results shold have the same toplevel keys"""
        self.assertListEqual(self.candidate.keys(), self.reference.keys())

if __name__ == '__main__':
    unittest.main()
