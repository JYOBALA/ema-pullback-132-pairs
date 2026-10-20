# Backtest Log — HYPE Scalp v4 / v5 (maker pullback)

Platform: openmarket.xyz · Chart **`8QvTI0Ik`** (huruf **I** besar — URL `8QvTl0Ik` dengan `l` kecil tidak ada dan memberi 404)
**Sumber data: BINANCE.F:HYPEUSDT** — bukan Hyperliquid native. Kata "Hyperliquid" di legend chart adalah nama aset (HYPE = token Hyperliquid), bukan exchange-nya.
Engine: wrun-ts · `instrument: "perps"` · leverage 5 · `qtyType: "percentOfEquity"` 20% → **notional $10.000** (1% notional = $100)
`fillModel: "pessimistic"` · `funding: "off"` · `pyramiding: 1`
Dikerjakan: 2026-10-18 → 2026-10-20

## KESIMPULAN SATU BARIS

**Tidak ada varian, timeframe, atau pair yang lolos kriteria — nol dari 132 pair.** Diuji 14 varian parameter, 4 timeframe (5m/15m/1h/4h), dan **sweep penuh 132 pair perp**: 93 di HYPERLIQUID.F + 39 di BINANCE.F (lihat `pair_sweep.md`). PF rata-rata lintas pair **0,912**; maksimum 1,300 (CYS); minimum 0,567 (Q). Max DD hanya sekali turun mendekati 10% (PAXG 11,2% — itu pun gagal PF). **Tujuh pair tampak lolos atau mendekati ambang di data dangkal; ketujuhnya turun saat data diperdalam, nol naik.** Dua kandidat sampai protokol penuh (MINA, CYS) dan keduanya gugur dengan struktur identik: paruh pertama rugi, seluruh keuntungan dari paruh kedua. Rekomendasi: hentikan sinyal ini.

---

## 0. Catatan engine yang menentukan interpretasi hasil

| Fakta | Implikasi |
|---|---|
| Limit entry & limit TP = **maker**, tanpa slippage | Biaya masuk murah |
| Limit dianggap terisi begitu harga **menyentuh** level (tidak ada antrean) | Hasil limit-entry **optimistis**; di live sebagian order tidak terisi |
| Stop / market / `closeAll` = **taker + slippage** | Sisi keluar yang mahal |
| Bracket exit baru aktif **sejak bar setelah entry terisi** | Bar pertama tidak terproteksi |
| Tester hanya menguji bar yang sudah dimuat chart | Harus pan ke kiri; "N bars" wajib dicatat tiap run |

**Biaya terukur langsung dari kolom FEES di tab Trades** (notional $10.000):

| Jalur exit | Fee round-trip | Keterangan |
|---|---|---|
| `limit` (TP) | **$3,94** | maker masuk + maker keluar |
| `stop` | **~$6,45** | maker masuk + taker keluar + slippage |
| `closeAll` (time stop) | ~$6,45 | market keluar, exit termahal |

Pada baseline 15m default: fee total $2.413,6 ÷ 459 trade = **$5,26/trade**.
Dari rata-rata ini campuran exit bisa dihitung: `x·3,94 + (1−x)·6,45 = 5,26` → **x ≈ 47% limit / 53% stop**, persis sama dengan win rate 47,7%. Artinya praktis setiap kemenangan = TP limit dan setiap kekalahan = stop.

---

## 1. Hasil 5m

Window: **3.652–3.655 bar**, ≈ 5 Okt 15:00 → 18 Okt 2026 (±12,7 hari).
"Zero" = `maker_fee_pct 0`, `taker_fee_pct 0`, `slippage_bps 0` (ablasi biaya, untuk mengisolasi edge sinyal).

| # | Varian | TF | Biaya | Perubahan (1 variabel) | Bar | Trade | Win% | Net % | PF | Max DD | Fee |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **V0** baseline | 5m | real | default | 3.652 | 396 | 45,2% | **−30,23%** | 0,58 | 30,4% | $2.010,3 |
| 2 | **E1** | 5m | zero | default | 3.653 | 396 | 49,0% | **−6,65%** | 0,90 | 11,2% | $0 |
| 3 | **E2** | 5m | zero | `be_trigger_r` 1 → 8 (BE mati) | ~3.654 | 344 | 40% | **−2,69%** | — | 9,3% | $0 |
| 4 | **E3** | 5m | zero | + `min_risk_pct` 0,3 → 0,8 | 3.654 | 155 | 47,7% | **+4,42%** | 1,09 | 12,9% | $0 |
| 5 | **E4** | 5m | zero | `min_risk_pct` 0,8 → 1,5 | ~3.654 | 131 | 47% | **+2,37%** | — | 11,8% | $0 |
| 6 | **E5** | 5m | **real** | konfigurasi E3 | 3.655 | 155 | 44,5% | **−7,57%** | 0,86 | 17,4% | $979,7 |

