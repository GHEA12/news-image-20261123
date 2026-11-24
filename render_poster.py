#!/usr/bin/env python3
"""Draw entry.png (1024x1024): "The World in One Day", Monday 23 Nov 2026.

A broadsheet front page rendered with Pillow and the system Noto Serif
faces. The page is laid out by a small flow engine (class Sheet): every
block advances a cursor, and the whole page is re-rendered at shrinking
type scales until it fits the canvas, so the output is byte-identical on
every run. No network, no randomness, no timestamps in the file.

Usage: python3 render_poster.py [output-path]   (default: ./entry.png)
"""
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 40
CONTENT = PAGE - 2 * MARGIN

PAPER = (248, 244, 236)
INK = (24, 21, 16)
BODY = (40, 36, 28)
MUTED = (84, 78, 66)
RED = (158, 30, 30)
TINT = (238, 231, 214)
HAIR = (198, 191, 175)
GREEN = (28, 110, 58)

BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"

DATE_LINE = "Monday 23 November 2026"

LEAD_HEAD = "Ukraine\u2019s sea drones sink a Russian warship in Libya"
LEAD_BODY = (
    "President Zelensky confirmed on Monday that seven Ukrainian-made naval "
    "drones sank the Russian corvette Merkury in Benghazi harbour, destroying "
    "a Ka-27 helicopter on board, and hit the cargo ship MV Angara, which Kyiv "
    "says carried weapons for Russia. The attack, at dawn on Sunday, struck "
    "about 1,050 miles from Ukraine\u2019s coast. Libya condemned the strike, "
    "and the UN called for an independent investigation."
)

MARKET_HEAD = "Nvidia brings back Jensen Huang \u2014 and the markets roar"
MARKET_BODY = (
    "Nvidia\u2019s board reinstated Huang as chief executive on Monday, 11 days "
    "after he resigned, after President Trump intervened. Nvidia shares closed "
    "up 31.5%, their best day since 2003, adding nearly $1 trillion in value."
)
MARKET_STATS = [("NVIDIA", "+31.5%"), ("NASDAQ", "+6.5%"), ("S&P 500", "+4.7%")]

STORIES = [
    ("UKRAINE",
     "Russian strikes kill at least 15 around Kyiv",
     "Overnight strikes hit a block of flats in Dymer, killing 11 people in one "
     "building, and a supermarket in Vyshneve. Rescuers were still digging "
     "through the rubble on Monday, and the region declared a day of mourning."),
    ("EUROPE \u00b7 NATO",
     "NATO meets over Russian missiles that entered Poland",
     "NATO\u2019s council met in Brussels on Monday to discuss Russian missiles "
     "that crossed into Polish airspace on Friday during a huge barrage on "
     "Ukraine. Poland called the incursion a deliberate provocation."),
    ("ASIA",
     "Indonesia confirms 24 dead in factory fire",
     "A fire at a confectionery factory in Banten province killed at least 24 "
     "people, with about 30 still missing. The toll was confirmed on Monday; "
     "the blaze broke out on Saturday evening."),
    ("SCIENCE \u00b7 HEALTH",
     "NHS begins the world\u2019s biggest AI breast-screening trial",
     "The NHS launched the EDITH trial on Monday: nearly 700,000 women at 30 "
     "screening sites over three years will test whether AI can help spot "
     "breast cancer earlier. The first recruits joined in Cambridgeshire."),
]

BRIEFS_LEFT = [
    "Australian broadcaster Molly Meldrum dies aged 83, after a career that "
    "shaped the country\u2019s music scene for decades.",
    "Trump says Iran\u2019s drone and missile attacks reached a year high, in a "
    "statement on Monday that underlined rising Middle East tensions.",
    "Israeli opposition leader Gadi Eisenkot calls West Bank settler attacks "
    "\u2018Jewish terrorism\u2019, as Israel investigates fires in the West Bank.",
]
BRIEFS_RIGHT = [
    "Drone strikes hit homes and a United Nations building in Khartoum, "
    "Sudan\u2019s capital, as the war there grinds on.",
    "America\u2019s lead over China in Asia has narrowed to its smallest since "
    "2018, the Lowy Institute\u2019s Asia Power Index finds.",
    "The EU and Indonesia signed a landmark trade deal at the weekend, "
    "removing nearly all tariffs on goods traded between them.",
]

SOURCES = ("Compiled from the day\u2019s reporting: Reuters \u00b7 CNN \u00b7 BBC \u00b7 "
           "The Times \u00b7 The Wall Street Journal \u00b7 Le Monde \u00b7 "
           "Associated Press \u00b7 NHS England \u00b7 the Lowy Institute")


