#!/usr/bin/env python3
"""
HumanDesignHD - Open source Human Design chart calculator
Built in English, for everyone.
"""

import swisseph as swe
from datetime import datetime, timezone
import math

# Set ephemeris path (uses built-in moshier ephemeris - no files needed)
swe.set_ephe_path('')

# ─────────────────────────────────────────────
# GATE MAP: ecliptic degree → Human Design gate
# Each gate spans 5.625 degrees (360 / 64 gates)
# ─────────────────────────────────────────────

# Gate sequence in ecliptic degree order starting from 28°15' Pisces (358.25°)
# Source: barneyandflow.com/gate-zodiac-degrees
GATE_SEQUENCE = [
    25, 17, 21, 51, 42, 3,   # Aries
    27, 24, 2,  23, 8,  20,  # Taurus
    16, 35, 45, 12, 15, 52,  # Gemini
    39, 53, 62, 56, 31, 33,  # Cancer
    7,  4,  29, 59, 40, 64,  # Leo
    47, 6,  46, 18, 48, 57,  # Virgo+Libra
    32, 50, 28, 44, 1,  43,  # Libra+Scorpio
    14, 34, 9,  5,  26, 11,  # Scorpio+Sag
    10, 58, 38, 54, 61, 60,  # Cap
    41, 19, 13, 49, 30, 55,  # Aquarius
    37, 63, 22, 36            # Pisces
]

HD_START_DEGREE = 358.25  # 28°15' Pisces

GATE_NAMES = {
    1: "The Creative", 2: "The Receptive", 3: "Ordering",
    4: "Formulization", 5: "Fixed Rhythms", 6: "Friction",
    7: "The Role of the Self", 8: "Holding Together", 9: "Focus",
    10: "Behavior of the Self", 11: "Ideas", 12: "Caution",
    13: "The Listener", 14: "Power Skills", 15: "Extremes",
    16: "Skills", 17: "Opinion", 18: "Correction",
    19: "Wanting", 20: "Now", 21: "The Hunter/Huntress",
    22: "Openness", 23: "Assimilation", 24: "Rationalization",
    25: "Spirit of the Self", 26: "The Egoist", 27: "Caring",
    28: "The Game Player", 29: "Saying Yes", 30: "Feelings",
    31: "Influence", 32: "Continuity", 33: "Privacy",
    34: "Power", 35: "Change", 36: "Crisis",
    37: "Friendship", 38: "Opposition", 39: "Provocation",
    40: "Aloneness", 41: "Contraction", 42: "Growth",
    43: "Insight", 44: "Coming to Meet", 45: "Gathering Together",
    46: "Pushing Upward", 47: "Realization", 48: "Depth",
    49: "Principles", 50: "Values", 51: "Shock",
    52: "Stillness", 53: "Development", 54: "Ambition",
    55: "Spirit", 56: "Stimulation", 57: "Intuitive Clarity",
    58: "Vitality", 59: "Sexuality", 60: "Limitation",
    61: "Mystery", 62: "Detail", 63: "Doubt", 64: "Confusion"
}

# Channels: pairs of gates that connect centers
CHANNELS = [
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15),
    (6, 59), (7, 31), (9, 52), (10, 20), (11, 56),
    (12, 22), (13, 33), (16, 48), (17, 62), (18, 58),
    (19, 49), (20, 34), (20, 57), (21, 45), (23, 43),
    (24, 61), (25, 51), (26, 44), (27, 50), (28, 38),
    (29, 46), (30, 41), (32, 54), (34, 57), (35, 36),
    (37, 40), (39, 55), (42, 53), (47, 64)
]

# Centers and which gates belong to them
CENTERS = {
    "Head":     [61, 63, 64],
    "Ajna":     [4, 11, 17, 24, 43, 47],
    "Throat":   [8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62],
    "Self":     [1, 2, 7, 10, 13, 15, 25, 46],
    "Sacral":   [3, 5, 9, 14, 27, 29, 34, 42, 59],
    "Root":     [19, 28, 38, 39, 41, 52, 53, 54, 58, 60],
    "Spleen":   [18, 28, 32, 44, 48, 50, 57],
    "Solar Plexus": [6, 22, 30, 36, 37, 49, 55],
    "Heart":    [21, 26, 40, 51]
}