**E3 detail:** Net +$441,5 · GP/GL $5.327,1/$4.885,5 · B&H −15,2% · Sharpe 2,59 · avg trade **+$2,8** · payoff 1,19 · Exposure 79,5% · Long −$649,8 (56 · 44,6%) / Short +$1.091,3 (99 · 49,5%)
**E5 detail:** Net −$757,4 · GP/GL $4.539,3/$5.296,7 · Sharpe −4,30 · avg trade **−$4,9** · payoff 1,07 · fee maker $365,0 / taker $614,8 · Long −$1.052,2 (56 · 39,3%) / Short +$294,8 (99 · 47,5%)

**Kesimpulan 5m:** pada biaya nol pun sinyalnya rugi (E1 −6,65%, PF 0,90; ekspektansi ≈ −0,05R/trade). Konfigurasi terbaik menghasilkan avg trade **+$2,8** melawan biaya **$6,3** — gap 2,75×. 5m tidak layak diteruskan.

---

## 2. Hasil 15m

Window: **3.539–3.540 bar**, ≈ 11 Sep → 18 Okt 2026 (±36,9 hari). Dimuat dengan `left_click_drag` berulang (tombol "Scroll to the left" mentok setelah ±5 klik, zoom-out capped di 15m).

| # | Varian | TF | Biaya | Perubahan (1 variabel) | Bar | Trade | Win% | Net % | PF | Max DD | Fee |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 | **V0-15m** baseline | 15m | real | default | 3.539 | 459 | 47,7% | **−26,78%** | 0,77 | 31,0% | $2.413,6 |
| 8 | **E6** | 15m | zero | default | 3.539 | 459 | 51% | **+2,08%** | — | 12,5% | $0 |
| 9 | **E7** | 15m | zero | `be_trigger_r` 1 → 8 (BE mati) | 3.539 | 403 | 41% | **−0,92%** | — | 16,7% | $0 |
| 10 | **E8** | 15m | zero | `min_risk_pct` 0,3 → 0,8 (BE hidup) | 3.539 | 290 | 53% | **+5,70%** | — | 13,2% | $0 |
| 11 | **E9** | 15m | zero | `min_risk_pct` 0,8 → 1,5 | 3.540 | 158 | — | **+5,97%** | — | — | $0 |
| 12 | **E10** | 15m | zero | + `max_hold` 24 → 96 | 3.540 | 114 | 54,4% | **+10,73%** | 1,125 | 16,6% | $0 |
| 13 | **E11** | 15m | **real** | konfigurasi E10 | 3.540 | 114 | 54,4% | **+2,20%** | 1,025 | 18,6% | $680,4 |
| 14 | **E12** | 15m | **real** | + `be_trigger_r` 1 → 8 (BE mati) | 3.540 | 98 | 43,9% | **+5,47%** | 1,058 | 16,3% | $573,1 |

### Baseline 15m default (V0-15m) — detail lengkap
Net −$2.678,2 · GP/GL $8.947,1/$11.625,3 · B&H −1,0% · Sharpe/Sortino −7,48/−10,38 · Max runup +$1.084,6 · Exposure 44,7% · avg trade **−$5,8** · payoff 0,84 · fee maker $1.070,0 / taker $1.343,6 · Long −$589,7 (215 · 52,1%) / Short −$2.088,5 (244 · 43,9%) · LW +$125,2 / LL −$105,3 · streak 5 menang / 12 kalah · model-settled fills 8

### E10 (biaya nol, kandidat terbaik) — detail lengkap
Net +$1.073,3 · GP/GL $9.642,7/$8.569,4 · **PF 1,125** · Sharpe/Sortino 2,06/3,02 · Max runup +$2.393,8 · Exposure 83,4% · avg trade +$9,4 · payoff 0,94 · Long −$113,1 (53 · 56,6%) / Short +$1.186,4 (61 · 52,5%) · LW +$263,7 / LL −$179,8 · streak 10/6

### E12 (biaya nyata, kandidat terbaik) — detail lengkap
Net +$546,9 · GP/GL $9.927,9/$9.381,0 · **PF 1,058** · Sharpe/Sortino 1,15/1,66 · Max runup +$2.555,1 · Exposure 85,0% · avg trade +$5,6 · **payoff 1,35** · fee maker $300,6 / taker $272,5 · Long +$28,0 (44 · 43,2%) / Short +$518,9 (54 · 44,4%) · LW +$255,2 / LL −$187,2 · streak 9/9

