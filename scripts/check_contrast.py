"""Check the text and background pairs used in static/styles.css. Exit 1 if any pair is under 4.5:1."""


def channel(value):
    value = value / 255
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def luminance(hex_color):
    hex_color = hex_color.lstrip("#")
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)


def ratio(foreground, background):
    lighter = max(luminance(foreground), luminance(background))
    darker = min(luminance(foreground), luminance(background))
    return (lighter + 0.05) / (darker + 0.05)


PAIRS = [
    ("text on page", "#12202B", "#F3F7FB"),
    ("text on card", "#12202B", "#FFFFFF"),
    ("text on selected card", "#12202B", "#E7F6EC"),
    ("white on primary button", "#FFFFFF", "#1B7A3E"),
    ("green icon on card", "#1B7A3E", "#FFFFFF"),
    ("green icon on page", "#1B7A3E", "#F3F7FB"),
    ("verified badge", "#1B7A3E", "#E7F6EC"),
    ("link on card", "#2563EB", "#FFFFFF"),
    ("link on page", "#2563EB", "#F3F7FB"),
    ("link on topic tile", "#2563EB", "#F3F7FB"),
    ("partly confirmed badge", "#2563EB", "#E8F1FF"),
    ("blue icon on selected card", "#2563EB", "#E7F6EC"),
    ("not yet verified badge", "#6A3B00", "#FFF6DE"),
    ("out of scope badge", "#12202B", "#E8EDF2"),
]


def main():
    failed = 0
    for name, foreground, background in PAIRS:
        value = ratio(foreground, background)
        ok = value >= 4.5
        if not ok:
            failed += 1
        print(f"{name}: {foreground} on {background} = {value:.2f} {'PASS' if ok else 'FAIL'}")
    border = ratio("#5C6B7A", "#FFFFFF")
    print(f"input border: #5C6B7A on #FFFFFF = {border:.2f} {'PASS' if border >= 3 else 'FAIL'} for a 3:1 boundary")
    if border < 3:
        failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
