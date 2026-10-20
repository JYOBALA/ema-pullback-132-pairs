//@lang=wrun-ts
// HYPE Scalp v5 - wide-R maker pullback (15m).
//
// ============================== BACA INI DULU ==============================
// VARIAN INI **TIDAK LOLOS** KRITERIA KELAYAKAN. JANGAN DIJALANKAN LIVE.
//
// Ini konfigurasi terbaik dari 14 varian yang diuji, disimpan sebagai catatan
// teknis - bukan sebagai strategi siap pakai. Hasilnya di BINANCE.F:HYPEUSDT 15m,
// 3.540 bar (11 Sep - 18 Okt 2026):
//
//   Full window, biaya nyata  : +5,47%  PF 1,058  DD 16,3%  98 trade
//   Tuning half  (<= day 20725): +10,87% PF 1,229  DD 15,0%  53 trade
//   Validation half (>= 20726): -7,87%  PF 0,820  DD 13,2%  47 trade   <-- GAGAL
//   Stress (maker 0,05/slip 5): -0,55%  PF 0,994  DD 18,3%  98 trade   <-- GAGAL
//
// Validation half negatif = parameter ini overfit ke paruh pertama data.
// Stress test negatif = edge-nya lebih tipis daripada ketidakpastian biaya.
// Detail lengkap semua eksperimen ada di strategies/backtest_log.md.
// ===========================================================================
//
// Perbedaan dari v4 (semuanya hasil eksperimen E6-E12, satu perubahan per langkah):
//   min_risk_pct 0,3 -> 1,5   stop lebih lebar; biaya tetap % notional, jadi
//                              memperbesar R mengecilkan rasio cost/R
//   max_hold     24  -> 96    time stop 24 bar memaksa exit lewat closeAll
//                              (market = taker + slippage, exit termahal). Dengan
//                              96 bar, exit pindah ke limit TP yang bayar maker
//   be_trigger_r 1,0 -> 8,0   mematikan breakeven lock. Di R lebar lock-nya
//                              memotong pemenang: payoff naik 0,86 -> 1,35
//
// Build backtest: hanya equity yang diplot. Mem-plot EMA dan level resting
// memicu FE_EXECUTION_PAUSED di chart >3k bar dan membekukan tester di tengah run.

// Biaya jadi param supaya stress test cukup ganti setting, bukan recompile.
const marginPct = param("margin_pct", 20, { min: 1, max: 100, description: "Percent of equity committed as isolated margin per entry" });
const makerFee = param("maker_fee_pct", 0.02, { min: 0.0, max: 0.2, description: "Maker fee, percent of notional" });
const takerFee = param("taker_fee_pct", 0.045, { min: 0.0, max: 0.2, description: "Taker fee, percent of notional" });
const slipBps = param("slippage_bps", 2, { min: 0, max: 50, description: "Adverse slippage on market-crossing fills, basis points" });

strategy({
  initialCapital: 10000,
  instrument: "perps",
  leverage: 5,
  qtyType: "percentOfEquity",
  qtyValue: marginPct,
  makerFeePercent: makerFee,
  takerFeePercent: takerFee,
  slippageBps: slipBps,
  funding: "off",
  pyramiding: 1,
  fillModel: "pessimistic"
});

param("fast_len", 20, { min: 2, max: 200, description: "Fast EMA length" });
param("slow_len", 100, { min: 5, max: 400, description: "Slow EMA length, the trend gate" });
param("atr_len", 14, { min: 2, max: 100, description: "ATR length" });
param("pull_atr", 0.5, { min: 0.0, max: 3.0, description: "Limit entry distance from close, in ATR" });
param("stop_atr", 1.0, { min: 0.1, max: 5.0, description: "Stop distance from entry, in ATR" });
param("min_risk_pct", 1.5, { min: 0.05, max: 3.0, description: "Floor on the stop distance, percent of entry price" });
param("rr", 1.5, { min: 0.3, max: 6.0, description: "Take profit as a multiple of risk" });
param("be_trigger_r", 8.0, { min: 0.1, max: 8.0, description: "Favourable excursion in R that arms breakeven. At 8 it never arms, which is the tested setting" });
param("be_lock_pct", 0.12, { min: 0.0, max: 1.0, description: "Profit locked when breakeven arms, percent of entry price" });
param("entry_ttl", 3, { min: 1, max: 50, description: "Bars a resting limit entry stays alive before it is cancelled" });
param("max_hold", 96, { min: 2, max: 500, description: "Bars a position may be held before the time stop" });
param("cool_down", 0, { min: 0, max: 200, description: "Bars to stand aside after a position closes" });
param("start_day", 0, { min: 0, max: 100000, description: "First UTC day, floor(time/86400), an entry may be armed. Tuning half used end_day 20725, validation half start_day 20726" });
param("end_day", 100000, { min: 0, max: 100000, description: "Last UTC day an entry may be armed" });

