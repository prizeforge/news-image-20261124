# 24 November 2026 in one image

Entry for the make.fun bounty **news-image-20261124**: sum up 24 November 2026's
world news in one image.

## What the image shows

A newspaper front page, 1024x1024, four stories that dominated 24 November 2026:

1. **Nvidia brings back Jensen Huang as CEO — shares +31%.** The board
   unanimously reinstated its founder as CEO on Monday 23 Nov (US), and NVDA
   ended the day up 31.5%, its best day since 2003, a single-day gain of
   about $952 billion in market value. Nasdaq +6.5%, S&P 500 +4.7%.
2. **COP31 climate talks collapse in Antalya.** After more than two weeks of
   talks, the longest COP ever, 194 countries failed to agree a deal on
   Sunday 22 Nov — the "Antalya Pact" was rejected because it never named
   fossil fuels.
3. **Russian drone strike near Kyiv: 14 missing.** A drone hit a five-storey
   apartment block in Dymer, Kyiv region, on Sunday 22 Nov; rescuers were
   still searching the rubble.
4. **Indonesia candy factory fire: 24 dead.** A fire at the PT Fonusa Agung
   Mulia (Milkita) factory in Serang, Banten, on Saturday 21 Nov killed 24
   and left about 30 missing; the search continued into Monday.

Sources for every story are listed in `../notes/news-image-20261124.md`
(in the builder's workspace, not this repo).

## How it is built

`scripts/render.py` draws the front page with Python + Pillow (flat editorial
style, cream paper, navy ink) and writes `assets/entry.png` (1024x1024).
`main.ts` (Node 22, standard library only) copies that image to
`/output/entry.png`, so two runs write byte-identical output.

## Run it

```sh
node main.ts   # writes /output/entry.png
```

## License

MIT. See LICENSE.
