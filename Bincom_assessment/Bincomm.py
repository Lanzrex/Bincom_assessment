"""
  BINCOM ICT - STAFF DRESS COLOUR ANALYSIS
"""

import re
import random
import math
from collections import Counter

# RAW DATA  (parsed from the HTML page)
RAW_DATA = {
    "MONDAY":    "GREEN, YELLOW, GREEN, BROWN, BLUE, PINK, BLUE, YELLOW, ORANGE, CREAM, ORANGE, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, GREEN",
    "TUESDAY":   "ARSH, BROWN, GREEN, BROWN, BLUE, BLUE, BLEW, PINK, PINK, ORANGE, ORANGE, RED, WHITE, BLUE, WHITE, WHITE, BLUE, BLUE, BLUE",
    "WEDNESDAY": "GREEN, YELLOW, GREEN, BROWN, BLUE, PINK, RED, YELLOW, ORANGE, RED, ORANGE, RED, BLUE, BLUE, WHITE, BLUE, BLUE, WHITE, WHITE",
    "THURSDAY":  "BLUE, BLUE, GREEN, WHITE, BLUE, BROWN, PINK, YELLOW, ORANGE, CREAM, ORANGE, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, GREEN",
    "FRIDAY":    "GREEN, WHITE, GREEN, BROWN, BLUE, BLUE, BLACK, WHITE, ORANGE, RED, RED, RED, WHITE, BLUE, WHITE, BLUE, BLUE, BLUE, WHITE",
}

# HELPER: parse & normalise colours

NORMALISE = {"BLEW": "BLUE", "ARSH": "ASH"}   # obvious typo / variant fixes

def parse_colours(raw: dict) -> list:
    """Return a flat list of normalised colour strings."""
    colours = []
    for row in raw.values():
        for colour in re.split(r",\s*", row.strip()):
            c = colour.strip().upper()
            c = NORMALISE.get(c, c)
            if c:
                colours.append(c)
    return colours

ALL_COLOURS  = parse_colours(RAW_DATA)
FREQ         = Counter(ALL_COLOURS)          # {colour: count}
SORTED_FREQ  = sorted(FREQ.items(), key=lambda x: x[1], reverse=True)
TOTAL        = len(ALL_COLOURS)


# Q1 – MEAN COLOUR
def mean_colour(freq: Counter) -> str:
    """
    'Mean' for categorical data = colour whose frequency is
    closest to the arithmetic mean of all frequencies.
    """
    mean_freq = sum(freq.values()) / len(freq)
    mean_col  = min(freq, key=lambda c: abs(freq[c] - mean_freq))
    return mean_col, mean_freq


# Q2 – MODE (most worn colour)
def mode_colour(freq: Counter) -> tuple:
    most_common = freq.most_common(1)[0]
    return most_common   # (colour, count)


# Q3 – MEDIAN COLOUR
def median_colour(all_colours: list) -> str:
    """
    Sort the full colour list alphabetically (treats colours as
    ordinal by name) and return the middle element.
    """
    sorted_colours = sorted(all_colours)
    mid = len(sorted_colours) // 2
    if len(sorted_colours) % 2 == 0:
        return sorted_colours[mid - 1], sorted_colours[mid]  # two midpoints
    return sorted_colours[mid], None


# Q4 BONUS – VARIANCE OF COLOUR FREQUENCIES
def variance_of_colours(freq: Counter) -> float:
    counts = list(freq.values())
    mean   = sum(counts) / len(counts)
    var    = sum((x - mean) ** 2 for x in counts) / len(counts)
    return var, mean


# Q5 BONUS – PROBABILITY OF RED
def probability_of_red(freq: Counter, total: int) -> float:
    return freq.get("RED", 0) / total


# Q6 – SAVE TO POSTGRESQL
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "bincom_db",
    "user":     "postgres",
    "password": "your_password",
}

