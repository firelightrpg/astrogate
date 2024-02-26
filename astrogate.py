"""
Generate a series of networks of jump paths to nearby stars.

Limitations -
The longest jump is two parsecs (~6.5 light years)
"""

import json
import math
import csv
import glob
import operator


class Star:
    str_keys = "id", "hip", "hd", "hr", "gl", "bf", "proper"
    name_preference = "proper", "bf", "gl", "hip", "hd", "hr"

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
            assert key in self.__dict__, f"Attribute '{key}' not found in class variables"
            if key not in self.str_keys:
                try:
                    value = float(value)
                except ValueError:
                    pass

            setattr(self, key, value)

        self.nearby_stars = []

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


class StarPaths:
    """
    Use the HYG database to map paths to nearby stars, based on arbitrary science fiction limitations
    """

    def __init__(self, jump_parsecs: float = 1.83961, parsec_limit: float = 20) -> None:
        """
        initialize the database
        """
        self.stars: list[Star] = []
        self.jump_parsecs = jump_parsecs
        self.parsec_limit = parsec_limit
        self.load_hyg()

    def load_hyg(self) -> None:
        """
        load star data from the hyg database

        limit the results to parsec_limit from Sol
        """

        path = "hygdata*.csv"
        filename = next(iter(glob.glob(path)))

        with open(filename, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if float(row["dist"]) <= self.parsec_limit and (
                    not row["gl"] or row["gl"][-1].isdigit() or row["gl"][-1] == "A"
                ):
                    self.stars.append(Star(**row))

        self.stars = sorted(self.stars, key=operator.attrgetter("dist"))
        self.set_nearby_stars()
        print("Star data loaded and pre-processed")

    def set_nearby_stars(self):
        """

        Returns:

        """
        for star in self.stars:
            star.nearby_stars = self.nearby_stars(star)

    @staticmethod
    def distance(origin: Star, target: Star) -> float:
        """
        Calculate and return the distance from a origin star to a target star, referenced by proper name.

        Do so by converting the angles to radians and applying the spherical trigonometry formula
        https://astronomy.stackexchange.com/a/48953/47073


        Args:
            origin:
            target:
        """
        dec_a, ra_a, d_a = origin.dec, origin.ra, origin.dist
        dec_b, ra_b, d_b = target.dec, target.ra, target.dist

        # Convert angles from degrees to radians
        dec_a = math.radians(dec_a)
        dec_b = math.radians(dec_b)
        ra_a = math.radians(ra_a)
        ra_b = math.radians(ra_b)

        cos_c = math.sin(dec_a) * math.sin(dec_b) + math.cos(dec_a) * math.cos(dec_b) * math.cos(ra_a - ra_b)

        # Ensure cos_c is within the valid range
        cos_c = min(1, max(-1, cos_c))

        # Handle the case where cos_c is very close to 1
        if abs(cos_c - 1) < 1e-12:  # Tolerance for cos_c being close to 1
            return abs(d_a - d_b)  # Approximate distance

        return math.sqrt(d_a**2 + d_b**2 - 2 * d_a * d_b * cos_c)

    def nearby_stars(self, origin: Star) -> list[Star]:
        """
        Get the stars with <parsecs> parsecs from the star with the proper name, <star>

        Args:
            origin:
        """
        nearby_stars = []
        if origin.proper == "Sol":
            # distance from Sol is a field in the database
            for target in self.stars:
                if target.proper == "Sol":
                    continue

                if target.dist <= self.jump_parsecs:
                    # print(f'{target.dist: .2f} parsecs from {self.name(origin)} to {self.name(target)}')
                    nearby_stars.append(target)

            return nearby_stars

        for target in self.stars:
            if origin.name == target.name:
                continue

            distance = self.distance(origin, target)
            if distance <= self.jump_parsecs:
                # print(f"{distance: .2f} parsecs from {origin.name} to {target.name}")
                nearby_stars.append(target)

        return nearby_stars

    def explore_paths(self, path, all_paths, visited_stars):
        """

        Args:
            path:
            all_paths:
            visited_stars:

        Returns:

        """
        current_star = path[-1]
        # print(current_star.name)
        nearby_stars = self.nearby_stars(current_star)

        if not nearby_stars or len(path) > 10:
            all_paths.append(path)
            return

        if len(all_paths) > 1:
            return

        for nearby_star in nearby_stars:
            # if nearby_star.name not in [_.name for _ in path]:
            nearby_name = nearby_star.name
            if nearby_name not in visited_stars:
                visited_stars.add(nearby_name)
                self.explore_paths(path + [nearby_star], all_paths, visited_stars)
                visited_stars.remove(nearby_name)

    def star_paths(self):
        """

        Returns:
            paths from Sol to stars within 2 parsecs
        """
        all_paths = []
        sol = next(s for s in self.stars if s.proper == "Sol")
        visited_stars = set()
        visited_stars.add(sol.name)
        self.explore_paths([sol], all_paths, visited_stars)

        for path in all_paths:
            for star in path:
                print(star.name)

            print()

        return all_paths

    def star_path(self, origin_name: str = "Sol", target_name: str = "Ross 154"):
        """

        Returns:

        """
        origin = next(s for s in self.stars if s.name == origin_name)
        target = next(s for s in self.stars if s.name == target_name)
        path = self.explore_path(origin, target)
        if path:
            print(", ".join([s.name for s in path]))

    def explore_path(self, origin: Star, target: Star, visited=None):
        """

        Args:
            origin:
            target:
            visited:

        Returns:

        """
        if visited is None:
            visited = set()

        if origin.name == target.name:
            return [origin]

        visited.add(origin.name)
        for nearby_star in origin.nearby_stars:
            if nearby_star.name not in visited:
                path = self.explore_path(nearby_star, target, visited.copy())
                if path:
                    return [origin] + path

        return None


if __name__ == "__main__":
    star_paths = StarPaths()
    # with open("star_systems.json", "w", encoding="utf-8") as f:
    #     json.dump(sorted([_.name for _ in star_paths.stars]), f, indent=2)

    _path = star_paths.star_path("Sol", "Del Pav")
    # for _s in _path:
