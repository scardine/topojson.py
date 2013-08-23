# coding=utf8
from mytypes import types
from stitchpoles import stitch
from coordinatesystems import systems
from bounds import bound
from line import Line
from clockwise import clock
import logging

E = 1e-6

logging.basicConfig(format='%(asctime)s %(message)s')


def is_infinit(n):
    return abs(n) == float('inf')


def topology(objects, stitch_poles=True, verbose=True, e_max=0, coordinate_system=None, object_name='name',
             id_key='id', quantization_factor=1e4, property_transform=None):

    id_ = lambda d: d[id_key]

    if property_transform is None:
        def property_transform(outprop, key, inprop):
            outprop[key] = inprop
            return True

    stitch_poles = True
    verbose = False
    e_max = 0
    object_name = 'name'
    if coordinate_system:
        system = systems[coordinate_system]

    if objects.has_key('type') and objects['type'] == 'FeatureCollection':
        objects = {object_name: objects}
    ln = Line(quantization_factor)

    [x0, x1, y0, y1] = bound(objects)

    oversize = x0 < -180 - E or x1 > 180 + E or y0 < -90 - E or y1 > 90 + E
    if coordinate_system is None:
        if oversize:
            system = systems["cartesian"]
        else:
            system = systems["spherical"]
        coordinate_system = system.name

    if coordinate_system == 'spherical':
        if oversize:
            raise Exception(u"spherical coordinates outside of [±180°, ±90°]")
        if stitch_poles:
            stitch(objects)
            [x0, x1, y0, y1] = bound(objects)
        if x0 < -180 + E:
            x0 = -180
        if x1 > 180 - E:
            x1 = 180
        if y0 < -90 + E:
            y0 = -90
        if y1 > 90 - E:
            y1 = 90

    if is_infinit(x0):
        x0 = 0
    if is_infinit(x1):
        x1 = 0

    if is_infinit(y0):
        y0 = 0
    if is_infinit(y1):
        y1 = 0

    logging.debug("{}".format([x0, y0, x1, y1]))

    kx, ky = make_ks(quantization_factor, x0, x1, y0, y1)
    if not quantization_factor:
        quantization_factor = x1 + 1
        x0 = y0 = 0

    class FindEmax(types):
        def __init__(self, obj):
            self.emax = 0
            self.obj = obj

        def point(self, point):
            x1 = point[0]
            y1 = point[1]
            x = ((x1 - x0) * kx)
            y = ((y1 - y0) * ky)
            ee = system['distance'](x1, y1, x / kx + x0, y / ky + y0)
            if ee > self.emax:
                self.emax = ee
            point[0] = int(x)
            point[1] = int(y)

    finde = FindEmax(objects)
    e_max = finde.emax
    clock(objects, system.ring_area)

    class findCoincidences(types):
        def line(self, line):
            for point in line:
                lines = ln.arcs.coincidenceLines(point)
                if not line in lines:
                    lines.append(line)

    fcInst = findCoincidences(objects)
    polygon = lambda poly: map(ln.lineClosed, poly)

    #Convert features to geometries, and stitch together arcs.
    class makeTopo(types):
        def Feature(self, feature):
            geometry = feature["geometry"]
            if feature['geometry'] == None:
                geometry = {}
            if feature.has_key('id'):
                geometry['id'] = feature['id']
            if feature.has_key('properties'):
                geometry['properties'] = feature['properties']
            return self.geometry(geometry)

        def FeatureCollection(self, collection):
            collection['type'] = "GeometryCollection"
            collection['geometries'] = map(self.Feature, collection['features'])
            del collection['features']
            return collection

        def GeometryCollection(self, collection):
            collection['geometries'] = map(self.geometry, collection['geometries'])

        def MultiPolygon(self, multiPolygon):
            multiPolygon['arcs'] = map(polygon, multiPolygon['coordinates'])

        def Polygon(self, polygon):
            polygon['arcs'] = map(ln.lineClosed, polygon['coordinates'])

        def MultiLineString(self, multiLineString):
            multiLineString['arcs'] = map(ln.lineOpen, multiLineString['coordinates'])

        def LineString(self, lineString):
            lineString['arcs'] = ln.lineOpen(lineString['coordinates'])

        def geometry(self, geometry):
            if geometry is None:
                geometry = {}
            else:
                types.geometry(self, geometry)
            geometry['id'] = id_(geometry)
            if geometry['id'] is None:
                del geometry['id']
            properties0 = geometry['properties']
            if properties0:
                properties1 = {}
                del geometry['properties']
                for key0 in properties0:
                    if property_transform(properties1, key0, properties0[key0]):
                        geometry['properties'] = properties1
            if 'arcs' in geometry:
                del geometry['coordinates']
            return geometry

    makeTopoInst = makeTopo(objects)
    return {
        'type': "Topology",
        'transform': {
            'scale': [1.0 / kx, 1.0 / ky],
            'translate': [x0, y0]
        },
        'objects': makeTopoInst.outObj,
        'arcs': ln.getArcs()
    }


def make_ks(Q, x0, x1, y0, y1):
    [x, y] = [1, 1]
    if Q:
        if x1 - x0:
            x = (Q - 1.0) / (x1 - x0)
        if y1 - y0:
            y = (Q - 1.0) / (y1 - y0)
    return [x, y]


def lines_equal(a, b):
    for arg in (a, b):
        if not isinstance(arg, list):
            return False
    return a == b


def distinct_point(a, b):
    if is_point(a) and is_point(b):
        return a != b
    return True


def is_point(p):
    if isinstance(p, basestring):
        return False

    try:
        float(p[0]), float(p[1])
    except (TypeError, IndexError, ValueError):
        return False
    else:
        return len(p) == 2
