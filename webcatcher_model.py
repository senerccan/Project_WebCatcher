"""The rules behind Web Catcher's call, shared with senergunsel.com/projects/web-catcher/.

The JavaScript copy on the site runs the same steps in the same order, so both give the
same numbers. Every number here is illustrative: none of it is Vans data or anyone's real sales.
"""

import copy
import math

LINE = 50  # momentum and fit both need 50 out of 100 to count as high

SHOES = [
    {"key": "oldskool", "name": "Old Skool", "look": "Low-top skate shoe with the side stripe, in suede and canvas"},
    {"key": "authentic", "name": "Authentic", "look": "The original low-profile canvas lace-up"},
    {"key": "slipon", "name": "Slip-On", "look": "Laceless canvas, often in checkerboard"},
]

TRAITS = [
    {"key": "price", "name": "Price", "q": "Would the trend's buyers pay our price?"},
    {"key": "function", "name": "Function", "q": "Is it worn for the same things?"},
    {"key": "shape", "name": "Shape", "q": "Slim or chunky, low or high: the same silhouette?"},
    {"key": "material", "name": "Material", "q": "Suede, leather, canvas or mesh, like the trend?"},
    {"key": "color", "name": "Color", "q": "In the colors the trend sells in?"},
    {"key": "pattern", "name": "Pattern", "q": "Stripes, panels and prints like the trend's?"},
]

# How long the trend lasts decides what can reach the shelf before it ends.
# `product` is how much of the product lever lands in time.
WINDOWS = {
    "short": {"name": "Under 6 months", "product": 0.0, "note": "Too short for product work to land. The product lever does nothing here."},
    "medium": {"name": "6 to 12 months", "product": 0.5, "note": "New colors and materials can land in time, a new shoe can't. The product lever works at half strength."},
    "long": {"name": "Over a year", "product": 1.0, "note": "Long enough to develop the shoe. The product lever works at full strength."},
}

LEVERS = [
    {"key": "product", "name": "Product", "note": "New materials, colors and patterns. Moves Material, Color and Pattern."},
    {"key": "marketing", "name": "Marketing", "note": "Shows people what the shoe is for. Moves Function."},
    {"key": "money", "name": "Money", "note": "Sharper prices and deeper stock. Moves Price."},
]
LEVEL_WORDS = ["Pull back", "Less", "As usual", "More", "All in"]
BUZZ_WORDS = ["Disliked", "Cool", "Mixed", "Warm", "Loved"]
SIZE_WORDS = ["Niche", "Small", "Mid-size", "Big", "Mainstream"]
WEIGHTS = {"growth": 50, "buzz": 30, "size": 20}
CALLS = {"back": "Back it", "test": "Test small", "hold": "Hold", "pass": "Pass"}
MAX_TRENDS = 8


def round_half_up(x):
    """Halves round up, as in JavaScript (Python's round() rounds halves to even)."""
    return math.floor(x + 0.5)


def clamp(x, lo, hi):
    return min(hi, max(lo, x))


def ratings(price, function, shape, material, color, pattern):
    return {"price": price, "function": function, "shape": shape, "material": material, "color": color, "pattern": pattern}