# Centers connected by each channel (for type determination)
CHANNEL_CENTERS = {
    (1, 8):   ("Self", "Throat"),
    (2, 14):  ("Self", "Sacral"),
    (3, 60):  ("Sacral", "Root"),
    (4, 63):  ("Ajna", "Head"),
    (5, 15):  ("Sacral", "Self"),
    (6, 59):  ("Solar Plexus", "Sacral"),
    (7, 31):  ("Self", "Throat"),
    (9, 52):  ("Sacral", "Root"),
    (10, 20): ("Self", "Throat"),
    (11, 56): ("Ajna", "Throat"),
    (12, 22): ("Throat", "Solar Plexus"),
    (13, 33): ("Self", "Throat"),
    (16, 48): ("Throat", "Spleen"),
    (17, 62): ("Ajna", "Throat"),
    (18, 58): ("Spleen", "Root"),
    (19, 49): ("Root", "Solar Plexus"),
    (20, 34): ("Throat", "Sacral"),
    (20, 57): ("Throat", "Spleen"),
    (21, 45): ("Heart", "Throat"),
    (23, 43): ("Throat", "Ajna"),
    (24, 61): ("Ajna", "Head"),
    (25, 51): ("Self", "Heart"),
    (26, 44): ("Heart", "Spleen"),
    (27, 50): ("Sacral", "Spleen"),
    (28, 38): ("Spleen", "Root"),
    (29, 46): ("Sacral", "Self"),
    (30, 41): ("Solar Plexus", "Root"),
    (32, 54): ("Spleen", "Root"),
    (34, 57): ("Sacral", "Spleen"),
    (35, 36): ("Throat", "Solar Plexus"),
    (37, 40): ("Solar Plexus", "Heart"),
    (39, 55): ("Root", "Solar Plexus"),
    (42, 53): ("Sacral", "Root"),
    (47, 64): ("Ajna", "Head")
}

def degree_to_gate_line(degree):
    """Convert ecliptic degree to HD gate and line."""
    gate_size = 360 / 64
    line_size = gate_size / 6
    adjusted = (degree - HD_START_DEGREE) % 360
    index = int(adjusted / gate_size)
    line = int((adjusted % gate_size) / line_size) + 1
    return GATE_SEQUENCE[index], line

def get_planet_positions(jd):
    """Get gate/line for all HD-relevant planets."""
    planets = {
        "Sun":     swe.SUN,
        "Earth":   None,  # opposite of Sun
        "Moon":    swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus":   swe.VENUS,
        "Mars":    swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn":  swe.SATURN,
        "Uranus":  swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto":   swe.PLUTO,
        "N.Node":  swe.TRUE_NODE,
    }
    
    results = {}
    for name, planet_id in planets.items():
        if name == "Earth":
            sun_deg = swe.calc_ut(jd, swe.SUN)[0][0]
            earth_deg = (sun_deg + 180) % 360
            gate, line = degree_to_gate_line(earth_deg)
            results[name] = {"degree": earth_deg, "gate": gate, "line": line}
        else:
            pos = swe.calc_ut(jd, planet_id)[0][0]
            gate, line = degree_to_gate_line(pos)
            results[name] = {"degree": pos, "gate": gate, "line": line}
    
    # South Node = opposite of North Node
    nn_deg = results["N.Node"]["degree"]
    sn_deg = (nn_deg + 180) % 360
    gate, line = degree_to_gate_line(sn_deg)
    results["S.Node"] = {"degree": sn_deg, "gate": gate, "line": line}
    
    return results

def get_defined_centers(all_gates):
    """Determine which centers are defined based on active channels."""
    defined = set()
    gate_set = set(all_gates)
    
    for g1, g2 in CHANNELS:
        if g1 in gate_set and g2 in gate_set:
            if (g1, g2) in CHANNEL_CENTERS:
                c1, c2 = CHANNEL_CENTERS[(g1, g2)]
                defined.add(c1)
                defined.add(c2)
    return defined

def determine_type(defined_centers):
    """Determine HD type from defined centers."""
    has_sacral = "Sacral" in defined_centers
    has_throat = "Throat" in defined_centers
    has_motor = any(c in defined_centers for c in ["Sacral", "Heart", "Solar Plexus", "Root"])
    motor_to_throat = False
    
    # Check if any motor is connected to throat
    motor_centers = {"Sacral", "Heart", "Solar Plexus", "Root"}
    if has_throat:
        for g1, g2 in CHANNELS:
            if (g1, g2) in CHANNEL_CENTERS:
                c1, c2 = CHANNEL_CENTERS[(g1, g2)]
                if (c1 in motor_centers and c2 == "Throat") or \
                   (c2 in motor_centers and c1 == "Throat"):
                    motor_to_throat = True
    
    if not defined_centers:
        return "Reflector"
    elif has_sacral and motor_to_throat:
        return "Manifesting Generator"
    elif has_sacral:
        return "Generator"
    elif motor_to_throat:
        return "Manifestor"
    else:
        return "Projector"

