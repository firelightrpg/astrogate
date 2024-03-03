"""
Traveller-esque system generation for nearby stars
"""

import random
import re


def roll_dice(dice: str) -> int:
    """
    Roll dice for a simple dice string like 2d6 or 3d8+2

    Args:
        dice:

    Returns:
        total
    """
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice)
    if not match:
        raise ValueError("Invalid dice roll format. Use 'NdM' or 'NdM+/-X'.")

    number = int(match.group(1))
    sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    return sum(random.randint(1, sides) for _ in range(number)) + modifier


def orbits(luminosity_class: str) -> list[str]:
    """
    Get a random number of orbits, based on star's luminosity class (size).

    Orbits are classes as inner, habitable and outer

    Args:
        luminosity_class

    Returns:
        A list of orbit types, inner, habitable and outer
            None for empty, inside star or too close to star
    """
    if luminosity_class in ("Ia", "II"):
        modifier = "+8"
    elif luminosity_class == "III":
        modifier = "+4"
    else:
        modifier = ""

    maximum_orbits = roll_dice(f"2d6{modifier}")
    for orbit in range(1, maximum_orbits + 1):
        pass


def luminosity_to_class(luminosity):
    if luminosity >= 10000:
        return "Ia"
    elif luminosity >= 1000:
        return "II"
    elif luminosity >= 100:
        return "III"
    elif luminosity >= 30:
        return "IV"
    elif luminosity >= 1:
        return "V"
    elif luminosity >= 0.1:
        return "VI"
    else:
        return "VII"
