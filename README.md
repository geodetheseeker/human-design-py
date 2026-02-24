# human-design-py

An open-source, accurate Human Design chart calculator in Python.

Built by a Projector. No gatekeeping.

## What it calculates
- Type (Projector, Generator, Manifesting Generator, Manifestor, Reflector)
- Profile (e.g. 2/4)
- Inner Authority
- Defined and Open Centers
- All active gates with lines
- Personality (conscious) and Design (unconscious) planetary positions
- Correct design date via solar arc (88° before birth Sun)

## Requirements
pip3 install pyswisseph

## Usage
from chart import calculate_chart, print_chart

result = calculate_chart(
    birth_year=1988,
    birth_month=10,
    birth_day=9,
    birth_hour=5,
    birth_minute=30,
    utc_offset=-7
)

print_chart(result, "Your Name")

## Accuracy
Verified against bodygraph.io. Gate sequence sourced from barneyandflow.com/gate-zodiac-degrees.

## Contributing
PRs welcome. This is meant to be a foundation.

## License
MIT
