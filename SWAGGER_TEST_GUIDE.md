# Swagger Test Guide - CGE Model API

## Quick Start

1. **Open Swagger UI**: http://3.110.189.51/docs (or http://13.203.193.142/docs if using old IP)
2. **Test Health**: GET `/health` (should return `{"status":"healthy"}`)
3. **Run a Scenario**: Use the payloads below

## Ready-to-Use JSON Payloads

### 🚀 Quick Test (Start Here)

```json
{
  "scenario_name": "quick_test",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "realgdp": 1.0
  }
}
```

---

## MoHRE Demo Scenarios

### Scenario 1: Aggressive Emiratization Policy
**Description:** This scenario models an ambitious Emiratization initiative where Emirati employment increases by 20% across all sectors. This represents a significant push to increase national workforce participation, aligned with UAE's Vision 2030 goals. The policy aims to create more opportunities for Emirati citizens while maintaining economic growth. This scenario helps MoHRE understand the macroeconomic impacts, sectoral shifts, wage dynamics, and overall economic performance under aggressive localization targets.

```json
{
  "scenario_name": "mohre_aggressive_emiratization",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 20.0
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 2: Balanced Workforce Transformation
**Description:** This scenario models a balanced approach to workforce nationalization where Emirati employment increases by 15% while migrant employment decreases by 8%. This represents a gradual transition strategy that maintains economic stability while progressing toward localization goals. The scenario helps MoHRE evaluate the trade-offs between localization speed and economic performance, assess sectoral reallocation effects, and understand wage and productivity impacts across different employment categories.

```json
{
  "scenario_name": "mohre_balanced_workforce_transformation",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 15.0,
    "x1labiEmplWgt_MIGRANTHH": -8.0
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 3: Priority Sectors Emiratization Focus
**Description:** This scenario targets Emiratization in key strategic sectors (Construction, Financial Services, and Government Services) with a 25% increase in Emirati employment, combined with 6% GDP growth. This represents a sectoral targeting strategy where MoHRE focuses localization efforts on high-impact sectors that offer better career prospects for Emirati nationals. The scenario helps assess sectoral employment shifts, productivity impacts in targeted sectors, and overall economic growth under sector-focused policies.

```json
{
  "scenario_name": "mohre_priority_sectors_emiratization",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 25.0,
    "realgdp": 6.0,
    "aprimRatio_CNS": 12.0,
    "aprimRatio_OFI": 10.0,
    "aprimRatio_GOV": 8.0
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 4: Economic Growth with Employment Shift
**Description:** This scenario models strong economic growth (7% GDP) combined with moderate Emiratization (12% increase) and a slight reduction in migrant employment (-5%). This represents a growth-oriented strategy where economic expansion creates opportunities for both Emirati and migrant workers, but with a preference for national workforce. The scenario helps MoHRE understand how economic growth can facilitate workforce localization, assess employment creation across sectors, and evaluate wage and productivity dynamics in a growing economy.

```json
{
  "scenario_name": "mohre_growth_with_employment_shift",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "realgdp": 7.0,
    "x1labiEmplWgt_EMIRATI": 12.0,
    "x1labiEmplWgt_MIGRANTHH": -5.0
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 5: Productivity-Led Growth Strategy
**Description:** This scenario models a productivity enhancement strategy across multiple key sectors (Manufacturing, Construction, Financial Services, and Trade) combined with moderate Emiratization (10%). This represents an investment in human capital and technology to boost productivity while creating quality employment opportunities for Emirati nationals. The scenario helps MoHRE evaluate how productivity improvements can support both economic growth and localization goals, assess sectoral competitiveness, and understand the relationship between productivity gains and employment quality.

```json
{
  "scenario_name": "mohre_productivity_led_growth",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 10.0,
    "aprimRatio_MACH": 15.0,
    "aprimRatio_CNS": 12.0,
    "aprimRatio_OFI": 10.0,
    "aprimRatio_TRD": 8.0,
    "realgdp": 5.5
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 6: Multi-Year Emiratization Roadmap
**Description:** This scenario models a 5-year progressive Emiratization strategy with 8% annual Emirati employment growth and 4% GDP growth per year. This represents a long-term, sustainable approach to workforce nationalization that allows for gradual adjustment and skill development. The scenario helps MoHRE plan multi-year localization targets, assess cumulative economic impacts over time, evaluate sectoral evolution, and understand how progressive policies affect employment patterns, wages, and economic performance across multiple years.

```json
{
  "scenario_name": "mohre_5yr_emiratization_roadmap",
  "year": 2023,
  "steps": 5,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 8.0,
    "realgdp": 4.0
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 7: Construction & Infrastructure Sector Focus
**Description:** This scenario targets the construction and infrastructure sectors with 30% Emirati employment increase and 15% productivity boost, combined with 6% GDP growth. This represents a strategic focus on sectors with high employment potential and significant infrastructure investment. The scenario helps MoHRE understand employment creation in construction, assess infrastructure investment impacts, evaluate wage dynamics in labor-intensive sectors, and analyze how sector-specific policies affect overall economic performance.

```json
{
  "scenario_name": "mohre_construction_infrastructure_focus",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 30.0,
    "aprimRatio_CNS": 15.0,
    "realgdp": 6.0
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 8: Knowledge Economy Transition
**Description:** This scenario models a transition toward a knowledge-based economy with productivity improvements in high-tech sectors (Machinery, Electronics, Information Services) and 18% Emirati employment growth. This represents investment in education, technology, and innovation to create high-value employment opportunities for Emirati nationals. The scenario helps MoHRE assess the shift toward knowledge-intensive sectors, evaluate skill requirements and wage premiums, understand productivity gains in technology sectors, and analyze how knowledge economy policies affect overall economic structure.

```json
{
  "scenario_name": "mohre_knowledge_economy_transition",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 18.0,
    "aprimRatio_MACH": 20.0,
    "aprimRatio_ELEC": 18.0,
    "aprimRatio_OFI": 15.0,
    "aprimRatio_OBS": 12.0,
    "realgdp": 6.5
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 9: Tax Policy Impact on Employment
**Description:** This scenario models a 3% tax increase combined with 12% Emirati employment growth to understand how fiscal policy affects employment patterns and economic performance. This represents a scenario where increased government revenue from taxes could fund Emiratization programs and training initiatives. The scenario helps MoHRE evaluate the trade-offs between tax policy and employment, assess fiscal space for workforce development programs, understand how tax changes affect sectoral competitiveness, and analyze the relationship between government revenue and employment policies.

```json
{
  "scenario_name": "mohre_tax_policy_employment_impact",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "taxcsi": 3.0,
    "x1labiEmplWgt_EMIRATI": 12.0,
    "realgdp": 4.5
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "x1prim",
    "x1cap",
    "x1lnd",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "ftax",
    "f1taxcsi",
    "f2taxcsi",
    "f3taxcs",
    "f5taxcs",
    "f0taxs",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "INITGDP",
    "contGDPexp"
  ]
}
```

### Scenario 10: Comprehensive National Strategy
**Description:** This scenario models a comprehensive national development strategy combining aggressive Emiratization (22%), productivity improvements across multiple sectors, strong GDP growth (7%), and moderate tax adjustments. This represents an integrated policy approach where employment, productivity, growth, and fiscal policies work together. The scenario helps MoHRE evaluate comprehensive policy packages, assess synergies between different policy instruments, understand economy-wide impacts of coordinated policies, and analyze how integrated strategies affect employment quality, economic competitiveness, and long-term sustainability.

```json
{
  "scenario_name": "mohre_comprehensive_national_strategy",
  "year": 2023,
  "steps": 1,
  "shocks": {
    "x1labiEmplWgt_EMIRATI": 22.0,
    "x1labiEmplWgt_MIGRANTHH": -7.0,
    "aprimRatio_MACH": 18.0,
    "aprimRatio_CNS": 15.0,
    "aprimRatio_OFI": 12.0,
    "aprimRatio_TRD": 10.0,
    "aprimRatio_EDU": 8.0,
    "realgdp": 7.0,
    "taxcsi": 2.5
  },
  "reporting_vars": [
    "x1labioEmplWgt",
    "x1labiEmplWgt_EMIRATI",
    "x1labiEmplWgt_MIGRANTHH",
    "x1labiEmplWgt_MIGRANTCOMB",
    "x1labiEmplWgt_COMMUTING",
    "x1labi_EMIRATI",
    "employi",
    "x1labi",
    "f1labio",
    "p1labi",
    "p1labio",
    "p1lab",
    "realgdp",
    "INCGDP",
    "V0GDPINC",
    "p0gdpexp",
    "x0gdpexp",
    "p3tot",
    "x3tot",
    "V3BAS",
    "V3TOT",
    "x1",
    "q1",
    "MAKE",
    "MAKEI",
    "V1BAS",
    "V1LAB",
    "V1CAP",
    "V1LND",
    "V1PRIM",
    "V1PTX",
    "V1OCT",
    "V1PTXI",
    "V1OCTI",
    "x1prim",
    "x1cap",
    "x1lnd",
    "x1oct",
    "delV1PTX",
    "p1cap",
    "p1capi",
    "x1capi",
    "aprim",
    "aprimRatio",
    "APRIMRATIO",
    "realwage",
    "phi",
    "x2tot",
    "x2cs",
    "V2TOT",
    "x4",
    "V4BAS",
    "x5tot",
    "V5TOT",
    "V5BAS",
    "x5",
    "taxcsi",
    "V0TAXCSI",
    "V1TAXCSI",
    "V2TAXCSI",
    "V3TAXcs",
    "V4TAXC",
    "V5TAXcs",
    "V0TARC",
    "ftax",
    "f1taxcsi",
    "f2taxcsi",
    "f3taxcs",
    "f5taxcs",
    "f0taxs",
    "VCAPSTOCK",
    "qcapstock",
    "pcapstock",
    "delCAPSTOCK",
    "VDEP",
    "IKERAT",
    "oneCapital",
    "x0com",
    "INITGDP",
    "contGDPexp"
  ]
}
```

---

## Summary of MoHRE Demo Scenarios

| # | Scenario Name | Key Focus | Emiratization | GDP Growth | Key Sectors | Reporting Vars |
|---|---------------|-----------|---------------|------------|-------------|----------------|
| 1 | Aggressive Emiratization | Maximum localization push | 20% | - | All sectors | ~60 variables |
| 2 | Balanced Workforce | Gradual transition | 15% / -8% migrant | - | All sectors | ~60 variables |
| 3 | Priority Sectors | Sector targeting | 25% | 6% | Construction, Finance, Government | ~60 variables |
| 4 | Growth with Shift | Growth-oriented | 12% / -5% migrant | 7% | All sectors | ~60 variables |
| 5 | Productivity-Led | Human capital investment | 10% | 5.5% | Manufacturing, Construction, Finance, Trade | ~60 variables |
| 6 | 5-Year Roadmap | Long-term strategy | 8% (annual) | 4% (annual) | All sectors (5 years) | ~60 variables |
| 7 | Construction Focus | Infrastructure sector | 30% | 6% | Construction | ~60 variables |
| 8 | Knowledge Economy | Technology transition | 18% | 6.5% | Machinery, Electronics, Services | ~60 variables |
| 9 | Tax & Employment | Fiscal policy impact | 12% | 4.5% | All sectors | ~65 variables |
| 10 | Comprehensive Strategy | Integrated approach | 22% / -7% migrant | 7% | Multiple sectors | ~70 variables |

## How to Use in Swagger

1. **Navigate to endpoint**: Find `POST /api/v1/scenarios/run` in Swagger UI
2. **Click "Try it out"**
3. **Paste JSON**: Copy one of the payloads above into the Request body field
4. **Execute**: Click the "Execute" button
5. **Get Scenario ID**: Copy the `scenario_id` from the response
6. **Check Status**: Use `GET /api/v1/scenarios/{scenario_id}/status` to check progress
7. **Get Results**: Once status is "completed", use `GET /api/v1/scenarios/{scenario_id}/results`

## Chat Endpoint Examples

### Natural Language Question

```json
{
  "question": "What if Emirati employment increases by 15%?"
}
```

### Complex Question

```json
{
  "question": "Run a scenario with 15% Emirati employment increase, 10% migrant decrease, and 5% GDP growth over 3 years"
}
```

## Available Variables

### Employment Variables
- `x1labiEmplWgt_EMIRATI` - Emirati employment weight
- `x1labiEmplWgt_MIGRANTHH` - Migrant household employment
- `x1labiEmplWgt_MIGRANTCOMB` - Migrant combined employment
- `x1labiEmplWgt_COMMUTING` - Commuting employment
- `employi` - Total employment index
- `f1labio` - Labor factor
- `p1labi` - Labor price

### Economic Variables
- `realgdp` - Real GDP growth (%)
- `INCGDP` - GDP income
- `p0gdpexp` - GDP expenditure price
- `p3tot` - Consumer price index (inflation)
- `x0gdpexp` - GDP expenditure
- `V0GDPINC` - GDP income value

### Productivity Variables (by sector)
- `aprimRatio_AG` - Agriculture
- `aprimRatio_MIN` - Mining
- `aprimRatio_MACH` - Machinery
- `aprimRatio_CNS` - Construction
- `aprimRatio_TEX` - Textiles
- And more... (use `GET /api/v1/sectors` to see all)

### Tax Variables
- `taxcsi` - Tax rate
- `ftax` - Tax factor
- `V0TAXCSI` - Tax value

## Testing Workflow

1. ✅ **Health Check**: `GET /health`
2. ✅ **List Variables**: `GET /api/v1/variables`
3. ✅ **List Sectors**: `GET /api/v1/sectors`
4. ✅ **Run Scenario**: `POST /api/v1/scenarios/run` (use payloads above)
5. ✅ **Check Status**: `GET /api/v1/scenarios/{scenario_id}/status`
6. ✅ **Get Results**: `GET /api/v1/scenarios/{scenario_id}/results`
7. ✅ **Compare Scenarios**: `POST /api/v1/scenarios/compare`

## Tips

- **Start Simple**: Use the "quick_test" payload first
- **Check Status**: Scenarios run in background - check status endpoint
- **Reporting Vars**: Include `reporting_vars` to limit output size
- **Multi-Year**: Use `steps` > 1 for projections
- **Negative Values**: Use negative values for decreases (e.g., `-10.0`)

## Troubleshooting

- **404 Error**: Check that scenario_id is correct
- **400 Error**: Validate JSON syntax and required fields
- **500 Error**: Check server logs with `docker logs cge-model-api`
- **Timeout**: Long-running scenarios may take several minutes
