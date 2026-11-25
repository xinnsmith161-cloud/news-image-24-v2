#!/usr/bin/env python3
"""Paint the 24 November 2026 front page of "The World" from its spec.

Page spec: a 1024x1024 broadsheet front page. A centred nameplate
with a dateline, one lead story spanning the full text width, then
forty-five short items in three columns under seven regional
banners. Every headline comes from a report published on 23-24
November 2026; the wording and sources are recorded in stories.md,
and the finished page is entry.png.

Implementation shape: the whole page is described as one flat feed.
Each region contributes a header line, then one line per story with
the headline and the standfirst joined by " || ". A parser turns the
feed into regions, a planner cuts the regions into three columns
(with "continued" markers where a region is split), and a painter
draws each piece. Only Pillow and the standard library are used, with
the system's DejaVu faces. The output is deterministic.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SHEET_W, SHEET_H = 1024, 1024
BACKGROUND = (253, 253, 248)
FOREGROUND = (12, 12, 12)
MUTED = (70, 70, 70)
RULE = (30, 30, 30)
SIGNAL = (140, 20, 20)
BANNER_FILL = (18, 18, 18)
HAIRLINE = (190, 190, 185)
COLUMN_RULE = (200, 200, 195)
SOFT_RULE = (150, 150, 145)
PAPER_WHITE = (255, 255, 255)

SIDE = 22
COLUMN_WIDTH = 320
GUTTER_WIDTH = 12
COLUMN_LEFTS = [SIDE + i * (COLUMN_WIDTH + GUTTER_WIDTH) for i in range(3)]
BASELINE_FOOTER = SHEET_H - 26
COLUMN_CAPS = (15, 14, 1 << 30)

FONT_FOLDER = Path("/usr/share/fonts/truetype/dejavu")
_FACE_CACHE = {}


def typeface(filename, size):
    """Load and cache one DejaVu face at the requested point size."""
    key = (filename, size)
    if key not in _FACE_CACHE:
        _FACE_CACHE[key] = ImageFont.truetype(str(FONT_FOLDER / filename), size)
    return _FACE_CACHE[key]


def face_title():
    return typeface("DejaVuSerif-Bold.ttf", 64)


def face_date():
    return typeface("DejaVuSans-Bold.ttf", 18)


def face_small():
    return typeface("DejaVuSans.ttf", 11)


def face_kicker():
    return typeface("DejaVuSans-Bold.ttf", 12)


def face_lead():
    return typeface("DejaVuSerif-Bold.ttf", 29)


def face_lead_deck():
    return typeface("DejaVuSerif.ttf", 14)


def face_banner():
    return typeface("DejaVuSans-Bold.ttf", 12)


def face_headline():
    return typeface("DejaVuSerif-Bold.ttf", 13)


def face_standfirst():
    return typeface("DejaVuSans.ttf", 11)


# The flat feed: region headers, then "headline || standfirst" lines.
FEED = [
    "NORTH AMERICA",
    "Trump wins path to erase hush-money case || Appeals court lets him seek federal court again.",
    "Trump orders faster federal executions || Justice Dept told to act without needless delay.",
    "Court clears Army detonation in Iowa || Appeals court allows blast of bomb material.",
    "Vance, Rubio meet Qatari PM on Iran || Talks as uncertainty over Trump plans mounts.",
    "CrowdStrike to buy Zscaler for $43.9bn || All-stock deal is the largest cyber deal yet.",
    "Amazon buys Decart AI tech in $7.5bn deal || Chip software and founders join Amazon.",
    "Commanders beat Bengals 22-20 || Washington holds on in Monday night finish.",
    "Pentagon rebukes Canada over defense || Says Ottawa falls short on F-35 review.",
    "LATIN AMERICA",
    "Bolsonaro stable in intensive care || Ex-president rests after bowel obstruction.",
    "Brazil bank chief warns on spending || Galipolo flags inflation risk in remarks.",
    "Drones hit police base in Cucuta, Colombia || Two civilians hurt; 60 homes damaged.",
    "Migrant caravan walks toward US border || About 300 cross from Guatemala into Mexico.",
    "Lula backs Sanchez in Spain snap vote || Brazil leader backs PM ahead of 29 Nov poll.",
    "Three Salvadoran soldiers die in Haiti blast || Accidental explosion during explosives work.",
    "EUROPE",
    "Russian drone enters Polish airspace || Brief incursion during night attack on Ukraine.",
    "Kremlin warns of painful consequences || Threat after Ukraine hits Russian ships off Libya.",
    "France rejects EU budget compromise || Paris says text fails farmers on incomes.",
    "Macron floats constitutional budget rule || Golden rule idea aims to calm bond markets.",
    "Germany grows, France shrinks in PMIs || German composite 55.0; French composite 46.2.",
    "Denmark court backs ghetto-law evictions || 91 leases ended; no ethnic bias, judges rule.",
    "Thousands protest living costs in Lisbon || Crowds march over rising prices in Portugal.",
    "AFRICA",
    "Fighting traps Ebola responders in Ituri || WHO staff shelter in maternity ward 24 hours.",
    "Ebola toll nears 5,700 deaths in Congo || 11,613 cases in worst-ever DRC outbreak.",
    "Sudan drone strikes cause mass blackouts || RSF attacks hit power stations, C54 reports.",
    "Ghana unveils Heritage Series banknotes || Notes honour Nkrumah, Annan, Makola traders.",
    "Kenya secures 293,600 jobs in Saudi Arabia || Questions over worker protections remain.",
    "South Africa bowl Bangladesh out for 91 || Hosts reach 88 for 1 on day one in Centurion.",
    "MIDDLE EAST",
    "US probes Iran link to tanker cyberattacks || Up to 50 ships targeted, WSJ reports.",
    "Three tankers ablaze after mine hits || Iran claim not independently confirmed.",
    "Qatar PM pushes to restart US-Iran talks || Push follows meeting with Rubio, reports say.",
    "Four Palestinians killed in Gaza strikes || Child among dead despite ceasefire, medics say.",
    "Israel kills two people in southern Syria || Army says pair moved oddly in security zone.",
    "Iran braces for winter gas shortages || War damage deepens the energy crisis.",
    "ASIA-PACIFIC",
    "China unveils Shenzhou-24 crew || Pakistani astronaut first foreigner on station.",
    "Hasina plans return to Bangladesh || Ousted PM to return from exile on 16 December.",
    "M5.6 quake strikes Nepal Koshi province || Tremor hits near the China border on Tuesday.",
    "Russian planes enter Korean defence zone || Seoul issues brief alert for Ulleung island.",
    "Asian chip stocks jump on Huang return || Taiwan shares trade near price limits.",
    "India third in Asia Power Index || Ahead of Japan and Russia, Lowy Institute says.",
    "Indonesia factory fire toll confirmed at 24 || Search goes on for about 30 people missing.",
    "OCEANIA",
    "Pacific islands go it alone on climate || Own coalitions after COP31 ends with no pact.",
    "Australia coalition opposes Vanuatu treaty || Climate clauses sink bipartisan backing.",
    "Fiji closes all schools for five days || El Nino drought crisis deepens, government says.",
    "India-New Zealand Test ends in a draw || NZ survive 120 overs, finishing on 239 for 5.",
    "Vanuatu region hit by deep M6.5 quake || No damage reported after Monday tremor.",
]

LEAD_KICKER = "LEAD STORY  \u00b7  TECHNOLOGY  \u00b7  MARKETS"
LEAD_HEADLINE = "Nvidia brings Huang back; shares jump 31%"
LEAD_DECK = (
    "Board reinstates Jensen Huang 11 days after his exit. "
    "Nasdaq rises 6.5% in its best day in over a year."
)


def parse_feed(feed):
    """Turn the flat feed into (label, [(headline, standfirst)]) pairs."""
    regions = []
    current = None
    for row in feed:
        head, sep, tail = row.partition(" || ")
        if not sep:
            current = [row, []]
            regions.append(current)
        else:
            current[1].append((head, tail))
    return [(label, stories) for label, stories in regions]


def wrap_lines(dc, text, font, limit):
    """Greedy word wrap: fill each line until the next word overflows.

    A word on its own always starts a line, even when it alone is
    wider than the limit; otherwise words join the current line while
    they still fit.
    """
    words = text.split()
    lines = []
    idx = 0
    while idx < len(words):
        line = words[idx]
        idx += 1
        while idx < len(words):
            joined = line + " " + words[idx]
            if dc.textlength(joined, font=font) > limit:
                break
            line = joined
            idx += 1
        lines.append(line)
    return lines


def plan_columns(regions):
    """Cut the regions, in order, into three columns.

    The first chunk takes 15 stories, the second 14, the last the
    rest. A chunk opening with a region's first story gets that
    region's banner; a chunk opening mid-region gets a "continued"
    marker for the region instead.
    """
    stream = []
    for label, stories in regions:
        for position, story in enumerate(stories):
            stream.append((label, position, story))
    planned = []
    cursor = 0
    for cap in COLUMN_CAPS:
        chunk = stream[cursor:cursor + cap]
        cursor += cap
        entries = []
        seen_label = None
        for label, position, story in chunk:
            if position == 0:
                entries.append(("banner", label, None))
            elif label != seen_label:
                entries.append(("resume", label, None))
            entries.append(("story", label, story))
            seen_label = label
        planned.append(entries)
    return planned


class Painter:
    """The drawing surface plus the page geometry."""

    def __init__(self, dc):
        self.dc = dc

    def rule(self, y, weight, colour=RULE):
        self.dc.line([(SIDE, y), (SHEET_W - SIDE, y)], fill=colour,
                     width=weight)

    def centred(self, text, y, font, colour):
        width = self.dc.textlength(text, font=font)
        self.dc.text(((SHEET_W - width) / 2, y), text, font=font,
                     fill=colour)

    def banner(self, x, y, label):
        self.dc.rectangle([x, y, x + COLUMN_WIDTH, y + 18], fill=BANNER_FILL)
        self.dc.text((x + 7, y + 3), label, font=face_banner(),
                     fill=PAPER_WHITE)
        return y + 25

    def resume(self, x, y, label):
        self.dc.text((x, y), label + "  -  CONTINUED", font=face_banner(),
                     fill=MUTED)
        self.dc.line([(x, y + 16), (x + COLUMN_WIDTH, y + 16)],
                     fill=SOFT_RULE, width=1)
        return y + 23

    def story(self, x, y, headline, standfirst):
        lines = wrap_lines(self.dc, headline, face_headline(), COLUMN_WIDTH)
        if len(lines) > 2:
            raise ValueError("headline wraps past two lines: %r" % headline)
        for line in lines:
            self.dc.text((x, y), line, font=face_headline(),
                         fill=FOREGROUND)
            y += 17
        if self.dc.textlength(standfirst, font=face_standfirst()) > COLUMN_WIDTH:
            raise ValueError("standfirst overflows: %r" % standfirst)
        self.dc.text((x, y), standfirst, font=face_standfirst(), fill=MUTED)
        y += 16
        self.dc.line([(x, y + 2), (x + COLUMN_WIDTH, y + 2)],
                     fill=HAIRLINE, width=1)
        return y + 10


def draw_nameplate(p):
    p.rule(12, 3)
    p.centred("The World", 16, face_title(), FOREGROUND)
    p.centred("Tuesday, 24 November 2026", 86, face_date(), SIGNAL)
    p.dc.text((SIDE, 88), "Vol. CXII  \u00b7  No. 328", font=face_small(),
              fill=MUTED)
    meta = "World News  \u00b7  46 Stories"
    p.dc.text((SHEET_W - SIDE - p.dc.textlength(meta, font=face_small()), 88),
              meta, font=face_small(), fill=MUTED)
    p.rule(110, 2)
    p.rule(114, 1)


def draw_lead(p):
    """The full-width lead story; returns the y where columns start."""
    y = 122
    p.dc.text((SIDE, y), LEAD_KICKER, font=face_kicker(), fill=SIGNAL)
    y += 18
    for line in wrap_lines(p.dc, LEAD_HEADLINE, face_lead(),
                           SHEET_W - 2 * SIDE):
        p.dc.text((SIDE, y), line, font=face_lead(), fill=FOREGROUND)
        y += 33
    for line in wrap_lines(p.dc, LEAD_DECK, face_lead_deck(),
                           SHEET_W - 2 * SIDE):
        p.dc.text((SIDE, y), line, font=face_lead_deck(), fill=MUTED)
        y += 18
    y += 2
    p.rule(y, 2)
    return y + 8


def draw_colophon(p):
    p.rule(BASELINE_FOOTER - 6, 1)
    p.centred(
        "The World  \u00b7  Tuesday, 24 November 2026  \u00b7  "
        "All stories from reports published 23-24 November 2026",
        BASELINE_FOOTER + 2, face_small(), MUTED)


def build_page():
    image = Image.new("RGB", (SHEET_W, SHEET_H), BACKGROUND)
    p = Painter(ImageDraw.Draw(image))
    draw_nameplate(p)
    top = draw_lead(p)
    for left, entries in zip(COLUMN_LEFTS,
                            plan_columns(parse_feed(FEED))):
        y = top
        for kind, label, story in entries:
            if kind == "banner":
                y = p.banner(left, y, label)
            elif kind == "resume":
                y = p.resume(left, y, label)
            else:
                y = p.story(left, y, story[0], story[1])
            if y > BASELINE_FOOTER - 4:
                raise ValueError("column overflow at %r" % (entries,))
        p.dc.line([(left, top - 4), (left, y)], fill=COLUMN_RULE, width=1)
    draw_colophon(p)
    return image


def main():
    image = build_page()
    target = Path(__file__).with_name("entry.png")
    image.save(target, optimize=True)
    print("wrote %s %dx%d" % (target, image.size[0], image.size[1]))


if __name__ == "__main__":
    main()