---

## 3. Validation split & stress test

Window dibagi di titik tengah UTC day. `floor(epoch/86400)`: 2026-10-18 = day **20744**, 2026-09-11 = day **20707**, titik tengah **20725/20726**.
`start_day`/`end_day` hanya menggerbang *pengarman entry*; posisi yang sudah terbuka tetap boleh keluar setelah batas.

| Run | Gating | Bar | Trade | Win% | Net % | PF | Max DD | Fee |
|---|---|---|---|---|---|---|---|---|
| **Tuning half** | `end_day 20725` | 3.540 | 53 | 47,2% | **+10,87%** | **1,229** | 15,0% | $301,9 |
| **Validation half** | `start_day 20726` | 3.540 | 47 | 38,3% | **−7,87%** | **0,820** | 13,2% | $249,8 |
| **Stress test** | maker 0,05 / slip 5 bps | 3.540 | 98 | 43,9% | **−0,55%** | 0,994 | 18,3% | $994,5 |

**Tuning half detail:** Net +$1.087,3 · GP/GL $5.829,6/$4.742,3 · avg trade +$20,5 · payoff 1,38 · Sharpe 2,45 · Long +$816,7 (26 · 50,0%) / Short +$270,6 (27 · 44,4%)
**Validation half detail:** Net −$786,5 · GP/GL $3.580,2/$4.366,7 · avg trade **−$16,7** · payoff 1,32 · Sharpe −2,00 · Long **−$844,8** (19 · 31,6%) / Short +$58,3 (28 · 42,9%)
**Stress detail:** Net −$55,2 · GP/GL $9.392,0/$9.447,1 · avg trade −$0,6 · payoff 1,27 · Sharpe 0,16 · fee maker $730,2 / taker $264,3

### Catatan tambahan: hasilnya bergeser hanya karena data live bertambah

Setelah stress test, setting biaya dikembalikan ke nilai nyata (maker 0,02 / slip 2) — yaitu **persis konfigurasi E12**. Hasilnya tidak sama:

| | E12 (03:38 UTC) | Ulang (03:45 UTC) |
|---|---|---|
| Bar | 3.540 | 3.541 |
| Trade | 98 | 98 |
| Net | **+$546,9 · +5,47%** | **+$368,2 · +3,68%** |
| Max DD | −17,0%* | −17,0% |
| Fee | $573,1 | $568,4 |
| Largest win | +$255,2 | +$253,9 |

Jumlah trade **identik** (98) — tidak ada trade baru. Yang berubah hanya satu bar live dan sedikit revisi harga, tapi net profit bergeser **−$178,7, sepertiga dari total hasil**. Sebuah strategi yang hasil totalnya bergerak 1,8 poin persen karena satu bar baru tidak punya edge yang bisa diandalkan — ini konsisten dengan temuan stress test.

> **Catatan kejujuran metodologi:** E6–E12 dituning di **full window**, baru setelah itu split dijalankan. Jadi validation half **tidak sepenuhnya out-of-sample** — parameternya dipilih dengan pengetahuan atas seluruh data. Artinya −7,87% di validation half adalah estimasi yang **terlalu optimistis**, bukan terlalu pesimistis. Out-of-sample sejati kemungkinan lebih buruk.

---

## 3b. Sweep timeframe (HYPE, konfigurasi wide-R E12, biaya nyata)

Semua pakai parameter identik: `min_risk_pct 1,5` · `max_hold 96` · `be_trigger_r 8` · `rr 1,5` · maker 0,02 / taker 0,045 / slip 2.

| TF | Bar | Rentang | Trade | Win% | Net % | PF | Max DD | avg trade | B&H |
|---|---|---|---|---|---|---|---|---|---|
| 5m | 3.655 | 12,7 hari | 155 | 44,5% | −7,57% | 0,86 | 17,4% | −$4,9 | −15,2% |
| **15m** | 3.540 | 36,9 hari | 98 | 43,9% | **+5,47%** | 1,058 | 16,3% | +$5,6 | −1,0% |
| 1h | 2.461 | 102 hari | 195 | 41,5% | −0,53% | **0,997** | 25,2% | −$0,3 | +9,7% |
| 4h | 1.316 | 219 hari | 149 | 38,3% | −24,89% | 0,883 | 40,3% | −$16,7 | +109,5% |