def save_to_postgresql(freq: Counter) -> None:
    """
    Saves colour frequencies to a PostgreSQL table.
    Requires:  pip install psycopg2-binary
    Update DB_CONFIG above with your credentials.
    """
    try:
        import psycopg2

        conn = psycopg2.connect(**DB_CONFIG)
        cur  = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS colour_frequency (
                id        SERIAL PRIMARY KEY,
                colour    VARCHAR(50) UNIQUE NOT NULL,
                frequency INTEGER NOT NULL
            );
        """)

        for colour, count in freq.items():
            cur.execute("""
                INSERT INTO colour_frequency (colour, frequency)
                VALUES (%s, %s)
                ON CONFLICT (colour) DO UPDATE SET frequency = EXCLUDED.frequency;
            """, (colour, count))

        conn.commit()
        cur.close()
        conn.close()
        print("  ✔  Colour frequencies saved to PostgreSQL successfully.")
    except ImportError:
        print("  ✘  psycopg2 not installed. Run: pip install psycopg2-binary")
    except Exception as e:
        print(f"  ✘  PostgreSQL error: {e}")


# Q7 BONUS – RECURSIVE BINARY SEARCH
def recursive_binary_search(arr: list, target: int,
                             low: int = 0, high: int = None) -> int:
    """
    Returns the index of target in the sorted list arr,
    or -1 if not found.
    """
    if high is None:
        high = len(arr) - 1

    if low > high:          # base case: not found
        return -1

    mid = (low + high) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return recursive_binary_search(arr, target, mid + 1, high)
    else:
        return recursive_binary_search(arr, target, low, mid - 1)

def demo_recursive_search() -> None:
    numbers = sorted(random.sample(range(1, 200), 20))
    print(f"\n  Sorted list: {numbers}")
    try:
        target = int(input("  Enter a number to search for: "))
        idx = recursive_binary_search(numbers, target)
        if idx != -1:
            print(f"  ✔  {target} found at index {idx}.")
        else:
            print(f"  ✘  {target} not found in the list.")
    except ValueError:
        print("  ✘  Invalid input – please enter an integer.")


# Q8 – RANDOM 4-BIT BINARY → BASE 10
def random_binary_to_decimal() -> tuple:
    """Generate a random 4-digit binary number and convert to base 10."""
    bits      = [random.randint(0, 1) for _ in range(4)]
    binary_str = "".join(map(str, bits))
    decimal   = int(binary_str, 2)          # built-in base conversion
    return binary_str, decimal


# Q9 – SUM OF FIRST 50 FIBONACCI NUMBERS
def fibonacci_sum(n: int = 50) -> tuple:
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence, sum(sequence)

# MAIN – PRINT ALL RESULTS
def main():
    sep = "=" * 62

    print(f"\n{sep}")
    print("  BINCOM ICT – DRESS COLOUR ANALYSIS")
    print(sep)

    # frequency table 
    print("\n📊 COLOUR FREQUENCY TABLE:")
    print(f"  {'Colour':<12} {'Frequency':>10}")
    print("  " + "-" * 24)
    for colour, count in SORTED_FREQ:
        print(f"  {colour:<12} {count:>10}")
    print(f"  {'TOTAL':<12} {TOTAL:>10}")

    # Q1: mean
    m_col, m_freq = mean_colour(FREQ)
    print(f"\n{'─'*62}")
    print(f"Q1 │ MEAN COLOUR")
    print(f"   │ Average frequency across all colours = {m_freq:.2f}")
    print(f"   │ Colour closest to the mean ➜  {m_col}  (worn {FREQ[m_col]} times)")

    # Q2: mode
    mode_col, mode_cnt = mode_colour(FREQ)
    print(f"\n{'─'*62}")
    print(f"Q2 │ MOST WORN COLOUR (Mode)")
    print(f"   │ ➜  {mode_col}  (worn {mode_cnt} times)")

    # Q3: median 
    med1, med2 = median_colour(ALL_COLOURS)
    print(f"\n{'─'*62}")
    print(f"Q3 │ MEDIAN COLOUR")
    if med2:
        print(f"   │ Two middle values ➜  {med1}  &  {med2}")
    else:
        print(f"   │ ➜  {med1}")

    # Q4: variance 
    var, avg = variance_of_colours(FREQ)
    print(f"\n{'─'*62}")
    print(f"Q4 │ VARIANCE OF COLOUR FREQUENCIES  (BONUS)")
    print(f"   │ Mean frequency = {avg:.4f}")
    print(f"   │ Variance       = {var:.4f}")
    print(f"   │ Std deviation  = {math.sqrt(var):.4f}")

    # Q5: probability of red 
    p_red = probability_of_red(FREQ, TOTAL)
    print(f"\n{'─'*62}")
    print(f"Q5 │ PROBABILITY OF PICKING RED AT RANDOM  (BONUS)")
    print(f"   │ Red count = {FREQ.get('RED', 0)},  Total = {TOTAL}")
    print(f"   │ P(Red) = {FREQ.get('RED', 0)}/{TOTAL} = {p_red:.4f}  ({p_red*100:.2f}%)")

    # Q6: PostgreSQL
    print(f"\n{'─'*62}")
    print(f"Q6 │ SAVE TO POSTGRESQL")
    print(f"   │ Attempting to save to database …")
    save_to_postgresql(FREQ)

    # Q7: recursive search
    print(f"\n{'─'*62}")
    print(f"Q7 │ RECURSIVE BINARY SEARCH  (BONUS)")
    demo_recursive_search()

    # Q8: binary → decimal
    print(f"\n{'─'*62}")
    print(f"Q8 │ RANDOM 4-BIT BINARY → DECIMAL")
    for i in range(1, 4):          # show 3 examples
        b, d = random_binary_to_decimal()
        print(f"   │ Run {i}: binary = {b}  →  decimal = {d}")

    # Q9: fibonacci sum
    seq, total_fib = fibonacci_sum(50)
    print(f"\n{'─'*62}")
    print(f"Q9 │ SUM OF FIRST 50 FIBONACCI NUMBERS")
    print(f"   │ Sequence (first 10): {seq[:10]} …")
    print(f"   │ Sum of all 50  ➜  {total_fib}")

    print(f"\n{sep}\n")


if __name__ == "__main__":
    main()