output("equity", line, lower, { description: "Strategy equity" });

let fastEma = new Ema(20);
let slowEma = new Ema(100);
let atr = new Atr(14);

let vPullAtr: f64 = 0.5;
let vStopAtr: f64 = 1.0;
let vMinRisk: f64 = 1.5;
let vRr: f64 = 1.5;
let vBeTrigger: f64 = 8.0;
let vBeLock: f64 = 0.12;
let vTtl: i32 = 3;
let vMaxHold: i32 = 96;
let vCool: i32 = 0;
let vStartDay: f64 = 0.0;
let vEndDay: f64 = 100000.0;

let prevPos: f64 = 0.0;
let hasPending: bool = false;
let pendingAge: i32 = 0;
let heldBars: i32 = 0;
let restBars: i32 = 999;
let beArmed: bool = false;
let entryPrice: f64 = NaN;
let riskPerUnit: f64 = NaN;

function onStart(): void {
  fastEma = new Ema(i32(p_fast_len()));
  slowEma = new Ema(i32(p_slow_len()));
  atr = new Atr(i32(p_atr_len()));
  vPullAtr = p_pull_atr();
  vStopAtr = p_stop_atr();
  vMinRisk = p_min_risk_pct();
  vRr = p_rr();
  vBeTrigger = p_be_trigger_r();
  vBeLock = p_be_lock_pct();
  vTtl = i32(p_entry_ttl());
  vMaxHold = i32(p_max_hold());
  vCool = i32(p_cool_down());
  vStartDay = p_start_day();
  vEndDay = p_end_day();
}

function onBar(): void {
  const h = bar.high();
  const l = bar.low();
  const c = bar.close();
  const t = bar.time();

  const fast = fastEma.update(c);
  const slow = slowEma.update(c);
  const a = atr.update(h, l, c);

  if (isNaN(fast) || isNaN(slow) || isNaN(a) || isNaN(c) || a <= 0.0) {
    out_equity(strategy.equity());
    return;
  }

  const pos = strategy.positionSize();
  const day = Math.floor(t / 86400.0);
  const inWindow = day >= vStartDay && day <= vEndDay;

  if (prevPos == 0.0 && pos != 0.0) {
    hasPending = false;
    pendingAge = 0;
    heldBars = 0;
    beArmed = false;
    entryPrice = strategy.positionAvgPrice();
    const floorRisk = entryPrice * vMinRisk / 100.0;
    const atrRisk = vStopAtr * a;
    riskPerUnit = atrRisk > floorRisk ? atrRisk : floorRisk;
  }

  if (prevPos != 0.0 && pos == 0.0) restBars = 0;

  if (pos != 0.0) {
    heldBars += 1;

    if (!beArmed) {
      if (pos > 0.0 && h >= entryPrice + vBeTrigger * riskPerUnit) beArmed = true;
      if (pos < 0.0 && l <= entryPrice - vBeTrigger * riskPerUnit) beArmed = true;
    }

    let stopPx: f64 = NaN;
    let tpPx: f64 = NaN;
    if (pos > 0.0) {
      stopPx = beArmed ? entryPrice * (1.0 + vBeLock / 100.0) : entryPrice - riskPerUnit;
      tpPx = entryPrice + vRr * riskPerUnit;
    } else {
      stopPx = beArmed ? entryPrice * (1.0 - vBeLock / 100.0) : entryPrice + riskPerUnit;
      tpPx = entryPrice - vRr * riskPerUnit;
    }
    strategy.exit("X").from("E").stop(stopPx).limit(tpPx).send();

    if (heldBars >= vMaxHold) strategy.closeAll();
  } else {
    heldBars = 0;
    restBars += 1;

    if (hasPending) {
      pendingAge += 1;
      if (pendingAge > vTtl) {
        strategy.cancel("E");
        hasPending = false;
        pendingAge = 0;
      }
    }

    if (!hasPending && inWindow && restBars > vCool) {
      const up = c > slow && fast > slow;
      const down = c < slow && fast < slow;
      if (up) {
        strategy.long("E").limit(c - vPullAtr * a).send();
        hasPending = true;
        pendingAge = 0;
      } else if (down) {
        strategy.short("E").limit(c + vPullAtr * a).send();
        hasPending = true;
        pendingAge = 0;
      }
    }
  }

  prevPos = pos;
  out_equity(strategy.equity());
}