**1h detail:** Net −$53,4 · GP/GL $19.314,6/$19.367,9 · Sharpe 0,17 · Exposure 62,8% · payoff 1,40 · fee $1.081,7 · Long +$268,1 (95 · 41,1%) / Short −$321,4 (100 · 42,0%) · LW +$546,4 / LL −$371,6
**4h detail:** Net −$2.488,6 · GP/GL $18.771,1/$21.259,8 · Sharpe −0,66 · Exposure 45,1% · payoff 1,43 · fee $728,1 · Long −$675,2 (85 · 38,8%) / Short −$1.813,5 (64 · 37,5%)

**Bacaan:** 597 trade di 4 timeframe, hanya 15m yang positif. 1h punya sampel paling kuat (195 trade / 102 hari) dan hasilnya **PF 0,997 — persis nol**. Naik timeframe **tidak** memperbaiki edge: edge mentah per trade justru turun dari ~$12,7 (15m) ke ~$6,3 (1h). Ini **membantah hipotesis `cost/R`** yang saya pakai untuk memilih arah tuning — memperbesar R memang mengurangi drag biaya, tapi tidak menciptakan edge, dan di TF tinggi sinyalnya malah makin lemah. 15m +5,47% adalah outlier yang konsisten dengan noise.

---

## 3c. Sweep lintas pair (semua di 1h, konfigurasi wide-R, biaya nyata)

Parameter **tidak pernah dituning ulang per pair** — semuanya memakai setting hasil tuning HYPE 15m. Artinya untuk BTC/ETH/SOL/ZEC, seluruh window sudah **out-of-sample**.

| Pair | Bar | Trade | Win% | Net % | PF | Max DD | B&H |
|---|---|---|---|---|---|---|---|
| HYPE | 2.461 | 195 | 41,5% | −0,53% | 0,997 | 25,2% | +9,7% |
| BTC | 2.962 | 95 | 35,8% | **−21,37%** | 0,762 | 28,4% | +24,8% |
| ETH | ~2.962 | 147 | 36% | **−31,64%** | — | 34,6% | — |
| SOL | ~2.962 | 172 | 41% | **−12,95%** | — | 26,2% | — |
| **ZEC** | 2.962 | 287 | 44,3% | **+20,22%** | 1,053 | 23,9% | **+131,8%** |

**BTC detail:** Net −$2.136,6 · GP/GL $6.855,8/$8.992,4 · Sharpe −2,15 · Exposure 83,0% · avg −$22,5 · payoff 1,37 · fee $502,1 · Long −$255,0 (53 · 41,5%) / Short −$1.881,5 (42 · 28,6%)
**ZEC detail:** Net +$2.021,5 · GP/GL $40.099,7/$38.078,1 · Sharpe 1,16 · Exposure 55,9% · avg +$7,0 · payoff 1,33 · fee $1.859,4 · **Long +$5.266,9 (164 · 47,6%) / Short −$3.245,4 (123 · 39,8%)**

### ZEC — satu-satunya kandidat positif, diuji split

| Run | Trade | Win% | Net % | PF | Max DD |
|---|---|---|---|---|---|
| Full window | 287 | 44,3% | +20,22% | 1,053 | 23,9% |
| Tuning half (`end_day 20682`) | 133 | 45,1% | +13,04% | 1,095 | 15,9% |
| **Validation half (`start_day 20683`)** | 154 | 42,9% | **+2,40%** | **1,011** | **23,9%** |

Validation half ZEC: net positif ✅ · ≥30 trade ✅ · **PF 1,011 ❌** (butuh 1,2) · **DD 23,9% ❌** (butuh <10%). Lolos 2 dari 4.

**Kenapa ZEC terlihat bagus, dan kenapa itu bukan edge:**
- B&H ZEC di window ini **+131,8%**. Strategi menghasilkan +20,22% di pasar yang naik 132% — **underperform buy-and-hold sebesar 112 poin persen** sambil menanggung DD 23,9%.
- Seluruh profit dari sisi long (+$5.266,9) sementara short rugi (−$3.245,4). Ini eksposur arah, bukan edge.
- PF 1,053 di ZEC vs PF 1,058 di HYPE 15m — dua pair berbeda, dua timeframe berbeda, **PF yang praktis sama**. Itu tanda tangan sistem ber-edge-nol: hasilnya ditentukan oleh tren aset, bukan oleh sinyalnya.

**Bacaan lintas pair:** 896 trade di 5 pair, jumlah net −46,3% (rata-rata −9,3% per pair). PF berkisar **0,76–1,05**, tidak pernah mendekati 1,2. Di **setiap** pair strategi kalah telak dari buy-and-hold. Volatilitas tinggi (ZEC) menaikkan angka net tapi tidak menaikkan PF — yang persis diprediksi kalau sinyalnya tidak punya informasi.

