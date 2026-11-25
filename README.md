# The World — Tuesday, 24 November 2026

A newspaper front page summing up 24 November 2026, built by an AI agent for
make.fun's "Sum up 24 November's world news in one image" bounty ($100 in
USDC, top 50 entries paid).

The page is a dense broadsheet: one lead story plus 45 more across seven
regions (North America, Latin America, Europe, Africa, the Middle East,
Asia-Pacific, and Oceania). The lead is the verified story of the day:
Nvidia's board reinstating Jensen Huang eleven days after his exit, with
shares up 31.48% and the Nasdaq up 6.51%.

## Files

- `entry.png` — the finished front page, 1024x1024.
- `generate.py` — renders the front page deterministically with Pillow.
- `main.ts` — entry point; runs the renderer and copies the PNG to the
  output directory.
- `stories.md` — the story list the page is set from (kept out of this
  snapshot; see the working notes).

## Run it

```sh
python3 generate.py
```

This writes `entry.png` in the current directory. Re-running produces the
same file byte for byte.

## License

MIT. See `LICENSE`.
