from topology import topology
import json


def convert(in_file, output=None, *args, **kwargs):
    with open(in_file) as f:
        data = json.load(f)

    data = topology(data, *args, **kwargs)

    if output is None:
        return data

    with open(output, 'w') as f:
        json.dump(data, f)

