"""Matplotlib custom colormap

You can customize `_custom_cmaps` to define original colormap.

See also: matplotlib.colors.LinearSegmentedColormap.from_list()
https://matplotlib.org/stable/api/_as_gen/matplotlib.colors.LinearSegmentedColormap.html#matplotlib.colors.LinearSegmentedColormap.from_list
"""

_custom_cmaps = [
    # dict(
    #     name = "custom1",
    #     colors = ["#0000ff","#00ff00","#ff0000"],
    #     # N = 256,
    #     # gamma = 1.0,
    # ),
    # dict(
    #     name = "custom2",
    #     colors = ["#ff0000","#ff0000","#00ff00"],
    #     # N = 256,
    #     # gamma = 1.0,
    # ),
]

def conv(cmaps_list: list) -> dict:
    _cmaps = dict()
    for cmap in cmaps_list:
        name = cmap["name"]
        _cmaps[name] = cmap.copy()
    return _cmaps

custom_cmaps = conv(_custom_cmaps)