# The five trends the tool was built with, as they looked in 2024.
EXAMPLES = [
    {"key": "samba", "name": "Adidas Samba", "look": "Slim terrace shoe in leather and suede, gum sole",
     "growth": 35, "buzz": 4, "size": 4, "window": "medium",
     "ratings": {"oldskool": ratings(4, 3, 2, 3, 3, 2), "authentic": ratings(4, 3, 4, 1, 3, 1), "slipon": ratings(4, 2, 3, 1, 2, 1)}},
    {"key": "af1", "name": "Nike Air Force 1", "look": "Chunky white leather court shoe",
     "growth": -40, "buzz": 3, "size": 5, "window": "medium",
     "ratings": {"oldskool": ratings(4, 4, 3, 3, 4, 2), "authentic": ratings(4, 3, 2, 1, 3, 3), "slipon": ratings(4, 3, 2, 1, 3, 2)}},
    {"key": "stansmith", "name": "Adidas Stan Smith", "look": "Minimal white leather tennis shoe",
     "growth": -15, "buzz": 2, "size": 3, "window": "short",
     "ratings": {"oldskool": ratings(4, 3, 3, 2, 3, 1), "authentic": ratings(4, 3, 4, 1, 4, 5), "slipon": ratings(4, 3, 3, 1, 3, 3)}},
    {"key": "nb993", "name": "New Balance 993", "look": "Chunky grey “dad” runner in mesh and suede",
     "growth": -35, "buzz": 2, "size": 2, "window": "short",
     "ratings": {"oldskool": ratings(3, 2, 1, 3, 2, 2), "authentic": ratings(3, 2, 1, 1, 2, 1), "slipon": ratings(3, 2, 1, 1, 2, 1)}},
    {"key": "dunk", "name": "Nike Dunk", "look": "Retro basketball low in two-tone leather",
     "growth": -45, "buzz": 3, "size": 4, "window": "short",
     "ratings": {"oldskool": ratings(4, 4, 3, 3, 3, 2), "authentic": ratings(4, 3, 2, 1, 3, 2), "slipon": ratings(4, 2, 2, 1, 3, 2)}},
]


def usual():
    return {"product": 3, "marketing": 3, "money": 3}


def defaults():
    trends = []
    for e in EXAMPLES:
        t = copy.deepcopy(e)
        t.update({"custom": False, "levers": usual()})
        trends.append(t)
    return trends


def new_trend(n):
    mid = lambda: ratings(3, 3, 3, 3, 3, 3)  # noqa: E731
    return {"key": f"own{n}", "name": "Your trend" if n == 1 else f"Your trend {n}", "look": "",
            "custom": True, "growth": 0, "buzz": 3, "size": 2, "window": "medium",
            "ratings": {"oldskool": mid(), "authentic": mid(), "slipon": mid()}, "levers": usual()}


def momentum(t):
    """How hot the trend is, 0 to 100: three signals on the same scale, then weighted."""
    g = clamp(t["growth"] + 50, 0, 100)  # -50% -> 0, +50% -> 100
    b = (t["buzz"] - 1) * 25
    s = (t["size"] - 1) * 25
    total = (WEIGHTS["growth"] * g + WEIGHTS["buzz"] * b + WEIGHTS["size"] * s) / 100
    parts = {"growth": WEIGHTS["growth"] * g / 100, "buzz": WEIGHTS["buzz"] * b / 100, "size": WEIGHTS["size"] * s / 100}
    return round_half_up(total), parts


def lever_shift(t, trait):
    """Each lever step moves the traits it touches by half a point. Nothing moves Shape fast."""
    lv = t["levers"]
    if trait == "price":
        return 0.5 * (lv["money"] - 3)
    if trait == "function":
        return 0.5 * (lv["marketing"] - 3)
    if trait in ("material", "color", "pattern"):
        return 0.5 * (lv["product"] - 3) * WINDOWS[t["window"]]["product"]
    return 0.0


def adjusted_ratings(t, shoe, with_levers=True):
    r = t["ratings"][shoe]
    return [clamp(r[tr["key"]] + (lever_shift(t, tr["key"]) if with_levers else 0), 1, 5) for tr in TRAITS]


def fit_score(t, shoe, with_levers=True):
    """How close a shoe is to the trend, 0 to 100: the average of its six ratings."""
    total = 0
    for v in adjusted_ratings(t, shoe, with_levers):
        total += v
    return round_half_up(((total - len(TRAITS)) * 25) / len(TRAITS))


def best_shoe(t, with_levers=True):
    best, top = SHOES[0]["key"], -1
    for s in SHOES:
        f = fit_score(t, s["key"], with_levers)
        if f > top:
            best, top = s["key"], f
    return best, top


def call_for(mom, fit):
    if mom >= LINE:
        return "back" if fit >= LINE else "test"
    return "hold" if fit >= LINE else "pass"


def bet_size(levers):
    up = sum(max(0, levers[l["key"]] - 3) for l in LEVERS)
    down = sum(max(0, 3 - levers[l["key"]]) for l in LEVERS)
    if up == 0:
        return "Pulling back" if down else "As usual"
    if up <= 2:
        return "A small bet"
    if up <= 4:
        return "A real bet"
    return "Everything in"