---

## 4. Status kriteria lolos

| Kriteria (tidak dilonggarkan) | Hasil | Status |
|---|---|---|
| Validation: ≥ 30 trade | 47 | ✅ |
| Validation: net profit > 0 setelah fee | −7,87% | ❌ |
| Validation: PF ≥ 1,2 | 0,820 | ❌ |
| Validation: max DD < 10% | 13,2% | ❌ |
| Tuning half juga positif | +10,87% | ✅ |
| Tetap breakeven tanpa trade terbesar | E12 full: +$546,9 − $255,2 = +$291,7 | ✅ (tapi tidak relevan, validation sudah gagal) |
| Tetangga parameter ±20% tidak langsung negatif | min_risk 1,5→0,8 menurunkan net; tidak diuji penuh karena validation sudah gagal | — |
| Stress test maker 0,05 / slip 5 bps | −0,55% | ❌ |

**4 dari 8 kriteria gagal, termasuk ketiga kriteria inti validation half.**
Varian terpakai: **14** dari jatah ~15.

### Rekap PF seluruh pengujian — tidak satu pun mencapai 1,2

| Pengujian | PF | Lolos PF ≥ 1,2? |
|---|---|---|
| HYPE 5m (E5) | 0,86 | ❌ |
| HYPE 15m full (E12) | 1,058 | ❌ |
| HYPE 15m tuning half | **1,229** | ✅ (satu-satunya, dan ini adalah paruh yang dituning) |
| HYPE 15m validation half | 0,820 | ❌ |
| HYPE 15m stress test | 0,994 | ❌ |
| HYPE 15m zero-cost ceiling (E10) | 1,125 | ❌ (bahkan tanpa biaya) |
| HYPE 1h | 0,997 | ❌ |
| HYPE 4h | 0,883 | ❌ |
| BTC 1h | 0,762 | ❌ |
| ZEC 1h full | 1,053 | ❌ |
| ZEC 1h tuning half | 1,095 | ❌ |
| ZEC 1h validation half | 1,011 | ❌ |

Satu-satunya PF ≥ 1,2 dalam seluruh pekerjaan ini muncul di paruh data yang dipakai untuk memilih parameternya. Itu definisi overfitting, bukan bukti edge.

---

## 5. Diagnosis

**(a) Biaya bukan satu-satunya masalah di 5m — sinyalnya sendiri tidak punya edge.**
E1 (biaya nol, default): −6,65%, PF 0,90. Ekspektansi ≈ `0,49 × 0,94R − 0,51R` = **−0,05R/trade**.

**(b) Di 15m edge mentahnya ada, tapi sangat kecil.**
E6 (biaya nol, default): **+2,08%** — positif, berbeda dari 5m. Tapi itu hanya `+$208 / 459 trade` = **+$0,45/trade** melawan biaya **$5,26/trade**. Rasio 1:12.

**(c) Tiga lever yang bekerja, dan alasannya.**

| Lever | Efek | Mekanisme |
|---|---|---|
| `min_risk_pct` 0,3 → 1,5 | edge/trade $0,45 → $3,78 | Biaya tetap dalam % notional, sedangkan R = jarak stop. Memperbesar R mengecilkan `cost/R`. Sekaligus menghindari stop-out oleh noise. |
| `max_hold` 24 → 96 | edge/trade $3,78 → $9,41 | Dengan R lebar, 24 bar habis sebelum TP tercapai, jadi mayoritas exit lewat `closeAll` (market = taker + slippage). Dilonggarkan, exit pindah ke `limit` TP yang bayar maker. |
| `be_trigger_r` 1 → 8 | payoff 0,86 → 1,35 | BE lock memotong pemenang sebelum mencapai TP 1,5R. |

**(d) Breakeven lock efeknya terbalik tergantung rezim — ini yang paling mudah salah disimpulkan.**
- Di 5m R sempit: mematikan BE **membantu** (E2: −6,65% → −2,69%).
- Di 15m R default: mematikan BE **merugikan** (E7: +2,08% → −0,92%).
- Di 15m R lebar + hold panjang: mematikan BE **membantu lagi** (E11 → E12: +2,20% → +5,47%).

Sensitivitas arah yang berbalik-balik seperti ini adalah ciri khas parameter yang tidak punya dasar struktural — ia menangkap kebetulan window, bukan sifat pasar.

