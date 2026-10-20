# Pair Sweep — inventaris & tracker

> **CATATAN ARSIP.** Ini adalah catatan kerja mentah, disimpan apa adanya supaya
> bisa diaudit. Setiap baris hasil ditulis saat pengukuran, sebelum verdict
> dibentuk — itulah nilainya.
>
> **Tetapi rata-rata PF berjalan di dokumen ini dihitung manual dan melenceng.**
> Dokumen ini menyebut rata-rata batch 1 = 0,911; hitung ulang dari seluruh 93
> nilai yang tercatat memberi **0,9216**. Rata-rata gabungan 132 pair =
> **0,9192**, bukan 0,912.
>
> Angka otoritatif ada di [`../data/results.csv`](../data/results.csv), yang
> di-parse langsung dari tabel di bawah. Semua angka di README dihitung dari CSV
> itu, bukan dari tally manual ini. Lihat bagian "Corrections" di README.

Dibuat 2026-10-18. Strategi: **HYPE Scalp v4 wide-R** (`min_risk_pct 1,5` · `max_hold 96` · `be_trigger_r 8` · `rr 1,5` · `pull_atr 0,5` · `stop_atr 1,0` · `fast 20` / `slow 100` / `atr 14` · `entry_ttl 3`).
Biaya: maker 0,02% · taker 0,045% · slippage 2 bps. Notional $10.000 (equity 10k × 20% margin × 5×).
Timeframe pengujian: **1h** (sampel paling kuat: ~2.900 bar ≈ 123 hari, ~100–290 trade per pair).

---

## Cakupan yang tersedia di openmarket

Panel simbol memotong daftar di **100 aset per filter** (`.asset-list__scroll` scrollHeight 5000px, tercapai penuh). Daftar diurutkan platform berdasarkan keaktifan, jadi 100 itu = 100 paling likuid. Ini bukan batasan yang merugikan: perp di luar top-100 punya spread dan slippage nyata yang lebih buruk daripada asumsi 2 bps di backtest, sehingga hasilnya akan optimistis palsu.

| Filter | Jumlah | Venue |
|---|---|---|
| Crypto · Perps · **Binance** | 100 | `BINANCE.F` |
| Crypto · Perps · **Hyperliquid** | 100 | `HYPERLIQUID.F` |
| Union kedua venue | **139** unik | — |
| Irisan (ada di kedua venue) | 61 | — |

Kategori lain di panel (Memecoins, Equities, Forex, Commodities, Indices, Predict, CME, HIP-4, Economy, Options) **tidak dimasukkan**: strategi dikonfigurasi `instrument: "perps"` dengan asumsi fee crypto perp. Memecoin perp sudah tercakup di daftar Crypto (FARTCOIN, PENGU, WIF, KBONK, USELESS, dst).

---

## Keputusan venue: Hyperliquid

Sweep dijalankan di **HYPERLIQUID.F**, bukan Binance. Alasannya: seluruh pekerjaan sebelumnya memakai BINANCE.F padahal target Anda perp Hyperliquid — itu caveat yang saya catat di `backtest_log.md` dan sweep ini kesempatan menutupnya. Fee dasar Hyperliquid (maker ~0,015% / taker ~0,045%) cukup dekat dengan asumsi sekarang.

---

## PROTOKOL — ditetapkan SEBELUM sweep dimulai

Ini bagian terpenting dari dokumen ini. Menguji 95 pair lalu mengambil yang terbaik **dijamin** menghasilkan pemenang semu: pada 95 tes independen dengan peluang 5% terlihat bagus karena kebetulan, ekspektasinya **~5 "pemenang" murni dari noise**. Kasus ZEC sudah membuktikannya (net +20,22% tapi PF 1,053, dan B&H-nya +131,8%).

**Aturan yang tidak boleh dilonggarkan setelah melihat hasil:**

1. **Catat SEMUA hasil**, bukan hanya yang positif. Tabel di bawah diisi berurutan tanpa pengecualian.
2. **Kriteria lolos screening** (dinilai di full window dulu, untuk menyaring):
   - PF ≥ **1,25** (dinaikkan dari 1,2 sebagai koreksi multiple-testing)
   - Max DD < 10%
   - ≥ 60 trade di full window (supaya validation half punya ≥30)
   - Net > 0 setelah biaya
   - **Kedua sisi tidak berdarah**: sisi yang rugi tidak boleh > 50% dari profit sisi yang untung
   - **Mengalahkan B&H risk-adjusted**: `net% / maxDD` harus > `B&H% / maxDD_B&H`
3. **Kandidat yang lolos screening** baru dijalankan protokol penuh: split tuning/validation, stress test (maker 0,05 / slip 5 bps), tetangga parameter ±20%, dan tes buang-trade-terbesar.
4. **Nilai PF dan perbandingan terhadap B&H, bukan net %.** Net % tinggi di pasar yang naik 130% bukan temuan.
5. Parameter **tidak dituning ulang per pair**. Semua pakai setting yang sama, sehingga setiap pair adalah tes out-of-sample murni dari konfigurasi tersebut.

---

## Realitas waktu

Per pair: ganti simbol → ~10 drag-pan untuk memuat ~2.900 bar → tunggu recompute → baca Performance. Sekitar **5 panggilan tool dan 3–4 menit**, belum termasuk renderer crash berkala (sudah terjadi 3× sesi ini).

**95 pair × 3,5 menit ≈ 5,5 jam** otomasi browser berjalan terus. Ini akan melintasi banyak sesi. Tracker ini yang menjaga progresnya supaya tidak ada yang diulang.

---

## Sudah diuji — JANGAN diulang

Semuanya di **BINANCE.F**, timeframe 1h, konfigurasi wide-R, biaya nyata.

| # | Pair | Bar | Trade | Win% | Net % | PF | Max DD | B&H | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| — | HYPE | 2.461 | 195 | 41,5% | −0,53% | 0,997 | 25,2% | +9,7% | ❌ |
| — | BTC | 2.962 | 95 | 35,8% | −21,37% | 0,762 | 28,4% | +24,8% | ❌ |
| — | ETH | ~2.962 | 147 | 36% | −31,64% | — | 34,6% | — | ❌ |
| — | SOL | ~2.962 | 172 | 41% | −12,95% | — | 26,2% | — | ❌ |
| — | ZEC | 2.962 | 287 | 44,3% | +20,22% | 1,053 | 23,9% | +131,8% | ❌ (PF & DD gagal; split: tuning 1,095 → validation 1,011) |

Juga sudah diuji di HYPE: timeframe **5m** (PF 0,86), **15m** (PF 1,058), **4h** (PF 0,883). Jangan diulang.

---

## ⚠ CACAT METODE YANG DITEMUKAN DI #11 — WAJIB DIBACA

**Jumlah bar tidak distandarkan antar pair, dan itu bisa membalik verdict sepenuhnya.**

DOGE membuktikannya: pada **1.715 bar** hasilnya +30,30% dengan **PF 1,301** — lolos ambang, mengalahkan B&H, kedua sisi positif. Setelah history ditambah ke **3.215 bar**, hasilnya **−15,80% dengan PF 0,884**. Terbalik total.

Jumlah bar per pair yang sudah diuji:

| Bar | Pair | Status |
|---|---|---|
| ~2.965 | PUMP, STRK, XMR, WLD, ENA | dapat dipercaya |
| 2.465 | XRP | cukup |
| 1.965 | TIA | cukup |
| **1.715** | **SUI, XPL, PYTH, DOGE** | **tidak dapat dipercaya** |

**Aturan baru untuk sisa sweep: minimum 2.900 bar, dan jumlah bar dicatat di setiap baris.** Kalau pan tidak mencapai itu (koneksi lambat), ulangi pan sampai tercapai sebelum membaca hasil.

**Yang harus diulang:** SUI (PF 1,121 — satu-satunya dari grup window-pendek yang masuk kelompok "bagus"). XPL dan PYTH sudah negatif di window pendek sehingga menambah data kemungkinan hanya memperjelas, tapi tetap ditandai belum final.

Pelajaran umum: pada window pendek, strategi ini bisa menghasilkan PF > 1,3 murni dari kebetulan. Itu bukan edge — itu alasan kenapa kedalaman data dan validation split tidak bisa ditawar.

---

## STATISTIK BERJALAN — 15 dari 95 pair selesai

| Pair | Bar | Net % | PF | DD | B&H |
|---|---|---|---|---|---|
| STRK | 2.962 | +88,80% | **1,193** | 36,4% | +79,8% |
| LINK | 1.716 | +22,82% | 1,169 | 17,2% | +46,4% |
| PUMP | 2.962 | +93,31% | 1,160 | 23,8% | +190,5% |
| ZRO | 1.465 | +56,84% | 1,149 | 39,2% | +139,1% |
| ENA | 2.965 | +39,24% | 1,085 | 34,1% | +118,3% |
| SUI | 2.215 | +12,68% | 1,069 | 18,2% | +32,7% |
| TIA | 1.965 | +11,67% | 1,046 | 25,4% | +90,6% |
| INJ | 1.966 | +0,61% | 1,002 | 22,4% | +85,0% |
| XRP | 2.465 | −3,37% | 0,977 | 32,6% | +14,7% |
| LIT | 1.965 | −16,40% | 0,946 | 38,4% | +42,5% |
| XPL | 1.715 | −14,82% | 0,929 | 28,9% | +3,6% |
| DOGE | 3.215 | −15,80% | 0,884 | 40,9% | −2,5% |
| XMR | 2.965 | −26,27% | 0,879 | 35,8% | +67,5% |
| WLD | 2.965 | −47,81% | 0,866 | 63,5% | −25,0% |
| PYTH | 1.715 | −36,79% | 0,837 | 51,3% | +103,0% |