def shoe_name(key):
    return next(s["name"] for s in SHOES if s["key"] == key)


def play_for(call, window, shoe):
    the = "the " + shoe_name(shoe)
    if call == "back":
        if window == "short":
            return f"Back {the} now with what's already made: marketing, the colors in stock and the front of the store. The trend won't last long enough for new product to land."
        if window == "long":
            return f"Back {the} and develop it. The trend should last long enough for a new version to land."
        return f"Back {the}. New colors and materials on it can land while the trend is still hot."
    if call == "test":
        if window == "short":
            return "Ride it with marketing, or let it pass. The trend is hot, but none of the core shoes is close, and it won't last long enough to close the gap."
        if window == "long":
            return "Write a brief for a new shoe. The trend is hot and lasting, and none of the core shoes is close."
        return f"Test a small run or a collab on {the} before betting the line on it."
    if call == "hold":
        return f"Keep {the} as it is. It already fits, but the trend isn't hot enough to earn extra spend."
    return "Let it pass. The trend isn't hot and none of the core shoes is close."


def evaluate(t):
    mom, parts = momentum(t)
    fits = {s["key"]: {"base": fit_score(t, s["key"], False), "now": fit_score(t, s["key"], True)} for s in SHOES}
    shoe, fit = best_shoe(t, True)
    base_shoe, base_fit = best_shoe(t, False)
    call = call_for(mom, fit)
    return {"key": t["key"], "momentum": mom, "parts": parts, "fits": fits, "shoe": shoe, "fit": fit,
            "base_shoe": base_shoe, "base_fit": base_fit, "call": call, "base_call": call_for(mom, base_fit),
            "play": play_for(call, t["window"], shoe), "bet": bet_size(t["levers"])}


def line_note(v):
    if v == LINE:
        return "right on the line"
    n = abs(v - LINE)
    return f"{n} point{'s' if n != 1 else ''} {'above' if v > LINE else 'below'} the line"


def cheapest_backing(t):
    """The smallest lever move from where the levers are now that turns the call into Back it.

    Returns {"levers", "steps", "shoe", "fit"} or None. Only moves up count (pulling a lever back never
    helps the fit), and no lever moves momentum, so a trend that isn't hot has no answer. Ties go to
    fewer steps, then fewer levers touched, then the move that leans least on product (the slowest
    lever), then marketing, then money.
    """
    mom, _ = momentum(t)
    if mom < LINE:
        return None
    base = t["levers"]
    best = None
    for p in range(base["product"], 6):
        for mk in range(base["marketing"], 6):
            for mo in range(base["money"], 6):
                lv = {"product": p, "marketing": mk, "money": mo}
                shoe, fit = best_shoe(dict(t, levers=lv), True)
                if call_for(mom, fit) != "back":
                    continue
                steps = (p - base["product"]) + (mk - base["marketing"]) + (mo - base["money"])
                touched = int(p > base["product"]) + int(mk > base["marketing"]) + int(mo > base["money"])
                rank = (steps, touched, p, mk, mo)
                if best is None or rank < best[0]:
                    best = (rank, {"levers": lv, "steps": steps, "shoe": shoe, "fit": fit})
    return best[1] if best else None


def coach(t):
    """One line on what would change the call, for the call card."""
    e = evaluate(t)
    if e["call"] == "back":
        return "Both scores clear the line."
    if e["call"] == "test":
        move = cheapest_backing(t)
        if move is None:
            _, top = best_shoe(dict(t, levers={"product": 5, "marketing": 5, "money": 5}), True)
            return f"Even with every lever all in, the best shoe only reaches fit {top}."
        parts = [f"{lv['name'].lower()} to {LEVEL_WORDS[move['levers'][lv['key']] - 1]}"
                 for lv in LEVERS if move["levers"][lv["key"]] > t["levers"][lv["key"]]]
        return f"Cheapest way to Back it from here: {' and '.join(parts)}. That takes the {shoe_name(move['shoe'])} to fit {move['fit']}."
    if e["call"] == "hold":
        n = LINE - e["momentum"]
        return f"Momentum is {n} point{'s' if n != 1 else ''} short of hot, and the levers don't change that: growth, buzz and size do."
    return "Neither score is near enough. The levers move the fit, not the heat."