def determine_authority(defined_centers):
    """Determine inner authority from defined centers."""
    priority = [
        ("Solar Plexus", "Emotional"),
        ("Sacral", "Sacral"),
        ("Spleen", "Splenic"),
        ("Heart", "Ego"),
        ("Self", "Self-Projected"),
    ]
    for center, authority in priority:
        if center in defined_centers:
            return authority
    return "Mental/Outer"

def calculate_chart(birth_year, birth_month, birth_day, birth_hour, birth_minute, utc_offset):
    """Calculate a complete Human Design chart."""
    
    # Convert to UTC
    utc_hour = birth_hour - utc_offset
    jd_personality = swe.julday(birth_year, birth_month, birth_day, 
                                 utc_hour + birth_minute/60)
    
    # Design date: Sun position 88 degrees earlier (~88 days before birth)
    # Design date: find exact moment Sun was 88 degrees behind personality Sun
    # Using binary search for solar arc (more accurate than 88 days)
    p_sun_deg = swe.calc_ut(jd_personality, swe.SUN)[0][0]
    target_design_deg = (p_sun_deg - 88) % 360
    jd_low = jd_personality - 100
    jd_high = jd_personality - 80
    for _ in range(50):
         jd_mid = (jd_low + jd_high) / 2
         sun_deg = swe.calc_ut(jd_mid, swe.SUN)[0][0]
         diff = (sun_deg - target_design_deg + 180) % 360 - 180
         if abs(diff) < 0.0001:
            break
         if diff > 0:
            jd_high = jd_mid
         else:
            jd_low = jd_mid
            jd_design = jd_mid
    
    # Get personality (conscious) positions
    personality = get_planet_positions(jd_personality)
    
    # Get design (unconscious) positions  
    design = get_planet_positions(jd_design)
    
    # Collect all active gates
    all_gates = set()
    for p in personality.values():
        all_gates.add(p["gate"])
    for p in design.values():
        all_gates.add(p["gate"])
    
    # Determine defined centers
    defined_centers = get_defined_centers(all_gates)
    
    # Profile: line of personality Sun / line of design Sun
    p_sun_line = personality["Sun"]["line"]
    d_sun_line = design["Sun"]["line"]
    profile = f"{p_sun_line}/{d_sun_line}"
    
    # Type and authority
    hd_type = determine_type(defined_centers)
    authority = determine_authority(defined_centers)
    
    return {
        "type": hd_type,
        "profile": profile,
        "authority": authority,
        "defined_centers": sorted(defined_centers),
        "undefined_centers": sorted(set(CENTERS.keys()) - defined_centers),
        "personality": personality,
        "design": design,
        "all_active_gates": sorted(all_gates)
    }

def print_chart(result, name=""):
    """Pretty print a Human Design chart."""
    print(f"\n{'='*50}")
    if name:
        print(f"  Human Design Chart: {name}")
    print(f"{'='*50}")
    print(f"  Type:      {result['type']}")
    print(f"  Profile:   {result['profile']}")
    print(f"  Authority: {result['authority']}")
    print(f"\n  Defined Centers:")
    for c in result['defined_centers']:
        print(f"    ✓ {c}")
    print(f"\n  Open Centers:")
    for c in result['undefined_centers']:
        print(f"    ○ {c}")
    print(f"\n  Active Gates: {result['all_active_gates']}")
    print(f"\n  Personality (Conscious) - Black:")
    for planet, data in result['personality'].items():
        print(f"    {planet:<10} Gate {data['gate']}.{data['line']}  ({data['degree']:.2f}°)")
    print(f"\n  Design (Unconscious) - Red:")
    for planet, data in result['design'].items():
        print(f"    {planet:<10} Gate {data['gate']}.{data['line']}  ({data['degree']:.2f}°)")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    # October 9, 1988, 5:30 AM Sacramento CA (PDT = UTC-7)
    result = calculate_chart(
        birth_year=1988,
        birth_month=10,
        birth_day=9,
        birth_hour=5,
        birth_minute=30,
        utc_offset=-7
    )
    print_chart(result, "Geode")