class Sheet:
    """One page at one type scale; the cursor flows top to bottom."""

    def __init__(self, scale):
        self.s = scale
        self.img = Image.new("RGB", (PAGE, PAGE), PAPER)
        self.d = ImageDraw.Draw(self.img)
        self.y = self.px(24)

    def px(self, v):
        return max(6, round(v * self.s))

    def font(self, path, size):
        return ImageFont.truetype(path, self.px(size))

    def measure(self, text, font):
        return self.d.textlength(text, font=font)

    def wrap(self, text, font, width):
        lines, current = [], ""
        for word in text.split():
            trial = (current + " " + word).strip()
            if self.measure(trial, font) <= width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def block(self, x, y, text, font, leading, color, width):
        """Draw wrapped text; return the y just below it."""
        for line in self.wrap(text, font, width):
            self.d.text((x, y), line, font=font, fill=color)
            y += self.px(leading)
        return y

    def centred(self, y, text, font, color, tracking=0):
        total = sum(self.measure(ch, font) for ch in text)
        total += tracking * max(0, len(text) - 1)
        x = MARGIN + (CONTENT - total) / 2
        for ch in text:
            self.d.text((x, y), ch, font=font, fill=color)
            x += self.measure(ch, font) + tracking
        return y

    def hline(self, y, weight=2, color=INK):
        self.d.rectangle([MARGIN, y, PAGE - MARGIN, y + self.px(weight) - 1],
                         fill=color)
        return y + self.px(weight)

    def double_hline(self, y):
        self.hline(y, 3)
        self.hline(y + self.px(5), 1)
        return y + self.px(6)

    def kicker(self, y, text):
        font = self.font(BOLD, 12)
        spaced = " \u00b7 ".join(text.split(" \u00b7 "))
        self.d.text((MARGIN, y), spaced, font=font, fill=RED)
        return y + self.px(20)

    def headline(self, y, text, size, leading, width=CONTENT):
        font = self.font(BOLD, size)
        return self.block(MARGIN, y, text, font, leading, INK, width)