**(e) Seluruh profit berasal dari sisi short, dan itu tidak bertahan.**
| Run | Long | Short |
|---|---|---|
| E10 (zero cost) | −$113,1 | **+$1.186,4** |
| E12 (real cost) | +$28,0 | **+$518,9** |
| Tuning half | +$816,7 | +$270,6 |
| **Validation half** | **−$844,8** | +$58,3 |

Di tuning half long-lah yang menghasilkan; di validation half long kehilangan −$844,8 dengan win rate anjlok 50,0% → 31,6%. Ini bukan edge yang stabil, ini arah pasar yang kebetulan.

**(f) Plafon PF-nya di bawah syarat bahkan tanpa biaya.**
E10 pada biaya nol sudah hanya **PF 1,125** dan **DD 16,6%** — keduanya di bawah/di atas syarat (PF ≥1,2, DD <10%) sebelum membayar sepeser pun. Memperkecil posisi bisa menurunkan DD (margin 20% → 12% membuat DD ≈ 9,8%) tapi **PF tidak berubah karena skala-invarian**. Jadi tidak ada pengaturan ukuran posisi yang bisa menyelamatkan ini.

**(g) Edge-nya lebih tipis daripada ketidakpastian biayanya.**
Menaikkan maker fee 0,02% → 0,05% dan slippage 2 → 5 bps mengubah +5,47% menjadi −0,55%. Keduanya angka yang sangat wajar di live. Strategi yang hasilnya berbalik tanda oleh perubahan asumsi biaya sekecil itu tidak bisa disebut punya edge.

---

## 6. Hambatan operasional yang tercatat

- **URL chart**: ID yang benar `8QvTI0Ik` (I besar). `8QvTl0Ik` (l kecil) → `GET /api/v1/workspaces/...` **404** dan "This chart is not available".
- **Browser**: ekstensi sempat terhubung ke Chrome (tidak login openmarket → "Guest Mode", disangka sesi kedaluwarsa padahal salah browser). Verifikasi dulu dengan `list_connected_browsers` sebelum menyimpulkan masalah auth. Ekstensi yang *terpasang* di Brave belum berarti *terdaftar* — harus login di dalam ekstensinya.
- **Jendela sempit**: tab MCP sempat dibuat di jendela Brave 356×741; `resize_window` dilaporkan sukses tapi tidak berefek (jendela ter-snap Windows). Solusi: buat tab baru — tab baru mendarat di jendela yang maximized.
- **Renderer crash**: chart 15m dengan strategi terpasang pernah membekukan renderer (CDP `Runtime.evaluate` timeout 45 s) dan tab ditutup paksa, 3×.
- **FE_EXECUTION_PAUSED**: chart mem-pause strategi yang >±130 ms per update. Harus di-Resume manual lewat chip "Paused by the chart" di legend, kalau tidak **perubahan setting tidak ter-apply dan angka di tester menyesatkan (tetap menampilkan hasil lama)**. Ini sumber kesalahan paling berbahaya di sesi ini.
- **Kedalaman backtest mengikuti chart**. Tombol "Scroll to the left" berhenti memuat setelah ±5 klik dan zoom-out capped di 15m; yang bekerja adalah `left_click_drag` dari (150,250) ke (870,250), ±3 hari per drag.
- **Edit nilai setting**: metode andal = `find` → klik via **ref** → `ctrl+a` → ketik → `Tab`. Klik via koordinat sering gagal fokus, dan `ctrl+a` tanpa fokus menyeleksi seluruh halaman. `form_input` tidak bisa (nilainya render sebagai `SPAN` sebelum diklik). Ref **tidak stabil antar panggilan** — ambil ref dan pakai segera.
- **Layout bergeser 32 px** saat bar "Paused, not applied to the chart / Resume" muncul; koordinat yang di-cache jadi salah sasaran.
- **Ikon legend bergeser** tergantung truncation teks: gear pernah di x=588, pernah di x=618, dengan tombol **×** (detach) hanya ~17 px di sebelahnya. Satu kali salah klik men-detach v4. Jangan pakai koordinat untuk ikon legend — pakai gear di header Strategy Tester (`find` → "Strategy settings"), di sana tidak ada tombol detach.
- Menekan Run di editor **me-reset parameter ke default kode**.

---

## 7. Rekomendasi

Tuning lanjutan pada sinyal ini tidak layak diteruskan. Buktinya bukan "belum ketemu setting bagus", melainkan tiga hal sekaligus: plafon PF di bawah syarat bahkan pada biaya nol, validation half negatif, dan hasil yang berbalik tanda oleh perubahan asumsi biaya yang wajar.

Yang masuk akal secara struktural:

