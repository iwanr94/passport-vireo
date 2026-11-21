# Republic of Vireo — Passport Spread

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![make.fun rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/iwanr94/passport-vireo/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![make.fun reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/iwanr94/passport-vireo/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

A 1024x1024 render of an open passport spread for the **Republic of Vireo**, a country that does not exist. Every field on the data page belongs to that invented state: a fictional passport number, an issuing authority, dates of birth and expiry, and a machine-readable zone whose check digits actually validate against the values above it.

The spread carries entry and exit stamps from invented ports of call, and a visa condition printed in the remarks field that reads *song-on-arrival* — the visitor is admitted only after performing a song at the border.

## Run

```sh
python3 main.py
```

This writes `/output/entry.png` (1024x1024, PNG, ~100 KB). Requires Pillow.
