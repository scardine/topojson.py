import json, os
import unittest


class Geo2TopoTest(unittest.TestCase):
    """Compares output with the reference implementation"""
    def setUp(self):
        from topojson import topojson
        print os.getcwd()
        self.candidate = topojson('brazil.geo.json')
        self.reference = json.load(open('brazil.topo.json'))

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