1. ~~**Naik ke 1h atau 4h.**~~ **SUDAH DIUJI — TIDAK BERHASIL.** Rekomendasi ini saya tulis sebelum sweep timeframe dijalankan, dan datanya membantahnya: 1h memberi PF 0,997 (195 trade) dan 4h memberi PF 0,883 (149 trade). Memperbesar R lewat timeframe memang mengurangi drag biaya, tapi tidak menciptakan edge — dan di TF tinggi sinyal EMA-pullback justru makin lemah. Jalur ini tertutup.

2. **Ganti sinyalnya, bukan parameternya.** EMA trend + pullback adalah sinyal paling teroverfit di crypto. Yang punya premis ekonomi lebih jelas: funding-rate skew, basis spot-vs-perp, likuidasi cluster — bukan turunan harga murni.

3. ~~**Uji di data Hyperliquid, bukan Binance Futures.**~~ **SUDAH DIKERJAKAN — kesimpulannya tidak berubah.** Sweep 93 pair dijalankan di HYPERLIQUID.F (`pair_sweep.md`). Dugaan "kesimpulan tidak ada edge kemungkinan besar tetap berlaku" terkonfirmasi: PF rata-rata 0,911 lintas 93 pair, nol lolos. Cross-check langsung tersedia di STX — BINANCE.F memberi PF 1,193, HYPERLIQUID.F memberi 1,058; venue menggeser angkanya, tidak mengubah verdict.

4. **Kalau tetap ingin melanjutkan jalur ini, perbaiki protokolnya dulu**: tentukan split tuning/validation **sebelum** tuning dimulai, dan jangan pernah melihat validation half sampai parameter dibekukan. Di sesi ini urutannya terbalik, sehingga −7,87% itu pun masih angka yang terlalu baik.

5. **Jangan mencari pair "yang ada edge-nya" dengan menyapu daftar simbol.** Itu yang saya lakukan di bagian 3c dan hasilnya instruktif: dari 5 pair, satu (ZEC) keluar +20,22%. Kalau berhenti di situ, kesimpulannya akan "ketemu!". Padahal PF-nya 1,053, DD 23,9%, dan B&H-nya +131,8% — strategi itu hanya menumpang tren, kalah 112 poin persen dari beli-dan-diam. Menyapu N pair lalu mengambil yang terbaik **menjamin** menemukan pemenang semu, karena yang dipilih adalah pair dengan tren terkuat, bukan pair tempat sinyalnya bekerja. Kalau menyapu pair, syaratnya: tentukan kriteria sebelum menyapu, dan nilai PF + perbandingan terhadap B&H, bukan net %.

---

## 8. Sweep penuh 93 pair Hyperliquid — hasil akhir

Dijalankan 2026-10-18 → 2026-10-20. Detail per pair ada di **`pair_sweep.md`**; ringkasannya di sini.

| Metrik | Nilai |
|---|---|
| Pair teruji | 93 (dari 95 antrean: 1 N/A, 1 duplikat) |
| **Lolos screening** | **0** |
| PF rata-rata | 0,911 |
| PF maks / min | 1,220 (MINA) / 0,587 (WLFI) |
| Net positif / negatif | 23 / 70 |
| vs B&H | 12 menang · 2 seri · 79 kalah |

### Yang membuat sweep ini bukan sekadar "belum ketemu pair yang tepat"

**Bentuk distribusinya.** PF terpusat di 0,911 dengan ekor tipis di atas 1,0 — persis bentuk yang diharapkan dari sinyal tanpa edge yang membayar biaya: nilai tengah di bawah breakeven sebesar biaya per trade, sisanya noise. Strategi yang punya edge tapi butuh pasar cocok akan memberi *kelompok* pair di atas ambang, bukan tiga kandidat yang semuanya runtuh saat diperdalam.

**Aturan kedalaman data menangkap tiga false positive:**

| Pair | PF dangkal | PF dalam |
|---|---|---|
| DOGE | 1,301 @1.715 bar | 0,884 @3.215 bar |
| MINA | 1,368 @2.744 bar | 1,220 @3.994 bar |
| kBONK | 1,253 @1.995 bar | 0,992 @3.495 bar |

Arahnya selalu turun. Estimasi yang benar bergerak dua arah saat sampel bertambah; yang meluruh satu arah adalah noise yang tadinya terukur terlalu optimistis. Protokol memprediksi ~5 pemenang semu dari 95 tes independen — yang muncul 3, dan ketiganya tersaring.

