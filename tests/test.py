import json
import unittest


class Geo2TopoTest(unittest.TestCase):
    """Compares output with the reference implementation"""
    def setUp(self):
        from topojson import topojson
        self.candidate = topojson('brazil.geo.json')
        self.reference = json.load(open('brazil.topo.json'))

    def test_is_point(self):
        from topojson.topology import is_point
        self.assertTrue(is_point([0, 1]))
        self.assertFalse(is_point('01'))
        self.assertFalse(is_point(['test', 1]))

    def test_point_compare(self):
        from topojson.topology import distinct_point
        self.assertFalse(distinct_point([0, 1], [0, 1]))
        self.assertTrue(distinct_point([0, 1], [1, 1]))
        self.assertFalse(distinct_point([2.0, 1], [2, 1]))

    def test_transform(self):
        c = self.candidate.get('transform', None)
        r = self.candidate.get('transform')
        self.assertIsNotNone(c, 'transform element should be present.')
        self.assertIsNotNone(c.get('scale', None), 'transform must have a scale element.')
        self.assertIsNotNone(c.get('translate', None), 'transform must have a translate element.')
        self.assertEqual(c['scale'], r['scale'], "transform['scale'] don't match.")
        self.assertEqual(c['translate'], r['translate'], "transform['translate'] don't match.")

    def test_type(self):
        t1 = self.candidate.get('type', None)
        t2 = self.reference.get('type')
        self.assertEqual(t1, t2, 'Type must match "{}"'.format(t2))

    def test_cartesian_ring_area(self):
        from topojson.coordinatesystems import systems
        cartesian = systems['cartesian']
        p1 = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
        p2 = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]
        self.assertTrue(cartesian.ring_area(p1) > 0, "clockwise area is positive")
        self.assertTrue(cartesian.ring_area(p2) < 0, "counterclockwise area is negative")

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
