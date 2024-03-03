"""
encapsulation of HYG data
"""


class Star:
    str_keys = "id", "hip", "hd", "hr", "gl", "bf", "proper"
    name_preference = "proper", "bf", "gl", "hip", "hd", "hr"
    valid_keys = (
        "id",
        "hip",
        "hd",
        "hr",
        "gl",
        "bf",
        "proper",
        "ra",
        "dec",
        "dist",
        "pmra",
        "pmdec",
        "rv",
        "mag",
        "absmag",
        "spect",
        "ci",
        "x",
        "y",
        "z",
        "vx",
        "vy",
        "vz",
        "rarad",
        "decrad",
        "pmrarad",
        "pmdecrad",
        "bayer",
        "flam",
        "con",
        "comp",
        "comp_primary",
        "base",
        "lum",
        "var",
        "var_min",
        "var_max",
    )

    def __init__(self, **kwargs):
        self.id = None
        self.hip = None
        self.hd = None
        self.hr = None
        self.gl = None
        self.bf = None
        self.proper = None
        self.ra = None
        self.dec = None
        self.dist = None
        self.pmra = None
        self.pmdec = None
        self.rv = None
        self.mag = None
        self.absmag = None
        self.spect = None
        self.ci = None
        self.x = None
        self.y = None
        self.z = None
        self.vx = None
        self.vy = None
        self.vz = None
        self.rarad = None
        self.decrad = None
        self.pmrarad = None
        self.pmdecrad = None
        self.bayer = None
        self.flam = None
        self.con = None
        self.comp = None
        self.comp_primary = None
        self.base = None
        self.lum = None
        self.var = None
        self.var_min = None
        self.var_max = None
        for key, value in kwargs.items():
            assert key in self.valid_keys, f"Attribute '{key}' not found in class variables"
            if key not in self.str_keys:
                try:
                    value = float(value)
                except ValueError:
                    pass

            setattr(self, key, value)

        self.nearby_stars: list[tuple[float, Star]] = []

    def to_dict(self):
        """
        Write out out vars to a dict
        """
        variables = {k: v for k, v in vars(self).items() if k in self.valid_keys}
        return variables

    @property
    def name(self):
        """
        Not all have proper names, and some databases are empty

        Returns:
            common name or Hipparcos or Henry Draper or Havard Revised or Gliese or Baye/ Flamsteed
        """
        for field in self.name_preference:
            value = getattr(self, field)
            if value:
                return " ".join(value.split())