**MINA** adalah satu-satunya yang sampai protokol penuh. Split waktunya: paruh awal **−17,07%** (PF 0,897, 184 trade) vs paruh akhir **+124,80%** (PF 1,456, 176 trade). Karena parameter diambil utuh dari HYPE tanpa tuning di MINA, kedua paruh itu out-of-sample — jadi yang terukur bukan overfitting parameter melainkan ketidakstabilan antarwaktu. Dan hasilnya tidak stabil.

**PAXG** satu-satunya yang berperilaku waras: DD 11,2%, kedua sisi positif, Sharpe +0,91, kalahkan B&H. Gagal di PF 1,158 dan hanya 48 trade. Bukan kandidat, tapi arahnya informatif — strategi ini paling tidak berantakan di instrumen vol rendah bertren mulus, bukan altcoin.

**"Mengalahkan B&H" tetap bukan alpha.** 12 pair mengalahkan B&H; **10 di antaranya tetap rugi uang**, hanya rugi lebih sedikit daripada asetnya (USELESS −31,87% vs −53,1%; BLUR −4,68% vs −48,9%; kBONK −2,48% vs −50,8%). Itu efek beta rendah dari eksposur parsial ~50–60%, bukan alpha.

---

## 9. Batch 2 — 39 pair khusus Binance

Dijalankan 2026-10-20 atas permintaan eksplisit setelah batch 1 selesai. Beban multiple-testing dicatat di muka: **~2 pemenang semu diharapkan dari 39 tes kalau strategi tidak punya edge sama sekali.**

| Metrik | Nilai |
|---|---|
| Pair teruji | 39 |
| **Lolos screening** | **0** |
| PF rata-rata | 0,914 |
| PF maks / min | 1,300 (CYS) / 0,567 (Q) |
| Net positif / negatif | 12 / 27 |

### CYS — satu-satunya dari 132 pair yang PF-nya bertahan ≥1,25 di kedalaman penuh

| Uji | Hasil | Verdict |
|---|---|---|
| PF @4.508 bar | **1,300** | ✓ |
| Stress test (maker 0,05 / slip 5) | PF **1,2503** | ✓ (lolos 0,0003) |
| Max DD | 18,4% | ✗ (>10%) |
| Paruh awal (231 trade) | **−23,95%**, PF 0,918 | ✗ |
| Paruh akhir (243 trade) | +677,10%, PF 1,379 | — |

Net +500,54% di full window adalah rata-rata dari satu paruh yang rugi 24% dan satu paruh yang untung 677%. Tiga hal memperbesar angkanya secara artifisial: compounding (`percentOfEquity` membuat trade akhir jauh lebih besar dari trade awal), B&H −68,7% (seluruh untung dari sisi short di satu runtuhan), dan paruh pertama yang negatif.

**Dua kandidat terbaik dari 132 pair — MINA (Hyperliquid) dan CYS (Binance) — gagal dengan struktur yang persis sama: paruh pertama rugi, seluruh keuntungan dari paruh kedua.** Dua aset tidak berhubungan di dua venue berbeda, pola kegagalan identik. Itu bukan kebetulan; itu tanda strategi ini menangkap rezim, bukan edge.

### Temuan metodologis terkuat dari seluruh proyek

Tujuh pair menunjukkan PF di atas atau mendekati ambang pada data dangkal. **Ketujuhnya turun saat diperdalam. Nol naik.** Besaran bias: 0,07–0,42.

Kalau strategi punya edge nyata, estimasi PF akan bergerak dua arah saat sampel bertambah. Tujuh dari tujuh satu arah adalah tanda bahwa yang terukur di window pendek adalah noise optimistis. Tanpa aturan kedalaman data, sweep ini akan melaporkan enam "pemenang" palsu.

---

**Tiga hal yang tidak boleh dilakukan:**
- Menjalankan MINA live karena full window-nya +86,43%. Angka itu rata-rata dari −17,07% (98 hari pertama) dan +124,80% (68 hari terakhir). Yang Anda beli adalah taruhan bahwa rezim 68 hari terakhir berlanjut, bukan sebuah edge.
- Menjalankan konfigurasi E12 di HYPE secara live karena full window-nya +5,47%. Angka itu rata-rata dari +10,87% (paruh yang dituning) dan −7,87% (paruh yang tidak). Yang akan dialami ke depan adalah yang kedua.
- Menjalankannya di ZEC karena +20,22%. Itu PF 1,011 di validation half dengan DD 23,9% — Anda menanggung risiko kehilangan seperempat modal untuk mendapat hasil yang secara statistik tidak bisa dibedakan dari nol, di aset yang kalau hanya dibeli dan didiamkan memberi +131,8%.