def build(scale):
    sh = Sheet(scale)
    d = sh.d
    y = sh.y

    # ---- Masthead ----
    over = "ONE DAY \u00b7 ONE FRONT PAGE \u00b7 THE WORLD\u2019S NEWS"
    of = sh.font(BOLD, 13)
    ow = sh.measure(over, of)
    ox = MARGIN + (CONTENT - ow) / 2
    d.line([MARGIN, y + sh.px(8), ox - 14, y + sh.px(8)], fill=INK, width=1)
    d.line([ox + ow + 14, y + sh.px(8), PAGE - MARGIN, y + sh.px(8)],
           fill=INK, width=1)
    sh.centred(y, over, of, MUTED)
    y += sh.px(24)

    tf = sh.font(BOLD, 60)
    title = "THE WORLD IN ONE DAY"
    d.text((MARGIN + (CONTENT - sh.measure(title, tf)) / 2, y), title,
           font=tf, fill=INK)
    y += sh.px(74)

    df = sh.font(BOLD, 32)
    d.rectangle([MARGIN, y, PAGE - MARGIN, y + sh.px(52)], fill=RED)
    sh.centred(y + sh.px(7), DATE_LINE, df, PAPER)
    y += sh.px(60)
    y = sh.double_hline(y) + sh.px(12)

    # ---- Lead story ----
    y = sh.kicker(y, "THE LEAD \u00b7 BENGHAZI, LIBYA")
    y = sh.headline(y, LEAD_HEAD, 46, 52)
    bf = sh.font(REGULAR, 17)
    y = sh.block(MARGIN, y + sh.px(6), LEAD_BODY, bf, 24, BODY, CONTENT)
    y += sh.px(10)
    y = sh.hline(y, 3) + sh.px(12)

    # ---- Market band ----
    y = sh.kicker(y, "BUSINESS \u00b7 TECHNOLOGY \u00b7 WALL STREET")
    body_w = CONTENT - 300
    y = sh.headline(y, MARKET_HEAD, 28, 33, width=body_w)
    mf = sh.font(REGULAR, 16)
    y = sh.block(MARGIN, y + sh.px(5), MARKET_BODY, mf, 23, BODY, body_w)
    # Stat chips on the right of the market story.
    chip_x = PAGE - MARGIN - 280
    chip_y = y - sh.px(5) - 3 * sh.px(34)
    sf = sh.font(BOLD, 15)
    vf = sh.font(BOLD, 22)
    for name, value in MARKET_STATS:
        d.rectangle([chip_x, chip_y, chip_x + 280, chip_y + sh.px(30)],
                    outline=HAIR, width=1)
        d.text((chip_x + 12, chip_y + sh.px(5)), name, font=sf, fill=MUTED)
        vw = sh.measure(value, vf)
        d.text((chip_x + 280 - 12 - vw, chip_y + sh.px(2)), value,
               font=vf, fill=GREEN)
        chip_y += sh.px(34)
    y += sh.px(10)
    y = sh.hline(y, 2) + sh.px(12)

    # ---- Grid: four stories, two by two ----
    col_w = (CONTENT - 36) // 2
    gf = sh.font(BOLD, 24)
    kf = sh.font(BOLD, 11)
    sf2 = sh.font(REGULAR, 15)

    def story_cell(x, top, kicker, head, text):
        d.rectangle([x, top + 2, x + 2, top + sh.px(120)], fill=RED)
        tx = x + 14
        d.text((tx, top), kicker, font=kf, fill=RED)
        yy = top + sh.px(18)
        for line in sh.wrap(head, gf, col_w - 14):
            d.text((tx, yy), line, font=gf, fill=INK)
            yy += sh.px(29)
        yy += sh.px(3)
        for line in sh.wrap(text, sf2, col_w - 14):
            d.text((tx, yy), line, font=sf2, fill=BODY)
            yy += sh.px(21)
        return yy

    x_left, x_right = MARGIN, MARGIN + col_w + 36
    top = y
    end_l = story_cell(x_left, top, *STORIES[0])
    end_r = story_cell(x_right, top, *STORIES[1])
    row2 = max(end_l, end_r) + sh.px(12)
    d.line([x_left, row2 - sh.px(6), x_left + col_w, row2 - sh.px(6)],
           fill=HAIR, width=1)
    d.line([x_right, row2 - sh.px(6), x_right + col_w, row2 - sh.px(6)],
           fill=HAIR, width=1)
    end_l = story_cell(x_left, row2, *STORIES[2])
    end_r = story_cell(x_right, row2, *STORIES[3])
    y = max(end_l, end_r) + sh.px(10)
    y = sh.hline(y, 2) + sh.px(11)

    # ---- Briefs ----
    pf = sh.font(REGULAR, 14)
    bcol = (CONTENT - 56) // 2

    def brief_lines(items):
        return sum(len(sh.wrap(t, pf, bcol - 16)) for t in items)

    rows = max(brief_lines(BRIEFS_LEFT), brief_lines(BRIEFS_RIGHT))
    band_h = sh.px(12) + sh.px(30) + rows * sh.px(20) \
        + (len(BRIEFS_LEFT) - 1) * sh.px(6) + sh.px(12)
    d.rectangle([MARGIN, y, PAGE - MARGIN, y + band_h], fill=TINT)
    bx, by = MARGIN + 14, y + sh.px(12)
    hf = sh.font(BOLD, 19)
    d.text((bx, by), "ALSO ON ", font=hf, fill=INK)
    d.text((bx + sh.measure("ALSO ON ", hf), by), "MONDAY", font=hf, fill=RED)
    by += sh.px(30)

    def brief(x, yy, text):
        for i, line in enumerate(sh.wrap(text, pf, bcol - 16)):
            if i == 0:
                d.text((x + 2, yy), "\u2022", font=pf, fill=RED)
            d.text((x + 16, yy), line, font=pf, fill=BODY)
            yy += sh.px(20)
        return yy + sh.px(6)

    ly, ry = by, by
    for item in BRIEFS_LEFT:
        ly = brief(bx, ly, item)
    for item in BRIEFS_RIGHT:
        ry = brief(bx + bcol + 28, ry, item)
    y += band_h + sh.px(11)
    y = sh.hline(y, 3) + sh.px(9)

    # ---- Footer ----
    y = sh.double_hline(y) + sh.px(8)
    ff = sh.font(REGULAR, 12)
    d.text((MARGIN, y), SOURCES, font=ff, fill=MUTED)
    fdf = sh.font(BOLD, 12)
    d.text((PAGE - MARGIN - sh.measure(DATE_LINE, fdf), y), DATE_LINE,
           font=fdf, fill=RED)
    y += sh.px(18)
    return sh.img, y


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    for scale in (1.0, 0.96, 0.92, 0.88, 0.84, 0.80):
        img, bottom = build(scale)
        if bottom <= PAGE - 8:
            break
    print(f"scale {scale}: content bottom {bottom} of {PAGE}")
    img.save(out, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