Ditambah **#16 KPEPE** (1.466 bar, −41,46%, **PF 0,656**, B&H +51,4%), **#17 ONDO** (1.216 bar, −7,67%, PF 0,944, B&H +22,9%), **#18 SAND** (1.716 bar, +14,85%, PF 1,070, B&H +56,5%), **#19 FIL** (1.716 bar, +13,93%, PF 1,063, B&H +54,1%).

Ditambah **#20 ARB** (0,909), **#21 UNI** (0,961), **#22 MON** (1,160 — kalahkan B&H +33 pp), **#23 TAO** (0,943), **#24 PONS** (0,760, DD 69%), **#25 FARTCOIN** (1,063 — kalahkan B&H +11 pp), **#26 AVAX** (0,758), **#27 NIL** (1,136), **#28 CRV** (0,823, 3.466 bar), **#29 VVV** (0,934), **#30 BNB** (0,807).

## 🏁 HASIL AKHIR GABUNGAN — 132 pair teruji, 0 lolos

Selesai 2026-10-20. Batch 1 (93 pair HYPERLIQUID.F) + batch 2 (39 pair BINANCE.F).

| Metrik | Batch 1 | Batch 2 | **Gabungan** |
|---|---|---|---|
| Pair teruji | 93 | 39 | **132** |
| **Lolos screening** | 0 | 0 | **0** |
| PF rata-rata | 0,911 | 0,914 | **0,912** |
| PF maksimum | 1,220 (MINA) | **1,300 (CYS)** | **1,300** |
| PF minimum | 0,587 (WLFI) | 0,567 (Q) | **0,567** |
| Net positif / negatif | 23 / 70 | 12 / 27 | **35 / 97** |
| Kalah dari B&H | 79 | 31 | **110 dari 132** |

### Temuan tunggal yang paling kuat: peluruhan satu arah

Tujuh pair menunjukkan PF di atas atau mendekati ambang pada data dangkal. **Ketujuhnya turun saat data diperdalam. Nol naik.**

Ini bukan sekadar "tidak ketemu pair yang tepat". Kalau strategi punya edge nyata yang hanya butuh pasar cocok, estimasi PF akan bergerak **dua arah** saat sampel bertambah — kadang naik, kadang turun, mengerucut ke nilai sebenarnya. Tujuh dari tujuh satu arah adalah tanda statistik klasik bahwa **yang diukur di window pendek adalah noise optimistis**, bukan sinyal.

Besaran biasnya: PF di <3.000 bar bisa **0,07–0,42 terlalu tinggi**.

### Dua kandidat yang sampai protokol penuh — keduanya gugur di split waktu

| | MINA (batch 1) | CYS (batch 2) |
|---|---|---|
| PF kedalaman penuh | 1,220 ✗ | **1,300 ✓** |
| Max DD | 30,8% ✗ | 18,4% ✗ |
| Stress test | — | PF 1,2503 ✓ (tipis) |
| **Paruh awal** | **−17,07% (PF 0,897)** | **−23,95% (PF 0,918)** |
| **Paruh akhir** | **+124,80% (PF 1,456)** | **+677,10% (PF 1,379)** |

**Keduanya punya struktur identik: paruh pertama rugi, seluruh keuntungan dari paruh kedua.** Dua kandidat terbaik dari 132, ditemukan di venue berbeda dan aset yang sama sekali tidak berhubungan, gagal dengan cara yang persis sama. Itu bukan kebetulan — itu tanda bahwa yang ditangkap strategi ini adalah rezim, bukan edge.

### Distribusi PF memberi diagnosis yang sama

Rata-rata 0,912 dengan ekor tipis di atas 1,0. Itu bentuk yang diharapkan dari sinyal tanpa edge yang membayar biaya: nilai tengah di bawah breakeven sebesar kira-kira biaya per trade, sisanya sebaran acak. Strategi dengan edge yang butuh pasar cocok akan memberi *kelompok* pair di atas ambang — bukan satu outlier yang runtuh begitu diperiksa.

### "Mengalahkan B&H" tetap bukan alpha

20 pair mengalahkan B&H dari 132. **13 di antaranya tetap rugi uang** — hanya rugi lebih sedikit daripada asetnya. Itu efek beta rendah dari eksposur parsial ~50–60%. Hanya 7 yang menang sambil untung, dan tidak satu pun lolos screening.

---

## SWEEP BATCH 1 — 95 antrean, 93 pair teruji

