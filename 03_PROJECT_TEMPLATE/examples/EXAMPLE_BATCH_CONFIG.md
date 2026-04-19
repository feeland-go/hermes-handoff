# Example Batch Configurations

Berikut contoh konfigurasi batch untuk berbagai domain riset.
Copy yang sesuai saat menjalankan `setup_new_project.py`.

---

## Metocean / Maritime (WeatherxProd style)

```
P 1 50 A_pricing_valuation
P 51 130 B_squall_nowcasting
P 131 210 C_nwp_ocean_forecasting
P 211 290 D_saas_pricing_theory
P 291 370 E_marine_service_adoption
P 371 450 F_indonesia_maritime
P 451 500 G_himawari_remote_sensing
```

## Stock / Index Analysis (IHSG style)

```
R 1 6 A_market_regime_macro
R 7 12 B_sector_rotation_fundamental
R 13 18 C_technical_flow_microstructure
R 19 24 D_risk_portfolio_strategy
IHSG 1 15 regime_detection
IHSG 16 45 technical_analysis
IHSG 46 70 hybrid_scoring
IHSG 71 85 exit_strategy
IHSG 86 105 sector_sentiment
IHSG 106 110 smart_money
```

## Cryptocurrency Research

```
CR 1 20 blockchain_fundamentals
CR 21 40 market_microstructure
CR 41 60 defi_protocols
CR 61 80 on_chain_analytics
CR 81 100 trading_strategies
CR 101 120 regulatory_compliance
```

## Commodity Analysis (Palm Oil, Coal, etc.)

```
K 1 15 global_supply_demand
K 16 30 pricing_mechanisms
K 31 45 logistics_supply_chain
K 46 60 sustainability_esg
K 61 75 regulatory_indonesia
K 76 90 trading_strategies
```

## Generic Academic Research

```
P 1 25 literature_review
P 26 50 methodology
P 51 75 data_collection
P 76 100 analysis
P 101 125 discussion
P 126 150 conclusions
```

---

## Tips

- Prefix bisa apa saja: `P`, `R`, `IHSG`, `CR`, `K`, dll — yang penting konsisten
- Angka bisa dimulai dari 1 untuk setiap prefix
- Folder name pakai snake_case, diawali huruf batch (A_, B_, C_)
- Task per batch idealnya 15-80 — terlalu banyak sulit di-manage
- Total tasks antara 100-500 adalah sweet spot
