"""
Generate a series of networks of jump paths to nearby stars.

Limitations -
The longest jump is two parsecs (~6.5 light years)

1G orbital distance by size
Dwarf Planets (e.g., Ceres):
    A few kilometers to tens of kilometers above the surface, let's say approximately 1-50 kilometers.

Sub-Earth Planets (e.g., Mars):
    Similar to dwarf planets, perhaps ranging from a few kilometers to tens of kilometers, approximately 1-50
    kilometers.

Earth-like Planets (e.g., Earth):
    Since Earth already has 1G at its surface, we're looking at the altitude above the surface. This could range from a
    few hundred kilometers to a few thousand kilometers, roughly 200-2,000 kilometers.

Super-Earths:
    Given their increased mass compared to Earth-like planets, we might estimate the distance required to be slightly
    greater than Earth-like planets, perhaps in the range of 500-5,000 kilometers.

Mini-Neptunes and Neptunian Planets:
    Due to their lower densities and larger sizes compared to terrestrial planets, achieving 1G in orbit around these
    planets would require significantly greater distances. This could range from thousands to tens of thousands of
    kilometers, roughly 5,000-50,000 kilometers.

Giant Planets (e.g., Jupiter):
    These massive planets would require considerable distances for achieving 1G in orbit. We might estimate this to be
    in the range of tens of thousands to hundreds of thousands of kilometers, approximately 20,000-200,000 kilometers.

Super-Jupiters:
    Given their even larger size and mass compared to Jupiter, the distance required for 1G in orbit around them would
    likely be similar to or greater than Jupiter. We could estimate this to be in the range of 50,000-500,000
    kilometers.
"""

import csv
import glob
import json
import math
import operator
import random
from operator import itemgetter

from star import Star


class NearbyStars:
    """
    Use the HYG database to populate nearby star systems and for navigation based on arbitrary limitations
    """

    jump_parsecs = 2
    parsec_limit = 4

    def __init__(self, jump_parsecs: float = None, parsec_limit: float = None) -> None:
        """
        initialize the database
        """
        self.stars: list[Star] = []
        if jump_parsecs is not None:
            self.jump_parsecs = jump_parsecs

        if parsec_limit is not None:
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
                if float(row["dist"]) <= self.parsec_limit:
                    # and (
                    # not row["gl"] or row["gl"][-1].isdigit() or row["gl"][-1] == "A"
                    # ):
                    self.stars.append(Star(**row))

        self.stars = sorted(self.stars, key=operator.attrgetter("dist"))
        self.set_nearby_stars()
        print("Star data loaded and pre-processed")
        print(f"{len(self.stars)} stars within {self.parsec_limit} parsecs of Sol.")
        # Save as new json
        with open(f"stars-within-{self.parsec_limit}-parsecs.json", "w", encoding="utf-8") as f:
            json.dump(sorted([s.to_json() for s in self.stars], key=itemgetter("dist")), f, indent=2)

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

    def nearby_stars(self, origin: Star) -> list[tuple[float, Star]]:
        """
        Get the stars with <parsecs> parsecs from the star with the proper name, <star>

        Args:
            origin:
        """
        nearby_stars = []
        if origin.proper == "Sol":
            # distance from Sol is a field in the database
            for star in self.stars:
                if star.proper == "Sol":
                    continue

                if star.dist <= self.jump_parsecs:
                    nearby_stars.append((star.dist, star))

            return nearby_stars

        for star in self.stars:
            if origin.name == star.name:
                continue

            distance = self.distance(origin, star)
            if distance <= self.jump_parsecs:
                nearby_stars.append((distance, star))

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
        nearby_stars = self.nearby_stars(current_star)

        if not nearby_stars:
            all_paths.append(path)
            return

        for distance, nearby_star in nearby_stars:
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
            print(json.dumps([s.name for s in path], indent=2))

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

    for p in range(10):
        target_name = random.choice([s.name for s in star_paths.stars if s.name != "Sol"])
        star_paths.star_path("Sol", target_name)