Selesai 2026-10-20. Dari 95 baris antrean: **93 teruji**, 1 N/A (tidak ada di venue), 1 duplikat (#95 = #80 MORPHO).

### Hasil akhir

| Metrik | Nilai |
|---|---|
| **Pair lolos screening** | **0 dari 93** |
| PF rata-rata | **0,911** |
| PF maksimum | **1,220** (MINA, 3.994 bar) |
| PF minimum | **0,587** (WLFI, 3.006 bar) |
| Net positif | 23 dari 93 |
| Net negatif | 70 dari 93 |
| Mengalahkan B&H | 12 menang · 2 seri · **79 kalah** |

Ambang yang harus dilewati: PF ≥ 1,25 · DD < 10% · ≥60 trade · net > 0 · kedua sisi tidak berdarah · kalahkan B&H risk-adjusted. **Tidak ada satu pun pair yang melewati semuanya.** Bahkan kalau kriteria DD dicabut sepenuhnya — kriteria yang paling bisa diperdebatkan karena DD skalanya ikut ukuran posisi — tetap nol, karena tidak ada yang punya PF ≥ 1,25 di kedalaman data penuh.

### Kenapa ini bukan sekadar "belum ketemu pair yang tepat"

Distribusi PF-nya terpusat di bawah 1,0 (rata-rata 0,911) dengan ekor tipis di atasnya. Itu bentuk yang diharapkan dari **strategi tanpa edge yang membayar biaya**: nilai tengahnya di bawah breakeven sebesar kira-kira biaya per trade, dan sebaran di sekitarnya adalah noise.

Kalau strategi ini punya edge yang hanya butuh pasar yang cocok, kita akan melihat sekelompok pair yang konsisten di atas 1,25, bukan tiga kandidat yang semuanya runtuh begitu datanya diperdalam.

### Tiga false positive — pola yang paling menentukan

| Pair | PF data dangkal | PF data dalam | Selisih |
|---|---|---|---|
| DOGE | 1,301 @1.715 bar | 0,884 @3.215 bar | −0,417 |
| MINA | 1,368 @2.744 bar | 1,220 @3.994 bar | −0,148 |
| kBONK | 1,253 @1.995 bar | 0,992 @3.495 bar | −0,261 |

**Arahnya selalu turun, tidak pernah naik.** Estimasi yang benar akan bergerak dua arah saat sampel bertambah. Yang meluruh satu arah adalah noise yang tadinya terukur terlalu optimistis. Tanpa aturan kedalaman data, sweep ini akan melaporkan tiga "pemenang" palsu — persis ~3–5 yang diprediksi di protokol sebagai konsekuensi 95 tes independen.

### MINA — satu-satunya yang sampai protokol penuh

Lolos PF di pembacaan awal, lalu gugur di tiga titik: PF turun ke 1,220 di kedalaman penuh, DD 30,8%, dan split waktunya menunjukkan **paruh awal −17,07% (PF 0,897) vs paruh akhir +124,80% (PF 1,456)**. Seluruh hasilnya berasal dari satu rezim 68 hari terakhir. Detail di bagian khusus di bawah.

### PAXG — satu-satunya yang berperilaku waras

DD 11,2% (satu-satunya yang mendekati ambang 10%), kedua sisi positif, Sharpe +0,91, mengalahkan B&H. Gagal di PF (1,158) dan jumlah trade (48). Bukan kandidat, tapi petunjuk arah: strategi ini paling tidak berantakan di instrumen volatilitas rendah dan bertren mulus (emas), bukan altcoin.

### "Mengalahkan B&H" tetap bukan alpha

12 pair mengalahkan B&H, **10 di antaranya tetap rugi uang** — hanya rugi lebih sedikit daripada asetnya. Itu efek beta rendah dari eksposur parsial ~50–60%, bukan alpha. Hanya PAXG dan MINA yang menang sambil untung.

---

## SETELAH 92 PAIR (91 teruji, 1 N/A)

**PF: rata-rata 0,914 · maks 1,220 (MINA) · min 0,654. Nol lolos screening.**
**Net: 23 positif, 68 negatif. Kalah dari B&H di 77 dari 91** (12 menang, 2 seri).

### Tiga false positive yang ditangkap aturan kedalaman data

Ini hasil terpenting dari batch #55–92. Tiga pair menunjukkan PF di atas ambang pada data dangkal, lalu runtuh begitu history diperdalam:

| Pair | PF data dangkal | PF data dalam | Selisih |
|---|---|---|---|
| DOGE | 1,301 @1.715 bar | 0,884 @3.215 bar | −0,417 |
| MINA | 1,368 @2.744 bar | **1,220** @3.994 bar | −0,148 |
| kBONK | 1,253 @1.995 bar | 0,992 @3.495 bar | −0,261 |

Arahnya selalu sama: **menambah data selalu menurunkan PF, tidak pernah menaikkannya.** Kalau ini edge nyata, penambahan data seharusnya membuat estimasinya makin stabil ke dua arah, bukan meluruh satu arah. Yang meluruh satu arah adalah noise yang sedang diukur terlalu optimistis.

Konsekuensi praktis: **PF yang diukur di bawah ~3.000 bar bisa 0,15–0,42 terlalu tinggi.** Angka di baris bertanda ⚠ pada tabel harus dibaca sebagai batas atas, bukan estimasi.

### Kandidat terbaik dari batch ini (semuanya gagal)

| Pair | Bar | PF | Net % | DD | B&H | Kenapa gagal |
|---|---|---|---|---|---|---|
| MINA | 3.994 | 1,220 | +86,43% | 30,8% | +16,1% | PF di bawah 1,25; paruh awal −17,07% |
| PAXG | 2.994 | 1,158 | +5,68% | 11,2% | −3,8% | PF & DD; hanya 48 trade |
| STX (HL) | 2.495 | 1,058 | +19,81% | 29,2% | +123,8% | PF; jauh di bawah B&H |

PAXG (emas) menarik secara kualitatif: DD-nya 11,2% — satu-satunya yang mendekati ambang 10% — kedua sisi positif, Sharpe +0,91. Tapi PF 1,158 dan cuma 48 trade. Kalau ada tempat strategi ini berperilaku waras, itu di instrumen bervolatilitas rendah dan bertren mulus, bukan di altcoin.

### "Mengalahkan B&H" tetap bukan alpha

12 pair kini mengalahkan B&H. **10 dari 12 tetap rugi uang** — mereka hanya rugi lebih sedikit daripada asetnya (USELESS −31,87% vs −53,1%; BLUR −4,68% vs −48,9%; kBONK −2,48% vs −50,8%; SOPH −38,57% vs −58,5%; POL −2,14% vs −19,4%). Itu efek beta rendah dari eksposur parsial ~50–60%, persis seperti yang sudah disimpulkan di #52. Hanya PAXG dan MINA yang menang sambil untung.

---

## SETELAH 54 PAIR (53 teruji, 1 N/A)

**PF: rata-rata 0,922 · maks 1,193 · min 0,654. Nol lolos.**
**Net: 16 positif, 37 negatif. Kalah dari B&H di 47 dari 53** (5 menang, 1 seri).

Pair 53–54: GRASS 0,802 (−66,18%, **DD 79,1%** — terburuk sepanjang sweep) · JUP 0,927 (−20,65%).

Lima drawdown terburuk sejauh ini, semuanya di pair berkedalaman penuh:

| Pair | DD | Net % | B&H |
|---|---|---|---|
| GRASS | **79,1%** | −66,18% | +80,1% |
| SPX | 73,2% | −69,16% | −11,1% |
| PONS | 69,0% | −56,95% | −15,2% |
| CRV | 63,1% | −55,81% | +56,3% |
| CHIP | 60,0% | −55,78% | +41,1% |

GRASS adalah contoh paling ekstrem: aset naik 80,1%, strategi rugi 66,18% dengan drawdown 79,1%. Selisihnya 146 poin persen di satu pair.

---

## SETELAH 52 PAIR (51 teruji, 1 N/A)

**PF: rata-rata 0,924 · maks 1,193 · min 0,654. Nol lolos.**
**Net: 16 positif, 35 negatif. Kalah dari B&H di 45 dari 51** (5 menang, 1 seri).

Pair 51–52: XLM 0,996 (−0,86%, **kalahkan B&H +18 pp**) · ZK 0,983 (−5,37%).

### Pola yang kini konsisten di kelima pair yang mengalahkan B&H

| Pair | Net strategi | B&H |
|---|---|---|
| MON | +35,40% | +2,2% |
| FARTCOIN | +14,33% | +3,3% |
| CASHCAT | +21,30% | −2,5% |
| **XLM** | **−0,86%** | **−18,9%** |
| STRK | +88,80% | +79,8% |

Empat dari lima terjadi di aset yang **tidak ke mana-mana atau turun**. XLM bahkan menang sambil tetap rugi — strateginya rugi 0,86%, asetnya rugi 18,9%.

Jadi "mengalahkan B&H" di sini bukan tanda alpha. Itu artinya: saat aset tidak naik, exposure parsial (50–85%) membuat strategi rugi lebih sedikit. Itu **efek beta rendah, bukan edge** — dan bisa didapat lebih murah hanya dengan memegang posisi lebih kecil.

---

## SETELAH 50 PAIR (49 teruji, 1 N/A) — SEPARUH JALAN

**PF: rata-rata 0,921 · maks 1,193 (STRK) · min 0,654 (TRX). Nol lolos.**
**Net: 16 positif, 33 negatif. Kalah dari B&H di 44 dari 49** (4 menang, 1 seri).

Pair 47–50: TRX 0,654 · DOT 0,987 · SEI 0,791 · SPX 0,733 (**−69,16%, DD 73,2%** — terburuk sepanjang sweep).

Tren rata-rata PF: 1,013 (15) → 0,996 (19) → 0,989 (25) → 0,973 (30) → 0,938 (35) → 0,931 (37) → 0,937 (39) → 0,940 (42) → 0,933 (45) → **0,921 (49)**.

### KOREKSI atas klaim saya di laporan #46

Di rekap 46 pair saya menulis: *"begitu sampelnya besar (>240 trade), hasilnya hampir selalu negatif tajam"*, dengan contoh CHIP, CRV, EIGEN, AERO.

**Klaim itu salah — saya memilih contoh yang mendukung.** Daftar lengkap pair dengan >280 trade:

| Pair | Trade | Net % |
|---|---|---|
| PUMP | 336 | **+93,31%** |
| STRK | 289 | **+88,80%** |
| ENA | 294 | **+39,24%** |
| ZEC | 287 | **+20,22%** |
| CHIP | 363 | −55,78% |
| CRV | 324 | −55,81% |
| SPX | 311 | −69,16% |
| WLD | 311 | −47,81% |
| EIGEN | 300 | −55,69% |
| AERO | 293 | −42,64% |

**6 negatif, 4 positif** — tidak ada hubungan yang bersih antara jumlah trade dan hasil. Klaim saya dicoret.

Yang benar-benar bertahan setelah 49 tes tetap yang sederhana: PF terpusat di bawah 1,0, tidak pernah mencapai 1,25, dan strategi kalah dari buy & hold di 90% pair.

---

## SETELAH 46 PAIR (45 teruji, 1 N/A) — hampir separuh

**PF: rata-rata 0,933 · maks 1,193 (STRK). Nol lolos.**
**Net: 16 positif, 29 negatif. Kalah dari B&H di 40 dari 45** (4 menang, 1 seri).

Pair 44–46: AERO 0,846 (−42,64%) · ALT 0,929 (−16,09%) · EIGEN 0,736 (−55,69%).

Batch ini semuanya berkedalaman penuh (~2.700–3.000 bar) dan semuanya negatif besar. EIGEN khususnya: **−55,69% dengan DD 59,2%** di aset yang justru naik 5,4%.

---

## SETELAH 43 PAIR (42 teruji, 1 N/A)

**PF: rata-rata 0,940 · maks 1,193 (STRK). Nol lolos.**
**Net: 16 positif, 26 negatif. Kalah dari B&H di 37 dari 42** (4 menang, 1 seri).

Pair 41–43, semuanya dengan kedalaman data bagus (~3.000 bar):
- **CHIP** 3.243 bar · 363 trade · −55,78% · PF 0,854 · DD 60,0% · B&H +41,1%
- **HBAR** 2.993 bar · 180 trade · −1,51% · PF 0,993 · DD 26,8% · B&H +2,9%
- **LTC** 2.993 bar · 154 trade · +11,90% · PF 1,083 · DD 20,5% · B&H +31,5%

---

## SETELAH 40 PAIR (39 teruji, 1 N/A)

**PF: rata-rata 0,937 · maks 1,193 (STRK). Nol lolos.**
**Net: 15 positif, 24 negatif. Kalah dari B&H di 34 dari 39** (4 menang, 1 seri).

Pair 39–40: BCH 0,942 · PENGU 1,131 (net +24,10% vs B&H +24,1% — seri persis).

Setelah **39 tes out-of-sample independen**, PF tertinggi masih 1,193 dan ambang 1,25 belum pernah tersentuh sekali pun.

---

## SETELAH 38 PAIR (37 teruji, 1 N/A)

**PF: rata-rata 0,931 · maks 1,193 (STRK). Nol lolos.**
**Net: 14 positif, 23 negatif. Kalah dari B&H di 33 dari 37.**

Pair 36–38: FET 0,929 · PRL ⬜ N/A (HIP-3, 89 bar) · ICP 0,715.

Tren rata-rata PF: 1,013 (15) → 0,996 (19) → 0,989 (25) → 0,973 (30) → 0,938 (35) → **0,931 (37)**.

**Catatan baru:** PRL adalah pasar **HIP-3** Hyperliquid, bukan perp standar — history-nya cuma 89 bar. Daftar 100 simbol Hyperliquid kemungkinan memuat beberapa pasar HIP-3 lain yang serupa; itu akan muncul sebagai N/A saat dicoba, bukan sebagai hasil.

---

## SETELAH 35 PAIR

**PF: rata-rata 0,938 · maks 1,193. Nol lolos.**
**Net: 14 positif, 21 negatif. Kalah dari B&H di 31 dari 35 pair.**

Pair 31–35: CASHCAT 1,027 (kalahkan B&H) · APT 0,833 · AAVE 0,942 · ADA 0,992 · PURR 0,839.

Tren rata-rata PF: 1,013 (15) → 0,996 (19) → 0,989 (25) → 0,973 (30) → **0,938 (35)**. Turun terus, tanpa pernah berbalik.

---

## SETELAH 30 PAIR — sepertiga jalan

**PF: rata-rata 0,973 · median 0,954 · min 0,656 · maks 1,193. Nol lolos (butuh ≥ 1,25).**
**Net: 13 positif, 17 negatif. Kalah dari B&H di 27 dari 30 pair.**

Distribusi PF seluruh 30 pair, diurutkan:

```
1,193 1,169 1,160 1,160 1,149 1,136 1,085 1,070 1,069 1,063
1,063 1,046 1,002 0,977 0,961 0,946 0,944 0,943 0,934 0,929
0,909 0,884 0,879 0,866 0,837 0,823 0,807 0,760 0,758 0,656
```

Tidak satu pun menyentuh 1,25. Nilai tertinggi (STRK 1,193) masih 5% di bawah ambang, dan itu pun dicapai dengan DD 36,4%.

**Rata-rata PF terus meluruh seiring sampel bertambah:** 1,013 (15 pair) → 0,996 (19) → 0,989 (25) → **0,973 (30)**. Arahnya konsisten satu arah, ke bawah 1,0.

Catatan soal tiga pair yang mengalahkan B&H: dua dari tiga adalah aset yang **B&H-nya mendekati nol** (MON +2,2%, FARTCOIN +3,3%; STRK +79,8% pengecualian). Strategi menang di sana bukan karena menghasilkan alpha, tapi karena ketika aset bergerak menyamping, kelemahan utamanya — tertinggal dari aset karena exposure parsial dan biaya — tidak terhukum. Di aset yang naik kuat (ARB +106%, UNI +89%, AVAX +52%, CRV +56%), strategi selalu kalah telak.

Sebaran PF makin sempit seiring bertambahnya sampel, dan rata-ratanya kini duduk tepat di **0,996 — secara praktis 1,0**. Itu persis yang diharapkan kalau edge sebenarnya nol.

Statistik yang paling tajam sekarang bukan PF, tapi perbandingan terhadap B&H: **18 dari 19 pair kalah dari beli-dan-diam.** Kalau sinyalnya sekadar acak, kita akan mengharapkan sekitar separuh menang. Kalah 18 dari 19 berarti strategi ini **secara sistematis lebih buruk daripada tidak melakukan apa-apa** — biaya transaksi dan exposure parsial (50–85%) membuatnya tertinggal dari asetnya sendiri.

---

## Rincian lama — 13 pair

Diurutkan dari PF tertinggi. Angka SUI dan DOGE sudah dikoreksi ke kedalaman data penuh.

| Pair | Bar | Net % | PF | DD | B&H | Kalahkan B&H? |
|---|---|---|---|---|---|---|
| STRK | 2.962 | +88,80% | **1,193** | 36,4% | +79,8% | ✅ (+9,0 pp) |
| PUMP | 2.962 | +93,31% | 1,160 | 23,8% | +190,5% | ❌ (−97,2 pp) |
| ZRO | 1.465 | +56,84% | 1,149 | 39,2% | +139,1% | ❌ (−82,3 pp) |
| ENA | 2.965 | +39,24% | 1,085 | 34,1% | +118,3% | ❌ (−79,1 pp) |
| SUI | 2.215 | +12,68% | 1,069 | 18,2% | +32,7% | ❌ (−20,0 pp) |
| TIA | 1.965 | +11,67% | 1,046 | 25,4% | +90,6% | ❌ (−78,9 pp) |
| XRP | 2.465 | −3,37% | 0,977 | 32,6% | +14,7% | ❌ |
| LIT | 1.965 | −16,40% | 0,946 | 38,4% | +42,5% | ❌ |
| XPL | 1.715 | −14,82% | 0,929 | 28,9% | +3,6% | ❌ |
| DOGE | 3.215 | −15,80% | 0,884 | 40,9% | −2,5% | ❌ |
| XMR | 2.965 | −26,27% | 0,879 | 35,8% | +67,5% | ❌ |
| WLD | 2.965 | −47,81% | 0,866 | 63,5% | −25,0% | ❌ |
| PYTH | 1.715 | −36,79% | 0,837 | 51,3% | +103,0% | ❌ |

**PF: rata-rata 1,002 · median 0,977 · min 0,837 · maks 1,193.**
**Net %: 6 positif, 7 negatif. Nol lolos screening** (butuh PF ≥ 1,25).
**Kalah dari buy & hold di 12 dari 13 pair.** Satu-satunya yang menang (STRK) menang 9 poin persen sambil menanggung DD 36,4%.

### Aturan asimetris untuk kedalaman data (ditetapkan di #12)

Pair yang **LOLOS** di bar sub-standar **wajib diperdalam** sebelum dicatat (ini yang menangkap DOGE). Pair yang **GAGAL** dicatat apa adanya dengan jumlah barnya dicantumkan. Risiko kesalahan hanya satu arah — false positive — dan menambah data sejauh ini selalu menurunkan PF, tidak pernah menaikkan.

### Satu pair sempat lolos, lalu runtuh

DOGE keluar **PF 1,301** di 1.715 bar — melewati ambang, mengalahkan B&H, kedua sisi positif. Di 3.215 bar jadi **PF 0,884 / −15,80%**. SUI bergerak ke arah yang sama (1,121 → 1,069) saat datanya ditambah.

Dua pengamatan ini bersama-sama menunjukkan sesuatu yang spesifik: **PF strategi ini meluruh menuju 1,0 seiring bertambahnya data.** Itu persis yang diharapkan dari sistem tanpa edge, dan kebalikan dari apa yang terjadi pada edge nyata (yang PF-nya justru stabil atau mengetat di sekitar nilai > 1 saat sampel membesar).

### Kenapa pola ini sudah bermakna secara statistik

Sebelas tes out-of-sample independen dengan konfigurasi identik. PF terpusat di **1,003** dengan sebaran sempit (0,84–1,19), sementara net % tersebar sangat lebar (−47,8% s/d +93,3%).

Kalau sinyalnya membawa informasi, PF akan konsisten di atas 1 lintas aset dan net % akan mengikuti PF. Yang terjadi sebaliknya — PF ≈ 1,0 di mana-mana, dan net % semata-mata mengikuti tren asetnya. PYTH adalah contoh paling tajam: aset naik 103%, strategi rugi 36,79%.

**Catatan anti-bias:** prediksi awal saya ("PF tidak akan keluar dari 0,85–1,20") dilanggar oleh DOGE di window pendek. Saya tidak membuangnya sebagai noise — saya tambah datanya, dan barulah runtuh. Itu urutan yang benar. Prediksi tidak boleh dipakai untuk menolak data; hanya data yang boleh menolak data.

---

## TEMUAN SEMENTARA setelah 2 pair (penting — baca sebelum lanjut)

Dua pair Hyperliquid pertama berperilaku **jelas berbeda** dari semua yang diuji di Binance:

| | PF | avg trade | Long | Short |
|---|---|---|---|---|
| PUMP (HL) | **1,160** | **+$27,8** | +$7.595,7 | **+$1.734,9** |
| STRK (HL) | **1,193** | **+$30,7** | +$8.532,5 | **+$347,8** |
| HYPE (Binance) | 0,997 | −$0,3 | +$268,1 | −$321,4 |
| BTC (Binance) | 0,762 | −$22,5 | −$255,0 | −$1.881,5 |
| ZEC (Binance) | 1,053 | +$7,0 | +$5.266,9 | −$3.245,4 |

Tiga hal baru:
1. **PF naik ke 1,16–1,19**, tertinggi dari seluruh pekerjaan ini (sebelumnya plafon 1,058).
2. **Kedua sisi positif.** Di semua pair Binance short selalu berdarah. Di PUMP dan STRK short ikut untung. Ini diagnostik yang saya tetapkan sebagai pembeda "edge" vs "beta" — dan baru di sini terpenuhi.
3. **STRK mengalahkan buy & hold** (+88,80% vs +79,8%) — pertama kalinya.

Mekanismenya konsisten dengan teori `cost/R`: aset ini bergerak jauh lebih besar per bar, jadi biaya round-trip ~0,053% notional menjadi tidak berarti relatif R. Avg trade melonjak dari −$0,3 (HYPE) ke +$30,7 (STRK).

**Keduanya tetap gagal screening** karena PF < 1,25 dan DD 24–36%.

### Koreksi metodologi: DD bukan kriteria yang mengikat, PF yang mengikat

DD **skalanya ikut ukuran posisi**; PF **tidak**. Mengecilkan `margin_pct` dengan faktor k mengecilkan net% dan DD% sama-sama ~k, tapi PF tetap.

Contoh PUMP: net +93,31% / DD 23,8%. Dengan k = 10/23,8 = 0,42 (margin_pct 20 → ~8,4), hasilnya jadi net **+39,2% dengan DD ~10%** dan PF tetap 1,160.

Artinya kriteria "DD < 10%" selalu bisa dipenuhi dengan sizing dan **tidak membuktikan apa pun tentang edge**. Untuk sisa sweep: **screening utama = PF**, DD dicatat apa adanya lalu dinormalisasi belakangan. Kandidat yang lolos tetap harus menang risk-adjusted terhadap B&H.

---

## Antrean kerja — HYPERLIQUID.F, 95 pair

Urutan mengikuti ranking keaktifan platform (paling likuid dulu). BTC/ETH/HYPE/ZEC/SOL dikeluarkan karena sudah diuji.

| # | Pair | Bar | Trade | Win% | Net % | PF | Max DD | B&H | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | PUMP | 2.962 | 336 | 46,1% | +93,31% | **1,160** | 23,8% | +190,5% | ❌ PF<1,25; DD; kalah B&H |
| 2 | STRK | 2.962 | 289 | 44,3% | +88,80% | **1,193** | 36,4% | +79,8% | ❌ PF<1,25; DD — **tapi kalahkan B&H** |
| 3 | XRP | 2.465 | 137 | 41,6% | −3,37% | 0,977 | 32,6% | +14,7% | ❌ |
| 4 | SUI | **2.215** | 170 | 44,1% | +12,68% | 1,069 | 18,2% | +32,7% | ❌ (di 1.715 bar: +20,92% / PF 1,121 — turun setelah history ditambah) |
| 5 | XMR | 2.965 | 218 | 39,0% | −26,27% | 0,879 | 35,8% | +67,5% | ❌ |
| 6 | WLD | 2.965 | 311 | 39,9% | −47,81% | 0,866 | 63,5% | −25,0% | ❌ |
| 7 | XPL | 1.715 | 180 | 42,2% | −14,82% | 0,929 | 28,9% | +3,6% | ❌ |
| 8 | TIA | 1.965 | 189 | 46,0% | +11,67% | 1,046 | 25,4% | +90,6% | ❌ |
| 9 | ENA | 2.965 | 294 | 45,2% | +39,24% | 1,085 | 34,1% | +118,3% | ❌ |
| 10 | PYTH | 1.715 | 175 | 38,3% | −36,79% | 0,837 | 51,3% | +103,0% | ❌ |
| 11 | DOGE | **3.215** | 179 | 40,8% | −15,80% | 0,884 | 40,9% | −2,5% | ❌ (di 1.715 bar sempat +30,30% / PF 1,301 — runtuh total setelah history ditambah) |
| 12 | ZRO | 1.465 | 173 | 46,2% | +56,84% | 1,149 | 39,2% | +139,1% | ❌ (bar sub-standar, tapi sudah gagal PF) |
| 13 | LIT | 1.965 | 207 | 39,6% | −16,40% | 0,946 | 38,4% | +42,5% | ❌ |
| 14 | INJ | 1.966 | 196 | 42,9% | +0,61% | 1,002 | 22,4% | +85,0% | ❌ |
| 15 | LINK | 1.716 | 131 | 47,3% | +22,82% | 1,169 | 17,2% | +46,4% | ❌ (kedua sisi +) |
| 16 | KPEPE | 1.466 | 127 | 34,6% | −41,46% | 0,656 | 43,6% | +51,4% | ❌ PF terendah |
| 17 | ONDO | 1.216 | 111 | 42,3% | −7,67% | 0,944 | 30,7% | +22,9% | ❌ |
| 18 | SAND | 1.716 | 160 | 45,0% | +14,85% | 1,070 | 21,5% | +56,5% | ❌ |
| 19 | FIL | 1.716 | 170 | 45,3% | +13,93% | 1,063 | 27,5% | +54,1% | ❌ |
| 20 | ARB | 1.216 | 132 | 37,1% | −20,45% | 0,909 | 46,0% | +106,0% | ❌ |
| 21 | UNI | 1.966 | 195 | 40,5% | −8,67% | 0,961 | 32,6% | +89,4% | ❌ |
| 22 | MON | 1.716 | 178 | 46,1% | +35,40% | 1,160 | 42,1% | **+2,2%** | ❌ PF — **kalahkan B&H (+33 pp)** |
| 23 | TAO | 1.216 | 114 | 41,2% | −7,34% | 0,943 | 24,5% | +13,3% | ❌ |
| 24 | PONS | 1.158 | 117 | 34,2% | −56,95% | 0,760 | **69,0%** | −15,2% | ❌ DD terburuk |
| 25 | FARTCOIN | 1.466 | 150 | 44,0% | +14,33% | 1,063 | 26,3% | **+3,3%** | ❌ PF — **kalahkan B&H**, kedua sisi + |
| 26 | AVAX | 1.716 | 130 | 36,2% | −29,31% | 0,758 | 34,9% | +51,8% | ❌ |
| 27 | NIL | 966 | 96 | 43,8% | +36,38% | 1,136 | 36,6% | +50,4% | ❌ |
| 28 | CRV | **3.466** | 324 | 37,3% | −55,81% | 0,823 | 63,1% | +56,3% | ❌ |
| 29 | VVV | 1.216 | 143 | 41,3% | −13,76% | 0,934 | 32,3% | +29,5% | ❌ |
| 30 | BNB | 1.217 | 51 | 37,3% | −9,15% | 0,807 | 19,2% | +3,8% | ❌ |
| 31 | CASHCAT | 1.467 | 167 | 41,9% | +21,30% | 1,027 | 51,0% | **−2,5%** | ❌ PF — kalahkan B&H; GP/GL $81k/$79k |
| 32 | APT | 967 | 96 | 38,5% | −20,48% | 0,833 | 35,6% | +24,7% | ❌ |
| 33 | AAVE | 1.467 | 129 | 40,3% | −7,34% | 0,942 | 24,8% | +71,7% | ❌ |
| 34 | ADA | 1.467 | 130 | 42,3% | −1,05% | 0,992 | 28,7% | +26,2% | ❌ |
| 35 | PURR | 1.467 | 148 | 40,5% | −28,30% | 0,839 | 50,4% | +21,0% | ❌ |
| 36 | FET | 1.717 | 180 | 42,8% | −13,20% | 0,929 | 37,0% | +42,0% | ❌ |
| 37 | PRL | 89 | 0 | — | — | — | — | −4,5% | ⬜ N/A — pasar HYPERLIQUID **HIP-3**, history hanya 89 bar, 0 trade. Tidak dapat diuji. |
| 38 | ICP | 1.467 | 139 | 34,5% | −36,94% | 0,715 | 47,6% | +28,4% | ❌ |
| 39 | BCH | 1.217 | 92 | 39,1% | −5,48% | 0,942 | 20,1% | +10,6% | ❌ |
| 40 | PENGU | 1.467 | 146 | 45,9% | +24,10% | 1,131 | 22,4% | +24,1% | ❌ (seri dgn B&H) |
| 41 | CHIP | **3.243** | 363 | 39,4% | −55,78% | 0,854 | 60,0% | +41,1% | ❌ |
| 42 | HBAR | **2.993** | 180 | 41,7% | −1,51% | 0,993 | 26,8% | +2,9% | ❌ |
| 43 | LTC | **2.993** | 154 | 43,5% | +11,90% | 1,083 | 20,5% | +31,5% | ❌ |
| 44 | AERO | 2.993 | 293 | 38,6% | −42,64% | 0,846 | 46,0% | +71,8% | ❌ |
| 45 | ALT | 2.993 | 246 | 40,7% | −16,09% | 0,929 | 35,4% | +28,9% | ❌ |
| 46 | EIGEN | 2.743 | 300 | 37,3% | −55,69% | 0,736 | 59,2% | +5,4% | ❌ |
| 47 | TRX | 2.993 | 43 | 30,2% | −12,57% | 0,654 | 17,9% | +4,7% | ❌ vol terlalu rendah utk stop floor 1,5% — exposure 90,2%, cuma 43 trade |
| 48 | DOT | 2.993 | 247 | 42,5% | −3,20% | 0,987 | 29,2% | +9,5% | ❌ |
| 49 | SEI | 2.743 | 204 | 37,7% | −34,18% | 0,791 | 37,4% | +14,5% | ❌ |
| 50 | SPX | 2.993 | 311 | 34,4% | **−69,16%** | 0,733 | **73,2%** | −11,1% | ❌ net & DD terburuk |
| 51 | XLM | 2.993 | 216 | 43,1% | −0,86% | 0,996 | 20,6% | **−18,9%** | ❌ PF — **kalahkan B&H** (+18 pp) |
| 52 | ZK | 2.993 | 305 | 42,0% | −5,37% | 0,983 | 38,9% | +30,1% | ❌ |
| 53 | GRASS | **3.244** | 354 | 38,7% | −66,18% | 0,802 | **79,1%** | +80,1% | ❌ DD terburuk |
| 54 | JUP | 2.994 | 287 | 40,4% | −20,65% | 0,927 | 45,7% | +54,3% | ❌ |
| 55 | ASTER | 494 ⚠ | 25 | 36,0% | −5,87% | 0,771 | 9,4% | −0,8% | ❌ PF — data cuma 494 bar (listing baru), sampel terlalu kecil |
| 56 | USELESS | 981 ⚠ | 103 | 40,8% | −31,87% | 0,791 | **59,6%** | −53,1% | ❌ — "kalahkan" B&H (+21 pp) tapi tetap rugi |
| 57 | TRUMP | 2.994 | 230 | 40,0% | −27,95% | 0,883 | 36,4% | −10,8% | ❌ |
| 58 | W | 2.994 | 289 | 44,6% | **+7,79%** | 1,019 | **41,5%** | +29,3% | ❌ PF & DD — net positif tapi kalah B&H |
| 59 | ETHFI | 2.994 | 318 | 38,4% | −38,76% | 0,904 | **55,7%** | +103,1% | ❌ short −$6.494 di tren naik |
| 60 | BLUR | 2.994 | 264 | 42,4% | −4,68% | 0,980 | **43,2%** | −48,9% | ❌ — "kalahkan" B&H (+44 pp) tapi tetap rugi |
| 61 | ALGO | 2.994 | 241 | 38,6% | −33,35% | 0,835 | 38,5% | +15,9% | ❌ |
| 62 | PAXG | 2.994 | 48 | 47,9% | **+5,68%** | **1,158** | 11,2% | −3,8% | ❌ PF<1,25, DD>10%, trade<60 — **tapi near-miss terbaik sejauh ini**: kedua sisi positif (L +$167 / S +$401), Sharpe +0,91, kalahkan B&H. Emas = tren mulus, vol rendah |
| 63 | GRAM | 2.620 | 158 | 39,9% | −23,21% | 0,849 | 34,0% | −20,0% | ❌ |
| 64 | POL | 2.994 | 222 | 42,8% | −2,14% | 0,992 | **43,5%** | −19,4% | ❌ PF & DD |
| 65 | **MINA** | **3.994** | 360 | 45,0% | **+86,43%** | **1,220** | 30,8% | +16,1% | ❌ **sempat PF 1,368 @2.744 bar, luruh ke 1,220 @3.994 bar.** Protokol penuh dijalankan → gugur. Lihat bagian khusus di bawah |
| 66 | PENDLE | 2.994 | 320 | 38,4% | −44,57% | 0,849 | **48,6%** | +87,3% | ❌ |
| 67 | ETC | 2.994 | 171 | 43,3% | −2,51% | 0,984 | 22,1% | +4,4% | ❌ |
| 68 | APE | 2.994 | 263 | 42,2% | −26,41% | 0,904 | **40,3%** | +13,3% | ❌ |
| 69 | OP | 2.994 | 284 | 43,3% | **+10,34%** | 1,031 | 31,0% | +15,7% | ❌ PF & DD — net positif tapi kalah B&H |
| 70 | LDO | 2.995 | 303 | 42,2% | +0,88% | 1,003 | **39,2%** | +42,4% | ❌ |
| 71 | JTO | 2.995 | 333 | 38,7% | −59,22% | 0,787 | **68,5%** | −43,8% | ❌ DD terburuk ke-3 |
| 72 | RSR | 2.950 | 256 | 37,5% | −44,54% | 0,800 | **51,3%** | +28,8% | ❌ |
| 73 | CAKE | 2.995 | 210 | 38,6% | −28,95% | 0,812 | **44,5%** | +54,3% | ❌ |
| 74 | MEGA | 1.995 ⚠ | 208 | 43,8% | **+9,20%** | 1,041 | 28,8% | +9,7% | ❌ PF & DD — listing baru, data 1.995 bar |
| 75 | GRIFFAIN | 1.995 ⚠ | 204 | 45,6% | −11,99% | 0,965 | **51,4%** | +78,8% | ❌ |
| 76 | APEX | 1.995 ⚠ | 195 | 37,9% | −46,77% | 0,773 | **56,2%** | −17,8% | ❌ |
| 77 | kBONK | **3.495** | 330 | 43,6% | −2,48% | 0,992 | **57,2%** | −50,8% | ❌ — **PF 1,253 @1.995 bar → 0,992 @3.495 bar.** False positive ke-3 yang tertangkap aturan kedalaman |
| 78 | WIF | 2.495 ⚠ | 216 | 40,3% | −28,70% | 0,850 | 37,4% | +18,1% | ❌ |
| 79 | STX | 2.495 ⚠ | 245 | 42,9% | **+19,81%** | 1,058 | 29,2% | +123,8% | ❌ PF — bandingkan BINANCE.F STX (PF 1,193 @2.962 bar): venue beda, keduanya tetap di bawah ambang |
| 80 | MORPHO | 2.495 ⚠ | 234 | 35,9% | −56,01% | **0,695** | **57,5%** | +23,0% | ❌ PF terburuk ke-2 |
| 81 | MET | 2.495 ⚠ | 254 | 36,2% | −57,11% | 0,733 | **64,7%** | +103,9% | ❌ |
| 82 | BERA | 2.495 ⚠ | 262 | 42,4% | −20,47% | 0,922 | **40,1%** | −20,5% | ❌ |
| 83 | SKY | 2.495 ⚠ | 219 | 41,6% | −11,59% | 0,939 | 32,2% | +25,5% | ❌ |
| 84 | SYRUP | 2.495 ⚠ | 230 | 39,1% | −36,26% | 0,825 | **47,4%** | +8,9% | ❌ |
| 85 | INIT | 2.495 ⚠ | 216 | 39,8% | −29,89% | 0,860 | **42,0%** | +124,4% | ❌ short −$3.349 di tren naik |
| 86 | CC | 2.495 ⚠ | 226 | 38,5% | −33,89% | 0,828 | **39,4%** | −21,3% | ❌ |
| 87 | RENDER | 2.495 ⚠ | 199 | 42,2% | −11,51% | 0,945 | 27,3% | +12,7% | ❌ |
| 88 | SOPH | 2.486 ⚠ | 191 | 42,4% | −38,57% | 0,832 | **56,9%** | −58,5% | ❌ |
| 89 | AR | 2.495 ⚠ | 210 | 39,0% | −28,83% | 0,882 | 36,9% | +89,1% | ❌ |
| 90 | AZTEC | 1.995 ⚠ | 176 | 43,2% | −11,00% | 0,954 | 32,2% | +35,3% | ❌ |
| 91 | STBL | 1.995 ⚠ | 178 | 37,6% | −47,34% | 0,728 | **53,6%** | −0,8% | ❌ |
| 92 | USUAL | 1.995 ⚠ | 192 | 42,2% | −12,46% | 0,938 | **48,9%** | +28,0% | ❌ |
| 93 | WLFI | 3.006 | 173 | 32,9% | −56,56% | **0,587** | **57,4%** | −10,0% | ❌ **PF terburuk sepanjang sweep**, win rate terendah (32,9%) |
| 94 | VIRTUAL | 3.006 | 271 | 41,0% | −13,98% | 0,947 | **40,0%** | +6,4% | ❌ — **SWEEP SELESAI** |
| 95 | ~~MORPHO~~ | — | — | — | — | — | — | — | DUPLIKAT dari #80, tidak diuji ulang |

---

## BATCH 2 — Pair khusus Binance (39)

Tidak ada di Hyperliquid, jadi hanya bisa diuji di **BINANCE.F**. Dimulai 2026-10-20 atas permintaan eksplisit setelah batch 1 selesai.

### PROTOKOL BATCH 2 — ditetapkan SEBELUM pair pertama dibuka

Batch ini adalah **39 tes independen baru**, jadi beban multiple-testing-nya dihitung terpisah dan dicatat di muka:

> **Ekspektasi null: dengan 39 tes pada peluang ~5% terlihat bagus karena kebetulan, perkiraan jumlah "pemenang" semu adalah ~2.**
> Artinya: menemukan 1–2 pair dengan PF ≥ 1,25 di batch ini adalah **hasil yang diharapkan kalau strateginya tidak punya edge sama sekali**. Itu bukan temuan. Yang akan jadi temuan adalah menemukan **lebih banyak** dari itu, atau menemukan satu yang bertahan melewati protokol penuh.

Aturan yang tidak berubah dari batch 1 (sengaja tidak digeser — menggeser ambang setelah melihat hasil adalah persis cara menipu diri sendiri yang coba dicegah protokol ini):

1. **Ambang tetap PF ≥ 1,25** · DD < 10% · ≥60 trade · net > 0 · kedua sisi tidak berdarah · kalahkan B&H risk-adjusted.
2. **Catat SEMUA hasil**, bukan hanya yang positif.
3. **Aturan kedalaman data asimetris** — terbukti menyelamatkan 3 false positive di batch 1 (DOGE, MINA, kBONK):
   - Pair yang **lolos** PF di <2.900 bar **wajib diperdalam** dulu sebelum dicatat.
   - Pair yang **gagal** dicatat apa adanya dengan jumlah bar ditandai ⚠.
4. **Parameter tidak dituning ulang per pair.** Konfigurasi wide-R yang sama: `min_risk_pct 1,5` · `max_hold 96` · `be_trigger_r 8` · `rr 1,5` · `pull_atr 0,5` · `stop_atr 1,0` · `fast 20`/`slow 100`/`atr 14` · `entry_ttl 3` · maker 0,02 / taker 0,045 / slip 2.
5. **Kandidat yang lolos screening** dijalankan protokol penuh: split tuning/validation, stress test (maker 0,05 / slip 5), tetangga parameter ±20%, tes buang-trade-terbesar.

Catatan venue: batch 1 di HYPERLIQUID.F, batch 2 di BINANCE.F. Cross-check STX di kedua venue memberi PF 1,193 (Binance) vs 1,058 (Hyperliquid) — venue menggeser angka sekitar 0,13, jadi **PF batch 2 tidak langsung sebanding dengan batch 1** dan tidak digabung ke rata-rata batch 1.

### ✅ BATCH 2 SELESAI — 39 dari 39 (2026-10-20)

| Metrik | Nilai |
|---|---|
| **Lolos screening** | **0 dari 39** |
| PF rata-rata | **0,914** |
| PF maks / min | **1,300 (CYS)** / 0,567 (Q) |
| Net positif / negatif | 12 / 27 |
| Mengalahkan B&H | 8 (hanya 4 di antaranya untung) |

Ekspektasi null yang dicatat di muka: ~2 pemenang semu dari 39 tes. Yang muncul: **satu kandidat yang PF-nya bertahan di atas ambang (CYS 1,300)** — lalu gugur di split waktu dan kriteria DD. Lihat bagian khusus B37 CYS di bawah.

#### Peluruhan PF — kini 7 konfirmasi, tetap satu arah

| Pair | PF dangkal | PF dalam | Δ | Mendarat |
|---|---|---|---|---|
| DOGE | 1,301 @1.715 | 0,884 @3.215 | −0,417 | di bawah |
| MINA | 1,368 @2.744 | 1,220 @3.994 | −0,148 | di bawah |
| kBONK | 1,253 @1.995 | 0,992 @3.495 | −0,261 | di bawah |
| RLC | 1,2435 @2.757 | 1,109 @4.257 | −0,134 | di bawah |
| ZIL | 1,2065 @2.507 | 1,140 @4.007 | −0,066 | di bawah |
| MAGIC | 1,2428 @2.757 | 1,109 @4.507 | −0,134 | di bawah |
| **CYS** | **1,370 @2.758** | **1,300 @4.508** | **−0,070** | **di atas** |

**Tujuh dari tujuh turun. Nol naik.** Kalau penambahan data hanya menambah presisi pada estimasi yang benar, arahnya akan acak. Satu arah konsisten = yang diukur di window pendek adalah noise optimistis.

CYS adalah satu-satunya yang mendarat di atas 1,25 — dan tetap gugur, tapi karena alasan lain (split waktu + DD), bukan karena peluruhan.

#### Ambang tidak digeser — dan itu menentukan di tiga kasus

RLC (1,2435) dan MAGIC (1,2428) masing-masing hanya ~0,007 di bawah 1,25. Keduanya diperdalam meski aturan hanya mewajibkannya untuk pair yang *lolos* — karena membiarkan pembulatan memutuskan adalah persis cara menipu diri sendiri yang coba dicegah protokol ini. Keduanya luruh ke 1,109.

#### AKE — ilustrasi paling tajam kenapa net % menyesatkan

Net **+319,40%**, terlihat seperti temuan besar. PF-nya **1,061** dan B&H-nya **+8.225,6%**. Strategi ini menangkap sekitar 4% dari yang diberikan beli-dan-diam, sambil menanggung DD 69,9%. Net % tinggi di aset yang naik 82× bukan bukti edge — itu bukti leverage di tren.

#### Pola batch 2: sisi short dihancurkan listing momentum

Banyak pair Binance-only adalah listing baru bermomentum ekstrem (Q +567%, AGT +563%, BTW +3.114%, AKE +8.226%, PROM +340%, MUBARAK +344%). Di semuanya sisi short berdarah besar — AGT −$5.654, BTW −$10.468, 龙虾 −$8.220, PROM −$8.099. DD terburuk seluruh proyek semuanya muncul di batch ini: 龙虾 93,3% · US 90,9% · Q 90,1% · BR 87,0% · AGT 82,4%.

### Antrean batch 2

| # | Pair | Bar | Trade | Win% | Net % | PF | Max DD | B&H | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| B1 | Q | 3.006 | 261 | 33,3% | **−82,02%** | **0,567** | **90,1%** | +566,7% | ❌ **terburuk seluruh proyek** — DD 90,1%, tertinggal 649 pp dari B&H |
| B2 | AGT | 3.006 | 286 | 38,1% | −59,72% | 0,830 | **82,4%** | +563,2% | ❌ short −$5.654 di tren +563% |
| B3 | BTW | 3.006 | 306 | 46,1% | −64,33% | 0,931 | **77,8%** | **+3.113,5%** | ❌ short −$10.468; tertinggal ~3.178 pp dari B&H |
| B4 | ICNT | 3.006 | 312 | 46,8% | **+82,39%** | **1,155** | **35,6%** | −8,2% | ❌ PF & DD — **tapi kalahkan B&H +90 pp sambil untung**, kedua sisi positif (L +$6.948 / S +$1.291), Sharpe +1,97. Pair ke-3 di proyek ini yang menang B&H sambil untung |
| B5 | GTC | 3.006 | 282 | 47,9% | **+105,53%** | 1,147 | **56,1%** | +315,3% | ❌ PF & DD; tertinggal 210 pp dari B&H |
| B6 | BR | 3.006 | 313 | 39,3% | **−79,88%** | 0,727 | **87,0%** | +275,4% | ❌ DD terburuk ke-2 |
| B7 | 1000PEPE | 3.006 | 261 | 40,6% | −23,31% | 0,923 | **44,8%** | +40,7% | ❌ |
| B8 | AVA | 3.006 | 286 | 47,6% | **+22,06%** | 1,044 | **49,7%** | +109,5% | ❌ PF & DD |
| B9 | SIREN | 3.006 | 275 | 41,5% | −46,84% | 0,856 | **58,8%** | −52,1% | ❌ |
| B10 | EPIC | 3.006 | 305 | 42,0% | −33,55% | 0,923 | **65,0%** | −62,6% | ❌ |
| B11 | ERA | 3.007 | 272 | 41,5% | −17,82% | 0,943 | 38,9% | −30,1% | ❌ — "kalahkan" B&H (+12 pp) tapi tetap rugi |
| B12 | QNT | 3.007 | 196 | 42,3% | +4,55% | 1,019 | 33,1% | +170,4% | ❌ |
| B13 | BAT | 2.757 ⚠ | 229 | 42,4% | +5,92% | 1,022 | 22,8% | +125,0% | ❌ |
| B14 | ZEREBRO | 2.757 ⚠ | 280 | 41,4% | −50,04% | 0,852 | **52,8%** | −28,9% | ❌ |
| B15 | LSK | 2.757 ⚠ | 215 | 40,0% | **−80,07%** | 0,670 | **80,2%** | +114,0% | ❌ |
| B16 | A (Vaulta) | 3.007 | 273 | 41,8% | −13,34% | 0,958 | 37,9% | +23,5% | ❌ |
| B17 | 龙虾 (Lobster) | 3.007 | 280 | 38,9% | **−90,22%** | 0,775 | **93,3%** | +16,4% | ❌ **net & DD terburuk seluruh proyek**; short −$8.220 |
| B18 | WAL (Walrus) | 2.757 ⚠ | 275 | 45,1% | **+26,31%** | 1,080 | 30,1% | +14,0% | ❌ PF & DD — kalahkan B&H +12 pp sambil untung, kedua sisi positif |
| B19 | APR | 2.757 ⚠ | 276 | 38,4% | −69,69% | 0,814 | **78,9%** | −85,8% | ❌ |
| B20 | AKE | 2.757 ⚠ | 250 | 45,2% | **+319,40%** | 1,061 | **69,9%** | **+8.225,6%** | ❌ **contoh terbaik kenapa net % menyesatkan**: net +319% terlihat spektakuler, tapi PF 1,061 dan hanya menangkap ~4% dari yang diberikan beli-dan-diam |
| B21 | DUSK | 2.757 ⚠ | 271 | 44,3% | **+39,19%** | 1,129 | 30,1% | +52,9% | ❌ PF & DD |
| B22 | NMR | 2.757 ⚠ | 175 | 38,9% | −9,44% | 0,951 | 38,6% | +25,5% | ❌ |
| B23 | RLC | **4.257** | 353 | 42,8% | **+38,33%** | **1,109** | **44,8%** | +52,7% | ❌ — **PF 1,2435 @2.757 bar → 1,109 @4.257 bar.** Peluruhan ke-4 yang tertangkap aturan kedalaman (setelah DOGE, MINA, kBONK) |
| B24 | CT | 451 ⚠ | 38 | 34,2% | −35,80% | 0,632 | **52,5%** | −20,4% | ❌ listing baru, sampel terlalu kecil (38 trade) |
| B25 | PROM | 2.757 ⚠ | 250 | 43,2% | −47,11% | 0,883 | **68,1%** | +339,5% | ❌ short −$8.099 di tren +340% |
| B26 | US (Talus) | 2.757 ⚠ | 258 | 40,3% | **−76,88%** | 0,825 | **90,9%** | −62,3% | ❌ DD terburuk ke-2 |
| B27 | MUBARAK | 2.257 ⚠ | 213 | 42,7% | −17,61% | 0,951 | **72,2%** | +344,4% | ❌ |
| B28 | AVAAI | 2.007 ⚠ | 175 | 40,6% | −24,57% | 0,919 | **43,0%** | +0,4% | ❌ |
| B29 | ZIL | **4.007** | 353 | 45,9% | **+60,24%** | **1,140** | 27,6% | −51,8% | ❌ — **PF 1,207 @2.507 bar → 1,140 @4.007 bar; DD 18,3% → 27,6%.** Peluruhan ke-5. Kedua sisi positif, kalahkan B&H +112 pp sambil untung |
| B30 | MAGIC | **4.507** | 388 | 44,6% | **+46,06%** | **1,109** | 34,2% | +56,5% | ❌ — **PF 1,2428 @2.757 bar → 1,109 @4.507 bar.** Peluruhan ke-6 |
| B31 | FOLKS | 1.507 ⚠ | 135 | 37,0% | −36,39% | 0,750 | **50,4%** | +29,6% | ❌ |
| B32 | TRUTH | 2.007 ⚠ | 116 | 42,2% | −9,19% | 0,934 | 25,5% | +36,3% | ❌ |
| B33 | BASED | 2.757 ⚠ | 264 | 41,3% | −33,73% | 0,887 | **52,8%** | −29,7% | ❌ |
| B34 | 1000SHIB | 2.758 ⚠ | 189 | 39,2% | −26,77% | 0,834 | 39,9% | +16,9% | ❌ |
| B35 | 牛来 | 1.216 ⚠ | 131 | 38,9% | **−72,41%** | **0,586** | **79,2%** | −46,7% | ❌ PF terburuk ke-2 (setelah Q 0,567) |
| B36 | DASH | 2.758 ⚠ | 218 | 38,5% | −33,20% | 0,850 | **43,4%** | +48,0% | ❌ |
| B37 | **CYS** | **4.508** | 473 | 44,8% | **+500,54%** | **1,300** | 18,4% | −68,7% | ⚠ **PF BERTAHAN ≥1,25 DI KEDALAMAN PENUH** — satu-satunya di seluruh proyek. Gagal hanya di DD (18,4%>10%). Protokol penuh dijalankan, lihat bagian khusus |
| B38 | OGN | 3.008 | 216 | 39,8% | −47,55% | 0,823 | **59,2%** | +66,2% | ❌ |
| B39 | MANA | 2.758 ⚠ | 222 | 35,1% | −49,38% | 0,717 | **56,5%** | +24,9% | ❌ — **BATCH 2 SELESAI** |

---

## #65 MINA — kandidat pertama yang tembus PF 1,25, lalu gugur

MINA adalah satu-satunya dari 65 pair yang pada pembacaan awal melewati ambang PF. Protokol penuh dijalankan. Hasilnya menggugurkannya.

### Tahap 1 — PF meluruh seiring data diperdalam

| Bar | Trade | Net % | PF | Max DD |
|---|---|---|---|---|
| 2.744 | 247 | +127,20% | **1,368** | 25,8% |
| 3.244 | 297 | +107,09% | **1,293** | 25,8% |
| **3.994** | **360** | **+86,43%** | **1,220** | **30,8%** |

Pola yang sama persis dengan DOGE (1,301 → 0,884) dan SUI (1,121 → 1,069): makin dalam datanya, makin turun PF-nya. Di kedalaman penuh **1,220 < ambang 1,25** — gagal screening tanpa perlu uji lanjutan.

Angka lengkap di 3.994 bar: GP/GL $47.884,9 / $39.242,3 · fee $1.903,8 · win 45,0% · Sharpe 2,23 · eksposur 59,9% · Long +$2.116,9 (184 trade) / Short +$6.525,8 (176 trade) · B&H +16,1%.

### Tahap 2 — split tuning/validation: seluruh hasil berasal dari satu rezim

| Periode | Trade | Net % | PF | Max DD | Long | Short |
|---|---|---|---|---|---|---|
| Paruh awal (≤ hari 20677, ~98 hari) | 184 | **−17,07%** | **0,897** | 25,8% | −$1.903,0 | +$196,0 |
| Paruh akhir (≥ hari 20678, ~68 hari) | 176 | **+124,80%** | **1,456** | 23,0% | +$4.847,3 | +$7.632,7 |

Strategi ini **rugi 17% selama 98 hari pertama**, lalu menghasilkan seluruh keuntungannya dalam 68 hari terakhir. Itu bukan edge yang persisten — itu satu rezim yang kebetulan cocok.

Catatan kejujuran metodologis: di MINA tidak ada tuning sama sekali (parameter diambil utuh dari HYPE), jadi **kedua paruh sebenarnya out-of-sample**. Karena itu split ini tidak mengukur overfitting parameter; yang diukur adalah stabilitas antarwaktu. Dan hasilnya tidak stabil.

### Verdict

❌ Gagal tiga kriteria pre-registered: PF 1,220 < 1,25 · Max DD 30,8% > 10% · hasil tidak stabil antarperiode. Tidak dilanjutkan ke stress test maupun uji tetangga parameter.

Pelajaran yang relevan untuk sisa sweep: **PF yang diukur di <3.000 bar bisa 0,15 terlalu tinggi.** Aturan "pair yang lolos harus diperdalam dulu" terbukti sekali lagi menyelamatkan satu false positive.

---

## B37 CYS — satu-satunya yang bertahan di atas ambang PF, lalu gugur di split

CYS adalah hasil terkuat dari seluruh 130+ tes proyek ini, dan **satu-satunya yang PF-nya tetap ≥1,25 setelah data diperdalam**. Protokol penuh dijalankan.

### Tahap 1 — PF bertahan saat diperdalam (pertama kali terjadi)

| Bar | Trade | Net % | PF | Max DD |
|---|---|---|---|---|
| 2.758 | 279 | +652,18% | 1,370 | 18,4% |
| **4.508** | **473** | **+500,54%** | **1,300** | **18,4%** |

PF turun 0,070 — tetap meluruh seperti enam pair lain, tapi ini satu-satunya yang mendarat **di atas** 1,25. DD-nya bahkan tidak memburuk.

Angka lengkap @4.508 bar: GP/GL $216.942,3 / $166.888,4 · fee $5.557,9 · win 44,8% · Sharpe 3,19 · eksposur 55,2% · Long +$19.254,5 (225 trade) / Short +$30.799,4 (248 trade) · B&H −68,7%.

### Tahap 2 — stress test: bertahan, nyaris

Dengan maker 0,05% dan slippage 5 bps: net **+352,39%**, **PF 1,2503**, DD 18,9%, fee naik $5.558 → $8.346.

Lolos **0,0003 di atas ambang**. Secara praktis ini berarti edge-nya setipis ketidakpastian biaya itu sendiri — satu basis poin lebih buruk dan ia gagal.

### Tahap 3 — split waktu: INI YANG MENGGUGURKAN

| Periode | Trade | Net % | PF | Long | Short |
|---|---|---|---|---|---|
| Paruh awal (≤ hari 20652) | 231 | **−23,95%** | **0,918** | −$2.117,9 | −$276,7 |
| Paruh akhir (≥ hari 20653) | 243 | **+677,10%** | **1,379** | +$27.656,0 | +$40.054,0 |

**Rugi 24% di paruh pertama, lalu seluruh +500% datang dari paruh kedua.** Persis struktur MINA. PF 1,300 di full window adalah rata-rata dari satu rezim yang rugi dan satu rezim yang untung — bukan edge yang persisten.

### Kenapa net +500% di sini tidak berarti apa yang terlihat

Tiga hal memperbesar angkanya secara artifisial:

1. **Compounding.** `qtyType: "percentOfEquity"` berarti ukuran posisi tumbuh seiring equity. Largest win $4.978 dan largest loss $4.754 di modal awal $10.000 menunjukkan bahwa di akhir periode satu trade menggerakkan ~50% modal awal. Net % akhir didominasi trade-trade terakhir, bukan konsistensi.
2. **B&H −68,7%.** Aset ini jatuh. Seluruh keuntungan datang dari sisi short (+$30.799 vs long +$19.255) di satu runtuhan besar. Itu bukan edge berulang — itu satu rezim turun yang kebetulan cocok dengan sinyal.
3. **Paruh pertama negatif.** Kalau strategi ini dijalankan mulai hari pertama data, Anda akan rugi 24% selama ~94 hari sebelum rezim yang menguntungkan datang. Tidak ada yang menjamin rezim itu datang lagi.

### Verdict

❌ Gagal dua kriteria pre-registered: **Max DD 18,4% > 10%** dan **tidak stabil antarperiode** (paruh awal PF 0,918). Stress test lolos hanya 0,0003. Tidak dijalankan ke uji tetangga parameter dan buang-trade-terbesar — split sudah menentukan.

**Catatan jujur:** CYS adalah hasil terdekat dengan "lolos" dari 130+ tes. Kalau kriteria DD dicabut dan split diabaikan, ini akan terlihat seperti temuan. Keduanya tidak boleh dicabut — justru untuk kasus seperti inilah keduanya ditetapkan di muka.

---

## Catatan prosedur per pair

1. Klik kotak simbol (106, 61) → ketik ticker di input (667, 147) → pilih baris aset.
2. Pastikan venue yang terpilih **HYPERLIQUID.F PERP** di panel kanan.
3. Collapse Strategy Tester dulu (pane harga harus tinggi, kalau tidak drag di y=250 meleset).
4. Kalau candle tidak render setelah ganti simbol: klik **Reset chart** dulu.
5. Drag `(150,250) → (870,250)` sebanyak ~10× dengan jeda 3 dtk.
6. Expand tester → tab Performance → catat baris tabel.
7. Kalau indikator ter-pause: klik chip "Paused by the chart" → Resume. **Tanpa ini angka di tester adalah hasil lama dan menyesatkan.**
