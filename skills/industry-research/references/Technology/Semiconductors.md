# Semiconductors

> Consolidated industry reference. Policy and data material is reviewed through 2026-07-14; verify time-sensitive rules, programs, and figures against current primary sources.

## Table of contents

1. [Taxonomy and Industry Boundaries](#1-taxonomy-and-industry-boundaries)
2. [Inputs and Dependencies](#2-inputs-and-dependencies)
3. [Market Landscape](#3-market-landscape)
4. [Operating Mechanics](#4-operating-mechanics)
5. [Economics and Valuation](#5-economics-and-valuation)
6. [Regulation and Public Funding](#6-regulation-and-public-funding)
7. [Historical Cases and Failure Patterns](#7-historical-cases-and-failure-patterns)
8. [Data Sources and Monitoring Dashboard](#8-data-sources-and-monitoring-dashboard)
9. [Geographic Operating Models](#9-geographic-operating-models)
10. [Cross-Industry Dependency Map](#10-cross-industry-dependency-map)
11. [Decision-Grade Unit Economics](#11-decision-grade-unit-economics)
12. [Industry Balance and Marginal Economics](#12-industry-balance-and-marginal-economics)
13. [Terminology and Comparability Traps](#13-terminology-and-comparability-traps)

## 1. Taxonomy and Industry Boundaries


Reviewed through 2026-07-14. Define the measured object before comparing firms, assets, or markets.

### Boundary

Chip design/IP, integrated device manufacturing, foundries, memory, analog/power/RF/sensors, semiconductor equipment/materials, and packaging/test.

### Operating taxonomy

| Segment | What is sold | Primary unit | Do not aggregate without |
| --- | --- | --- | --- |
| Leading-edge logic and accelerators | CPUs, GPUs, AI accelerators and custom logic | dies, wafers, compute, performance/W | Node, architecture, software, package, memory and yield |
| Memory | DRAM, NAND and high-bandwidth memory | bits, wafers, ASP/bit | Generation, density, mix, inventory and cycle |
| Analog, power, RF and sensors | Signal, power conversion, connectivity and sensing | units, content/system, wafer diameter | Process, voltage/frequency, reliability and qualification |
| Foundry and IDM manufacturing | Wafer fabrication and integrated chip production | wafer starts, wafers shipped, utilization | Node, wafer size, layer count, cycle, yield and customer |
| Packaging, assembly and test | Conventional and advanced package integration | units, substrates, test time | Package type, interposer, HBM, thermal and known-good die |
| Equipment, materials, EDA and IP | Tools, wafers/chemicals/gases, design software and reusable blocks | systems, installed base, licenses/royalties | Process step, qualification, service, export and node |

### Specifications that change value

- State process node but also transistor architecture, density, yield, die size, layer count and design maturity.
- Performance needs workload, precision, memory, interconnect, power, thermal and software stack.
- Capacity is compatible wafer starts plus package/test, not generic fab space.
- Memory must state bit generation, density, HBM stack/speed, contract/spot and inventory.
- Design wins need socket, program, content, production date, lifetime and customer qualification.

### Role map

Architect/OEM specifies; fabless/IDM designs; EDA/IP enables; foundry fabricates; equipment/material firms supply; OSAT packages/tests; distributor holds; system OEM integrates; cloud/consumer/auto/industrial customer uses; governments regulate trade/security.

### Terms that must be explicit

- node label versus delivered density/performance
- wafer start versus good packaged die
- die yield versus final yield
- design win versus production revenue
- leading-edge, mature-node and specialty capacity


## 2. Inputs and Dependencies


Scope note: "Semiconductors" here spans the whole make-a-chip stack — design (fabless + IP + EDA), fabrication (foundry/IDM), and back-end (assembly/test/packaging). Inputs differ sharply by stage, so each input below is tagged with where it bites hardest. All figures dated; anything older than ~3 years is flagged.

### 1. The master fact that governs every input
Global semiconductor sales were ~$627–630B in 2024 (+19.1% YoY) and hit **$791.7B in 2025** (+25.6%), with a $1T run-rate projected for 2026 (**[Fact]** — SIA/WSTS, 2026 — https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/). This device-level revenue sits on top of a much smaller but chokepoint-dense input base: ~$95B of wafer-fab equipment (2024) and a few tens of billions of materials. **[Inference]** The economically decisive inputs are not the biggest by dollar value — they are the ones with a single or dual supplier (EUV, EUV photoresist, EDA, IP), because those cap what can be built at all.

### 2. Capital equipment (the largest and most concentrated input)
Wafer-fab equipment (WFE) was ~$95B in 2024 (**[Estimate]** — MarketsandMarkets, 2024 — https://www.marketsandmarkets.com/ResearchInsight/semiconductor-manufacturing-equipment-market.asp). Five firms take ~56–66% of it: Applied Materials, ASML, Lam Research, Tokyo Electron, KLA (**[Fact]** — same source).

- **Lithography / ASML monopoly:** ASML is the *only* series producer of EUV. It recognized **44 EUV systems in 2024** and €21.8B of total system sales, ~38% of that EUV (**[Fact]** — ASML 20-F FY2024 / SEC — https://www.sec.gov/Archives/edgar/data/0000937966/000093796625000009/asml-20241231.htm). A standard EUV scanner is ~$200M; High-NA EUV exceeds $350M (**[Estimate]** — SemiAnalysis / IBS, 2024 — https://newsletter.semianalysis.com/p/euv-requirements-halved-applied-materials). **[Inference]** This is the industry's hardest single point of failure: no fab below ~7nm exists without ASML, and ASML itself depends on Zeiss optics and Cymer/light-source subsystems. Pricing power sits entirely with ASML at the leading edge.
- **Deposition/etch (Applied, Lam, TEL) and process control (KLA):** more competitive than litho — two-to-three credible suppliers per step — so pricing power is weaker and buyers (TSMC, Samsung, Intel) extract volume terms.

Why it caps capacity: fab output is gated by tool delivery lead times (often 12–18 months for EUV). A shock here (ASML export ban, Zeiss optic shortage) directly freezes leading-edge capacity additions.

### 3. Silicon wafers (the substrate)
Polished/epi 300mm wafers are the physical canvas. Supply is a tight oligopoly: Shin-Etsu (~28% of 300mm), SUMCO (~23%), then GlobalWafers, Siltronic, SK Siltron — top five ≈ **82% of revenue** (2023 data, **[Estimate]** — market-research aggregates — https://www.marketgrowthreports.com/market-reports/300mm-silicon-wafers-market-103422). Shin-Etsu + SUMCO alone exceed 50% of 300mm capacity.

Cost sensitivity: **[Inference]** raw wafer cost ($100–150 for a blank 300mm wafer) is a rounding error against a finished 3nm wafer's ~$18,000–20,000 process value (Morgan Stanley/TrendForce estimates — https://www.tomshardware.com/tech-industry/tsmcs-wafer-pricing-now-usd18-000-for-a-3nm-wafer-increased-by-over-3x-in-10-years-analyst), so wafer price does *not* drive leading-edge margins — but wafer *availability* can cap capacity, and for trailing-edge/analog chips the substrate is a more meaningful share of cost. Pricing power historically sat with buyers (chronic overcapacity), shifting toward suppliers in the AI-driven 2024–2026 upcycle as SUMCO retooled 200mm lines for "AI-grade" 300mm (**[Fact]** — SUMCO, 2025).

### 4. Specialty chemicals, gases, photomasks
- **Photoresist:** Japan controls >70% of all photoresist; JSR + Tokyo Ohka Kogyo ≈ 91% of the market, and JSR/TOK/Shin-Etsu hold >90% of the *EUV* resist segment (**[Estimate]** — TrendForce / GM Insights, 2025 — https://www.trendforce.com/news/2025/11/06/news-japan-ramps-up-photoresist-investment-for-2nm-chips-tokyo-ohka-kogyo-jsr-lead-the-charge/). **[Inference]** EUV resist is a near-total single-country dependency and a genuine chokepoint alongside EUV tools themselves.
- **Gases:** high-purity neon, argon, and specialty gases (WF6, C4F6). Neon supply was heavily Ukraine-linked pre-2022; the 2022 invasion spiked neon prices and forced qualification of alternate sources (**[Fact]** — widely reported, 2022, now partly stale).
- **Critical minerals:** China restricted **gallium and germanium** exports (2023) and tightened controls since — inputs for compound semis (GaAs, GaN) and some optics (**[Fact]** — widely reported policy, 2023–2025).
- **Photomasks:** leading-edge masks (esp. EUV mask blanks) are dominated by Hoya and a handful of makers; a single EUV mask set can cost several $M. **[Inference]** Mask-blank defectivity is a recurring yield chokepoint.

Cost flow: **[Inference]** materials collectively are a low-double-digit % of front-end cost, but their concentration means a supply cut (e.g., Japan's Nov-2025 METI export-control listing of 12 core materials to 42 Chinese firms — https://www.trendforce.com/news/2025/11/06/news-japan-ramps-up-photoresist-investment-for-2nm-chips-tokyo-ohka-kogyo-jsr-lead-the-charge/) can halt specific customers' production entirely rather than just raise costs.

### 5. Software / IP (small dollars, enormous leverage)
- **EDA tools:** Synopsys (~31%), Cadence (~30%), Siemens EDA (~13%) — ~75% of the market (**[Fact]** — 2024 estimates — https://www.embedded.com/taking-stock-of-the-eda-industry/). Synopsys FY2024 revenue $6.13B. No advanced chip is designed without this software.
- **Design IP:** Arm generated $3.2B in FY2024, $1.8B of it royalties (**[Fact]** — Statista/Arm filings — https://www.statista.com/statistics/1132055/arm-net-sales-by-segment-worldwide/). Arm instruction-set IP underlies nearly all mobile SoCs and a growing share of data-center CPUs.

**[Inference]** These are the cheapest inputs by dollars yet among the highest in leverage: US export controls on EDA to China (2025) instantly threatened Chinese design capability, showing the software layer is a policy chokepoint equal to hardware.

### 6. Labor
Deep scarcity of process/integration engineers, litho/etch specialists, and packaging engineers. **[Fact]** SIA and industry studies repeatedly flag a projected US workforce shortfall of tens of thousands of skilled roles this decade (SIA Factbook, 2025 — https://www.semiconductors.org/wp-content/uploads/2025/05/2025-SIA-Factbook-FINAL-1.pdf). **[Inference]** Labor is now a binding constraint on *geographic diversification*: TSMC's Arizona ramp was delayed partly by skilled-labor availability, which is a core reason fab clusters (Taiwan, Korea) are sticky — the tacit human capital does not relocate quickly. Labor is a modest share of leading-edge fab operating cost (fabs are capital-, not labor-intensive) but a hard gate on *where* capacity can exist.

### 7. Energy, water, physical infrastructure
A leading-edge fab consumes power and ultrapure water at utility scale (tens of MW; millions of gallons/day). **[Inference]** Energy is a meaningful and rising opex line — EUV tools are extremely power-hungry — and reliable, cheap, uninterrupted power plus abundant water are siting prerequisites (a reason Taiwan's droughts and Texas grid events are watched closely). Energy price moves flow to gross margin at trailing-edge/memory fabs more than at leading-edge, where wafer value per unit is so high that energy is a smaller %.

### 8. Financial capital (the input that actually caps expansion)
Leading-edge fabs are among the most capital-intensive assets on earth. A 3nm-class fab (~50k wafer-starts/month) runs ~$20B; a 2nm-class fab ~$28B (**[Estimate]** — IBS, 2024 — https://www.tomshardware.com/tech-industry/firm-predicts-it-will-cost-dollar28-billion-to-build-a-2nm-fab-and-dollar30000-per-wafer). TSMC alone spent **$29.76B capex in 2024** and guided $38–42B for 2025 (**[Fact]** — TSMC 6-K, 2025 — https://www.sec.gov/Archives/edgar/data/1046179/000104617925000004/a4q24e_withguidancexfinal.htm). **[Inference]** Access to cheap capital and multi-year cash-flow visibility is itself a moat — only ~3 firms can fund the leading edge, which is why government subsidy became a required input (see §10). Capital availability, more than any raw material, caps how fast frontier capacity grows.

### 9. Logistics / cross-industry dependencies
Chips depend on outside industries both up and down: precision optics (Zeiss), advanced valves/pumps (Edwards), ABF substrate (Ajinomoto — a food company that makes the insulating film under every high-end CPU/GPU; a genuine niche chokepoint), lead-frames, bonding wire (gold/copper), and air/sea freight for a globe-spanning supply chain where a wafer can cross borders a dozen times. **[Inference]** ABF substrate and advanced IC-substrate capacity have been recurring bottlenecks for high-end packaging.

### 10. Regulation & industrial policy as an input
Subsidy is now a factor of production. US CHIPS Act finalized >$33B in 2024 awards — TSMC up to $6.6B, Intel up to $7.86B, Micron ~$6.2B, Samsung ~$4.75B (**[Fact]** — SIA/Commerce, 2024 — https://www.manufacturingdive.com/news/chips-and-science-act-tracker-semiconductor-manufacturing/734039/). The EU Chips Act mobilizes >€43B toward a 20%-by-2030 share goal (**[Fact]** — EU, 2024 — https://fortune.com/2024/08/20/tsmc-eu-dresden-germany-chip-plant-intel-subsidies/). Export controls (US on China; Japan/Netherlands on tools/materials) act as a *negative* input — cutting off buyers or suppliers by policy.

### 11. Which inputs determine margins vs. cap capacity (summary)
- **Cap capacity (physical/binding):** EUV tools (ASML), EUV photoresist (Japan), skilled labor, financial capital, wafer supply. A shock here stops output regardless of price.
- **Determine margin:** at the leading edge, margin is set far more by *yield and utilization* (see MECHANICS) than by input prices — inputs are a modest, concentrated cost. At trailing-edge/analog/memory, substrate, energy, and gases matter more to unit cost.
- **Propagation example:** an ASML EUV export freeze → no new sub-7nm capacity for the affected fab → leading-edge wafer scarcity → foundry ASPs rise → fabless GPU/CPU costs rise → device prices rise 1–2 quarters later. A photoresist cutoff propagates the same way but faster, since resist is consumed continuously rather than installed once.

### 9. Full atom-to-fab and design input ledger

Start upstream of the wafer. Silicon devices require quartz, metallurgical silicon, polysilicon and single-crystal wafers; compound semiconductors require gallium, arsenic, indium, phosphorus, silicon carbide or gallium nitride substrates/epitaxy. Fabs consume photoresists and developers, masks/pellicles, high-purity acids/bases/solvents, deposition and etch precursors, dopant and noble gases, copper/tungsten/cobalt and other metals, ultrapure water, clean electricity, cooling and abatement. Packaging adds organic substrates, leadframes, solder, gold/copper wire, molding compound, underfill, thermal materials and increasingly silicon interposers and high-bandwidth memory.

Equipment chains include lithography, deposition, etch, ion implant, metrology/inspection, cleaning, furnaces, CMP and test; each embeds precision optics, lasers, vacuum systems, ceramics, magnets, bearings, pumps, power electronics and specialized software. EDA tools, process-design kits, IP blocks, architecture licenses, firmware, verification, foundry capacity and trained analog/RF/digital/process/packaging engineers are equally critical design inputs.

Sites need stable grid power, enormous treated-water and wastewater capacity, gases/chemicals logistics, vibration control, clean rooms, fire safety, cyber/IP security and export-compliant maintenance. Capital includes corporate cash/debt/equity, customer prepayments, foundry and packaging contracts, equipment leases, strategic investors, government grants/loans/tax credits and R&D programs.

Wafer price, yield, die size, product mix, memory pricing, depreciation and utilization set margin; EUV tools, masks, leading-edge wafers, advanced packaging, HBM, substrates, ultrapure water, electricity, qualified chemicals and scarce engineering talent can cap output. Node migration, chiplets, mature-node redesign, inventory, second sourcing and material substitution help, but requalification and redesign take quarters or years.

### Sources

- NIST, CHIPS for America — https://www.nist.gov/chips
- SIA/WSTS 2025 sales — https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/
- SIA 2024 sales — https://www.semiconductors.org/global-semiconductor-sales-increase-19-1-in-2024-double-digit-growth-projected-in-2025/
- SIA 2025 Factbook — https://www.semiconductors.org/wp-content/uploads/2025/05/2025-SIA-Factbook-FINAL-1.pdf
- ASML 20-F FY2024 (SEC) — https://www.sec.gov/Archives/edgar/data/0000937966/000093796625000009/asml-20241231.htm
- WFE market share — https://www.marketsandmarkets.com/ResearchInsight/semiconductor-manufacturing-equipment-market.asp
- SemiAnalysis EUV/High-NA economics — https://newsletter.semianalysis.com/p/euv-requirements-halved-applied-materials
- 300mm wafer share — https://www.marketgrowthreports.com/market-reports/300mm-silicon-wafers-market-103422
- Photoresist / Japan export controls — https://www.trendforce.com/news/2025/11/06/news-japan-ramps-up-photoresist-investment-for-2nm-chips-tokyo-ohka-kogyo-jsr-lead-the-charge/
- EDA market — https://www.embedded.com/taking-stock-of-the-eda-industry/
- Arm revenue split — https://www.statista.com/statistics/1132055/arm-net-sales-by-segment-worldwide/
- Fab cost / 2nm — https://www.tomshardware.com/tech-industry/firm-predicts-it-will-cost-dollar28-billion-to-build-a-2nm-fab-and-dollar30000-per-wafer
- 3nm wafer price — https://www.tomshardware.com/tech-industry/tsmcs-wafer-pricing-now-usd18-000-for-a-3nm-wafer-increased-by-over-3x-in-10-years-analyst
- TSMC 4Q24 6-K (capex) — https://www.sec.gov/Archives/edgar/data/1046179/000104617925000004/a4q24e_withguidancexfinal.htm
- CHIPS Act tracker — https://www.manufacturingdive.com/news/chips-and-science-act-tracker-semiconductor-manufacturing/734039/
- EU Chips Act — https://fortune.com/2024/08/20/tsmc-eu-dresden-germany-chip-plant-intel-subsidies/

## 3. Market Landscape


### 1. The value chain, stage by stage — and who wins at each
The industry disaggregated decades ago into specialized layers. Profit does not spread evenly: it pools where a monopoly or near-monopoly exists and is competed away where there are many capable suppliers.

- **IP / instruction-set (Arm, RISC-V, Imagination, SiFive).** Arm: $3.2B FY2024 revenue, $1.8B royalties (**[Fact]** — https://www.statista.com/statistics/1132055/arm-net-sales-by-segment-worldwide/). Moat: an installed base and software ecosystem locked to the architecture. **[Inference]** High-margin, but RISC-V (open, royalty-free) is a structural threat to the licensing model.
- **EDA (Synopsys, Cadence, Siemens EDA).** ~75% combined share (**[Fact]** — https://www.embedded.com/taking-stock-of-the-eda-industry/). Moat: decades of tool refinement, foundry-certified flows, high switching cost. Near-oligopoly → fat, durable margins. Synopsys' ~$35B Ansys acquisition (2025) extends into multiphysics simulation.
- **Fabless design (Nvidia, AMD, Qualcomm, Broadcom, Apple silicon, MediaTek).** Nvidia FY2025: $130.5B revenue, $115.2B data-center, **75.0% gross margin** (**[Fact]** — Nvidia 10-K — https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm). Moat: architecture + software (CUDA), design talent, and control of scarce foundry/packaging allocation. **[Inference]** This is where the *most* profit now accrues — the AI compute layer.
- **Foundry (TSMC, Samsung, GlobalFoundries, UMC, SMIC, Intel Foundry).** TSMC held ~67% of the pure-play foundry market in Q4 2024 (**[Fact]** — TrendForce — https://www.trendforce.com/presscenter/news/20250310-12510.html), rising toward ~70% through 2025. Moat: process leadership, yield, ecosystem, and capital scale. Foundry is capital-heavy so margins (56% at TSMC) trail fabless, but TSMC's leadership gives it unusual pricing power for a manufacturer.
- **IDMs (Intel, Samsung, Micron, SK Hynix, TI, Infineon, STMicro, NXP, Analog Devices).** Own design + fab. Strong in memory, analog, power, auto/industrial.
- **Equipment (ASML, Applied Materials, Lam, TEL, KLA).** ~$95B WFE market, top-5 ≈ 56–66% (**[Fact]** — https://www.marketsandmarkets.com/ResearchInsight/semiconductor-manufacturing-equipment-market.asp). ASML's EUV monopoly is the single most profitable structural position in the chain.
- **Materials (Shin-Etsu, SUMCO wafers; JSR/TOK photoresist; gases).** Concentrated, chokepoint-rich (see INPUTS).
- **OSAT / packaging (ASE 44.6%, Amkor 15.2%, JCET 12% — 2024).** ASE $18.54B sales; top-10 OSAT combined $41.56B in 2024 (**[Fact]** — TrendForce — https://www.trendforce.com/presscenter/news/20250513-12577.html). Historically low-margin; advanced packaging is re-rating it.
- **Memory (Samsung, SK Hynix, Micron).** Distinct sub-industry. DRAM Q1 2026: Samsung 38.6%, SK Hynix 28.8%, Micron 22.4% (**[Fact]** — TechTimes/Counterpoint — https://www.techtimes.com/articles/318052/20260609/samsung-leads-dram-market-share-386-sk-hynix-trails-revenue-tops-profit-margins.htm). In **HBM**, SK Hynix leads (~50–57%), reflecting first-mover HBM3E and Nvidia design wins.

### 2. Where profits accrue vs. where they are competed away
**[Inference]** Two positions capture outsized economic rent: (1) ASML at EUV (true monopoly), and (2) the AI-compute stack (Nvidia + CUDA + HBM + CoWoS). TSMC captures rent because it is the *only* firm that can reliably manufacture the leading edge at scale. Profit is *competed away* in commodity DRAM/NAND (cyclical, near-zero at troughs), trailing-edge foundry (many suppliers), and traditional OSAT (labor-cost competition, now eroded by Chinese entrants). The pattern: **rent flows to whoever holds the scarcest non-substitutable capability at each node of the chain.**

### 3. Regional clusters — and why they exist
- **Taiwan:** TSMC + a deep ecosystem of design, materials, packaging, and skilled engineers. Cluster stickiness comes from tacit process know-how and co-located suppliers — not replicable by capital alone (**[Inference]**, evidenced by Arizona's slow ramp).
- **South Korea:** Samsung + SK Hynix — memory and logic, vertically integrated, state-backed.
- **United States:** design/IP/EDA leadership (Nvidia, AMD, Qualcomm, Synopsys, Cadence, Applied, Lam, KLA) but only ~10–12% of fabrication — the gap CHIPS Act targets.
- **Japan:** materials (photoresist, wafers), equipment (TEL, Screen), and image sensors; reviving leading-edge via Rapidus.
- **Netherlands:** ASML — the entire EUV world depends on one Dutch firm plus Germany's Zeiss.
- **China:** largest *consumer* of chips; building capacity (SMIC, CXMT, YMTC) but blocked from EUV and advanced tools by export controls, so pinned at ~7nm with yield/cost penalties.
- **Europe (ex-NL):** analog/power/automotive (Infineon, STMicro, NXP, Bosch).

### 4. Trade flows, import/export dependencies, national security
Chips are among the most globally traded goods, and the supply chain is deliberately interdependent — Taiwan fabs, Japanese materials, Dutch litho, US design/IP, Chinese assembly/consumption. **[Inference]** This interdependence is both an efficiency and a systemic fragility: the "Silicon Shield" thesis holds that Taiwan's TSMC centrality deters conflict, but it also concentrates ~90% of leading-edge logic in one seismically and geopolitically exposed island — the industry's single largest tail risk. Export controls have turned the supply chain into a geopolitical weapon: the US restricts advanced GPUs, EUV/DUV tools, and (2025) EDA to China; Japan and the Netherlands align on tool/material curbs; China retaliates with gallium/germanium/rare-earth controls.

### 5. Subsidies and industrial policy
- **US CHIPS Act:** >$33B finalized 2024 — TSMC $6.6B, Intel $7.86B, Micron $6.2B, Samsung $4.75B (**[Fact]** — https://www.manufacturingdive.com/news/chips-and-science-act-tracker-semiconductor-manufacturing/734039/). In 2025 the US floated taking *equity stakes* in awardees (notably Intel), a shift from grants to state ownership (**[Fact]** — reported 2025 — https://www.kedglobal.com/business-politics/newsView/ked202508200001).
- **EU Chips Act:** >€43B mobilized, 20%-share-by-2030 goal; STMicro/GlobalFoundries France plant got €2.9B state aid (**[Fact]** — https://fortune.com/2024/08/20/tsmc-eu-dresden-germany-chip-plant-intel-subsidies/).
- **Japan:** heavy subsidy of TSMC Kumamoto and Rapidus (2nm ambitions with IBM/imec).
- **China:** "Big Fund" phases totaling hundreds of billions of RMB to build a domestic, controls-proof supply chain.
**[Inference]** Subsidy has become a permanent feature; it distorts the cost of capital for new fabs and means "true" fab economics must be read net of grants.

### 6. What's gaining vs. losing relevance
**Gaining:**
- **AI accelerators + HBM + advanced packaging (CoWoS).** The dominant demand driver; DRAM revenue hit records on HBM (**[Fact]** — https://www.astutegroup.com/news/general/sk-hynix-holds-62-of-hbm-micron-overtakes-samsung-2026-battle-pivots-to-hbm4/).
- **Chiplets / heterogeneous integration** — the new axis of performance as monolithic scaling slows.
- **Gate-all-around/nanosheet (N2/18A/SF2)** and backside power delivery.
- **Compound semis (SiC/GaN)** for EV/power, though 2024–25 SiC saw an EV-driven glut.
- **RISC-V** — open ISA eroding Arm/x86 licensing economics over time.
- **Advanced packaging as a profit center** — re-rating OSAT and giving TSMC a second moat.

**Losing / at risk:**
- **Samsung Foundry** — share fell below ~8% and struggled on leading-edge yield vs. TSMC (**[Fact]** — TrendForce — https://www.trendforce.com/presscenter/news/20250310-12510.html).
- **Intel** — lost process leadership last decade; 18A/foundry is a bet-the-company turnaround; took CHIPS funds and possible US equity.
- **Commodity DRAM/NAND** — structurally cyclical, value competed away except in HBM.
- **Pure trailing-edge OSAT** — squeezed between Chinese cost competition and the shift of value into advanced packaging.

### 7. Real progress vs. promotional claims
**[Inference]** Node *names* ("2nm," "18A") are marketing labels, not physical gate lengths — real progress is measured in transistor density, performance-per-watt, and SRAM scaling (which has largely stalled, a genuine headwind). Treat "angstrom-era" branding skeptically; the meaningful transitions are FinFET→GAA and the arrival of backside power and High-NA EUV. Chinese "7nm" claims (SMIC) are real silicon but achieved via DUV multipatterning at low yield and high cost — technically impressive, economically not competitive at scale. HBM roadmaps (HBM4) are real and demand-backed, not hype. Conversely, many "AI chip startup" and "photonic/quantum will replace silicon soon" claims are promotional relative to near-term economics.

### 8. Where value is likely to MIGRATE
- **Toward packaging and interconnect.** As transistor scaling slows and costs balloon, more performance comes from how dies are combined — so value migrates from the fab's front-end toward advanced packaging, where TSMC and OSATs are positioning. **[Inference]**
- **Toward HBM/memory in the AI stack.** Memory bandwidth is the binding constraint for AI, shifting profit toward SK Hynix/Micron/Samsung HBM. **[Fact/Inference]** — record DRAM revenue confirms the shift.
- **Toward system-level design + software (CUDA-style lock-in).** The durable moat is increasingly the software ecosystem, not the transistor.
- **Away from commodity manufacturing** toward whoever controls the scarce capability (EUV, leading-edge yield, HBM, packaging capacity).
- **Contested: hyperscaler custom silicon (Google TPU, Amazon Trainium, Microsoft Maia).** If in-house accelerators succeed, value migrates from merchant fabless (Nvidia) toward hyperscalers + foundry — the biggest medium-term threat to the current profit pool. **[Inference]**

### 9. Disruption / obsolescence risks to watch
- A Taiwan geopolitical shock — the industry's dominant tail risk.
- RISC-V eroding IP licensing rent.
- Hyperscaler ASICs disintermediating merchant GPU vendors.
- A memory/AI capex air-pocket (the cycle always turns).
- Export-control escalation fragmenting the supply chain into US-aligned and China-aligned blocs, raising costs for all.

### 9. Complete output, customer, geography, funding, and policy map

Outputs include logic, memory, analog, power, RF, sensors, optoelectronics, discretes and microcontrollers; design IP, wafers, packaged/tested chips and manufacturing equipment/materials are separate markets. Scrap wafers, hazardous chemicals, fluorinated-gas emissions, wastewater and end-of-life electronics are residuals. Performance per watt, reliability, software support and qualified supply matter beyond transistor count.

Customers include cloud/data-center operators, device and hardware OEMs, autos, industrial/energy, telecom, defense/aerospace, distributors and contract manufacturers. A system architect may specify the chip, an OEM contracts it, a foundry fabricates it and a distributor holds inventory. Automotive and defense qualification make demand sticky but slow; consumer channels correct inventory quickly.

Design clusters in the US, Europe, Israel, India and Asia; leading foundry capacity is concentrated in Taiwan and Korea; memory in Korea and the US/Asia; equipment in the US, Netherlands and Japan; packaging/testing across East and Southeast Asia; raw/material niches are globally concentrated. Water, power, talent, supplier ecosystems and geopolitics keep clusters sticky.

Fabless designers, IDMs, foundries, OSATs, EDA/IP firms, equipment makers, materials suppliers and distributors capture different economics. Private funding includes corporate markets, venture capital and customer commitments; public funding includes sovereign grants, loans, tax incentives, public R&D and defense procurement. CHIPS-style industrial policy seeks resilience but cannot instantly recreate supplier density or workforce.

Policy covers export controls and sanctions, foreign-investment review, subsidies/local content, antitrust, IP, environmental and chemical rules, data/security assurance, defense trusted supply and trade tariffs. Cross-markets include AI/cloud, hardware, autos, electricity, critical minerals and capital equipment. A chip shortage can stop a much higher-value product; an end-market inventory correction can travel backward and collapse fab utilization despite long-term demand.

### Sources

- NIST, CHIPS for America — https://www.nist.gov/chips
- TrendForce foundry Q4 2024 shares — https://www.trendforce.com/presscenter/news/20250310-12510.html
- TrendForce OSAT 2024 rankings — https://www.trendforce.com/presscenter/news/20250513-12577.html
- Nvidia 10-K FY2025 — https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm
- DRAM/HBM share (Counterpoint/TechTimes) — https://www.techtimes.com/articles/318052/20260609/samsung-leads-dram-market-share-386-sk-hynix-trails-revenue-tops-profit-margins.htm
- HBM share — https://www.astutegroup.com/news/general/sk-hynix-holds-62-of-hbm-micron-overtakes-samsung-2026-battle-pivots-to-hbm4/
- Arm revenue — https://www.statista.com/statistics/1132055/arm-net-sales-by-segment-worldwide/
- EDA market — https://www.embedded.com/taking-stock-of-the-eda-industry/
- WFE market share — https://www.marketsandmarkets.com/ResearchInsight/semiconductor-manufacturing-equipment-market.asp
- CHIPS Act tracker — https://www.manufacturingdive.com/news/chips-and-science-act-tracker-semiconductor-manufacturing/734039/
- US equity-stake shift — https://www.kedglobal.com/business-politics/newsView/ked202508200001
- EU Chips Act — https://fortune.com/2024/08/20/tsmc-eu-dresden-germany-chip-plant-intel-subsidies/
- SIA 2025 sales — https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/

## 4. Operating Mechanics


### 1. The production workflow, step by step
A chip's life runs through four economically distinct stages. Value and margin concentrate very unevenly across them.

1. **Design (fabless / IDM design teams).** Architecture → RTL → logic synthesis → place-and-route → verification → tape-out. Tools are EDA (Synopsys/Cadence/Siemens); building blocks are IP cores (Arm, licensed interfaces). Output is a GDSII/OASIS layout file. **[Inference]** This stage has near-zero marginal cost and the highest gross margins in the industry — it sells design + brand, not atoms.
2. **Mask making.** The layout becomes a set of photomasks (reticles). An advanced EUV mask set costs several million dollars, amortized across every wafer of that design — which is why leading-edge only pays off at high volume.
3. **Front-end fabrication (the fab / foundry).** 300mm wafers pass through 1,000–1,500+ process steps over ~3 months: deposition (add film) → lithography (pattern) → etch (remove) → ion implant (dope) → CMP (planarize) → clean/metrology, repeated across dozens of mask layers. Sub-7nm uses EUV lithography; older nodes use immersion DUV (193nm) with multipatterning. Output: patterned wafers.
4. **Back-end (assembly, test, packaging — OSAT/ATP).** Wafer probe (test dies while still on wafer) → dice → attach/bond → encapsulate → final test → ship. Advanced packaging (2.5D/3D, chiplets, HBM stacks, TSMC's CoWoS) is where this stage stopped being a commodity and became strategic.

### 2. Competing methods — and why players choose differently
- **EUV vs. DUV multipatterning.** EUV (13.5nm wavelength) prints fine features in fewer exposures. DUV (193nm) can reach similar dimensions only via multipatterning (2–4x the mask/etch steps), which raises cost and cuts yield. **Rule:** EUV beats DUV multipatterning below ~7nm *because* the step-count and defectivity of multipatterning explode, making EUV cheaper per good die despite the $200M tool. Above ~10nm, DUV is cheaper because the EUV tool's capital and power cost isn't justified. **[Inference]** This is exactly why China (denied EUV) is stuck stretching DUV multipatterning at 7nm with poor yields.
- **Leading-edge (FinFET → Gate-All-Around/nanosheet, N3/N2/18A) vs. trailing-edge (28nm+).** GAA/nanosheet transistors (TSMC N2, Samsung SF2, Intel 18A "RibbonFET") improve performance/power at huge cost. Trailing-edge is mature, depreciated, and cash-generative — analog, power, MCU, and automotive chips do not need and cannot afford the leading edge. **Rule:** you go leading-edge only when performance-per-watt directly drives your customer's revenue (GPUs, flagship SoCs); otherwise trailing-edge wins on cost.
- **Monolithic SoC vs. chiplets.** As single dies hit reticle-size and yield limits, designers split the chip into smaller chiplets and reconnect them in-package (AMD, Nvidia, Intel). **Rule:** chiplets win at large die sizes *because* yield falls with die area — many small dies yield better than one huge one — and because you can mix nodes (compute on N3, I/O on N6). This made advanced packaging a bottleneck and a moat (see §7).
- **Silicon vs. compound semis (GaN, SiC).** For power electronics/EVs/RF, SiC and GaN beat silicon on switching efficiency and high-voltage handling. **Rule:** compound semis win where silicon's physics cap voltage/frequency; silicon wins everywhere cost and integration dominate.

### 3. Asset types and their economics
- **Leading-edge fab:** ~$20–28B, depreciates over ~5–7 years, obsolesces fast; needs ~$1B+/year to stay current. Economics live or die on utilization and yield.
- **Trailing-edge fab:** largely depreciated; a cash cow with 60–80%+ utilization economics and low reinvestment. GlobalFoundries and much of China's capacity live here.
- **OSAT/packaging assets:** cheaper, shorter-lived, historically low-margin — but advanced-packaging lines (CoWoS) now command premium pricing due to AI scarcity.
- **Fabless / IP / EDA:** asset-*light*. Their "assets" are people, patents, and tool licenses. Returns on invested capital dwarf the fabs' because they carry no fab depreciation.

### 4. Testing, qualification, approval
Yield is measured at wafer probe and final test; **defect density (D0, defects/cm²)** and **parametric yield** are the core quality metrics. Qualification for automotive (AEC-Q100) and mil/aero adds years of reliability testing (burn-in, HTOL). **[Inference]** Long qualification cycles are why automotive/industrial customers are sticky and why trailing-edge nodes have decade-long lives — re-qualifying a safety-critical part is expensive, so incumbents keep the socket.

### 5. How capacity is measured
- **Wafer starts per month (WSPM)** — the standard capacity unit, normalized to 300mm-equivalent.
- **Node mix** — share of revenue by process (TSMC: 3nm was 18% of wafer revenue in 2024; ≤7nm "advanced" was ~69–70%) (**[Fact]** — TSMC 2024 report — https://techsoda.substack.com/p/explainer-tsmcs-2024-annual-report).
- **Utilization %** — the swing factor for margins across the cycle.

### 6. Unit economics — the cost stack
Take a TSMC 3nm wafer at ~$18,000–20,000 list (**[Estimate]** — Morgan Stanley/TrendForce, 2024–25 — https://www.tomshardware.com/tech-industry/tsmcs-wafer-pricing-now-usd18-000-for-a-3nm-wafer-increased-by-over-3x-in-10-years-analyst). Against that:
- **Depreciation** is the single largest cost bucket at the leading edge (**[Inference]** — because the fab and its EUV tools are so capital-heavy; TSMC's D&A runs into the tens of billions annually).
- **Materials + chemicals + gases:** low-double-digit % of wafer cost.
- **Labor:** low single-digit % (fabs are automated).
- **Energy:** low single-digit %, rising.
- **Yield** converts wafer cost into *cost per good die*: a $18,000 wafer yielding 60% good die costs far more per chip than one at 90%.

Marginal cost of one more wafer, once the fab exists and is running, is dominated by materials/energy/consumables — a fraction of the fully-loaded cost. **[Inference]** This is the industry's defining economic feature: enormous fixed cost, low marginal cost → profits are hyper-sensitive to utilization, which is why the industry is violently cyclical.

**Gross-margin structure (2024, [Fact]):** TSMC 56.1% (https://techsoda.substack.com/p/explainer-tsmcs-2024-annual-report); ASML 51.3% (SEC 20-F); Nvidia (fabless) 75.0% for FY2025 (https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm). **[Inference]** The gradient — fabless > tool maker > foundry — shows where pricing power sits: design and IP capture more margin than manufacturing because manufacturing carries the capital.

### 7. Where margins are actually won: yield, utilization, packaging
The three levers that move a fab's profit: **yield** (good die/wafer), **utilization** (WSPM run vs. capacity), and **node leadership** (ability to charge a premium for the newest process). CoWoS/advanced packaging became a fourth lever in the AI era — TSMC's packaging capacity is a gating scarcity for every Nvidia GPU, giving TSMC pricing power it never had in commodity assembly.

### 8. KPIs practitioners track
Revenue by node, gross/operating margin, capex intensity (capex/revenue), utilization %, D0/defect density, book-to-bill (equipment makers), inventory days & DIO (cycle indicator), ASP per wafer, and for memory: bit growth and $/Gb. **[Inference]** Book-to-bill and inventory days are the best *leading* indicators of the cycle turning.

### 9. Development and lead timelines
- New process node: ~2–3 years R&D + ramp; nodes arrive on a ~2-year cadence.
- New fab: 2–4 years to build and qualify; TSMC Arizona slipped on labor/permits.
- EUV tool delivery: 12–18 months.
- Automotive qualification: 1–3 years.
**[Inference]** These long lead times cause the classic semiconductor cycle: capacity ordered in a boom arrives in a bust (and vice versa), guaranteeing over/under-shooting.

### 10. Characteristic failure points
Yield crashes on a new node (Samsung and Intel both lost customers to yield stumbles); a single contaminated chemical lot; EUV mask defects; a fab power/water interruption; cyclical demand air-pockets that strand fixed cost; and export-control shocks that strand capacity or customers.

### 11. VALUATION across company life-stages

#### (a) Mature, cash-generative businesses (TSMC, ASML, Applied, Texas Instruments, Broadcom)
Value on **earnings and cash flow**: P/E, EV/EBITDA, and free-cash-flow yield / DCF. Watch **capex intensity** — a foundry guiding capex up (TSMC $38–42B for 2025) trades near-term FCF for future capacity, so the market prices the return on that capex, not just current earnings. **[Inference]** For toolmakers and IP/EDA (asset-light, recurring, high-margin), the market pays premium multiples (often 25–40x earnings) because revenue is stickier and ROIC is high; for foundries the multiple is lower because capital intensity depresses FCF conversion. Key ratios: gross margin trend, ROIC vs. WACC, and capex/sales.

#### (b) Cyclical / asset-heavy businesses across the cycle (memory — Micron, SK Hynix; commodity foundry; equipment)
Never value these on trough or peak earnings — earnings swing from huge losses to huge profits within the same asset base. Use:
- **Price / book (P/B) and price / tangible book** — the classic memory-cycle tool: buy near ~1x book at the trough, trim as it approaches 2–3x at the peak. **[Inference]** Because the asset base is stable while earnings gyrate, book value is a steadier anchor than EPS.
- **Mid-cycle / normalized earnings** — average margins across a full cycle and apply a modest multiple.
- **Replacement value** of the fab base and **$/Gb cost curve** position for memory.
- **EV/EBITDA on normalized EBITDA**, and inventory/book-to-bill as timing signals. The mistake to avoid: a low P/E at the peak (earnings about to collapse) looks "cheap" but is a value trap; a high or negative P/E at the trough often marks the buy.

#### (c) Pre-revenue / early / IP- or milestone-driven (startups, RISC-V design houses, compound-semi entrants, national fabs)
No cash flows to discount, so value rests on optionality and comparables:
- **IP / patent portfolio and design wins** — value by comparable licensing economics (e.g., Arm's royalty model: ~$1.8B royalties on a large installed base — https://www.statista.com/statistics/1132055/arm-net-sales-by-segment-worldwide/) and by revenue-multiple comps to listed peers.
- **Probability-adjusted (risk-weighted) DCF / real-options** — assign probabilities to technical milestones (tape-out, yield target, qualification) and discount the resulting cash flows heavily.
- **Capacity/reserve-style valuation** for capital projects: value committed WSPM capacity net of build cost and subsidy, discounted for ramp and utilization risk.
- **Comparable-transaction / VC-round multiples** and strategic value to acquirers (an EDA or IP tuck-in is often worth more to Synopsys/Cadence than standalone).
**[Inference]** For these, the dominant value driver is a *binary technical event* (does the node yield? does the tool work?), so scenario/probability weighting matters more than a single point DCF, and the discount rate should be high to reflect execution risk.

#### Cross-cutting valuation cautions
- **Cyclicality dominates:** always ask where in the cycle the multiple is being struck.
- **Subsidy distortion:** CHIPS/EU grants inflate reported returns on new fabs; strip them to see true economics.
- **Concentration risk:** a fabless firm dependent on one foundry (TSMC) or one customer carries a discount; a monopolist (ASML) carries a premium.

### 9. Complete design-to-yield and cash-conversion mechanics

The chain is architecture/specification → RTL/circuit design and IP integration → verification → tape-out/mask → wafer fabrication through repeated pattern/deposit/etch/doping steps → wafer probe → dice and advanced/conventional package → final test/qualification → board/system integration → field support and end-of-life notice. A defect or design change can require an expensive respin and months of cycle time.

Capacity must be measured by compatible wafer starts, layer count, cycle time, yield and package/test—not generic fab square footage. Saleable dies per wafer depend on die area and yield; cost includes wafer, mask/NRE, package/test, scrap, royalties and depreciation. Leading nodes, memory and mature analog/power have different pricing and cycle behavior.

Revenue can be unit/product sales, wafer service, take-or-pay reservation, license/royalty, equipment sale plus service or distribution margin. Deposits and noncancellable orders can improve visibility but create customer inventory. Working capital spans long WIP, finished goods, channel inventory, prepayments and supplier commitments; equipment firms add backlog and customer acceptance milestones.

Track design wins versus production revenue, wafer starts, utilization, cycle time, die and final yield, ASP/mix, inventory days by stage, channel weeks, capex and depreciation, node/package mix, foundry/OSAT concentration and R&D. Stress end-demand decline, double ordering unwind, yield shortfall, tool/material outage, power/water interruption, export restriction, earthquake/geopolitical loss, rapid node transition and advanced-packaging bottleneck.

### Sources
- TSMC 2024 report highlights (margin, node mix) — https://techsoda.substack.com/p/explainer-tsmcs-2024-annual-report
- TSMC 4Q24 6-K (capex/margins) — https://www.sec.gov/Archives/edgar/data/1046179/000104617925000004/a4q24e_withguidancexfinal.htm
- 3nm wafer price estimate — https://www.tomshardware.com/tech-industry/tsmcs-wafer-pricing-now-usd18-000-for-a-3nm-wafer-increased-by-over-3x-in-10-years-analyst
- 2nm fab cost / $/wafer — https://www.tomshardware.com/tech-industry/firm-predicts-it-will-cost-dollar28-billion-to-build-a-2nm-fab-and-dollar30000-per-wafer
- ASML 20-F FY2024 (gross margin, EUV) — https://www.sec.gov/Archives/edgar/data/0000937966/000093796625000009/asml-20241231.htm
- Nvidia 10-K FY2025 (gross margin, DC revenue) — https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm
- Nvidia Q4 FY25 CFO commentary — https://www.sec.gov/Archives/edgar/data/1045810/000104581025000021/q4fy25cfocommentary.htm
- Arm revenue split — https://www.statista.com/statistics/1132055/arm-net-sales-by-segment-worldwide/
- EUV vs. patterning economics — https://newsletter.semianalysis.com/p/euv-requirements-halved-applied-materials

## 5. Economics and Valuation


Benchmark bands are diagnostic starting points; refresh for product, asset, geography, contract, and cycle.

### Core unit-economic identity

Chip gross profit = packaged good dies × ASP − wafer/foundry − mask/NRE amortization − package/test − royalties − scrap and warranty. Manufacturing return subtracts R&D, depreciation, sustaining and growth capex, inventory and working capital.

### Ten benchmark measures

| Measure | Diagnostic band or unit | Decision use |
| --- | --- | --- |
| Leading-edge fab cost | often roughly $10–30B+ for a new advanced site/phase | Capital barrier |
| Fab build/ramp | roughly 3–5+ years including qualification | Supply response |
| Wafer cycle time | often 2–4 months; process-specific | WIP and response |
| Fab utilization | roughly 80–95% in balanced periods | Fixed-cost absorption |
| Mature/leading yield | wide, often ~60–95% after ramp | Cost and ramp quality |
| R&D intensity | often ~15–30% of sales for design leaders | Innovation burden |
| Gross margin | ~40–70% for many differentiated designers/IDMs; model-specific | Product and foundry economics |
| Inventory days | often ~70–150 across cycle/model | Correction risk |
| Equipment service share | installed-base service as percent of revenue | Recurring quality |
| Advanced-package bottleneck | substrate/interposer/HBM/package output and lead time | System supply |

### Accounting-to-cash bridge

Separate sell-in/sell-through, channel inventory, wafer and packaged inventory, foundry prepayments, take-or-pay, nonrecurring engineering, capitalization, depreciation, equipment acceptance, license/royalty and government incentives.

### Highest-value sensitivities

- End demand, customer inventory/double ordering, memory pricing and product mix.
- Yield, die size, wafer price, package/HBM/substrate, utilization and depreciation.
- Tool/material availability, power/water, earthquake/geopolitics and export controls.
- Node transition, software ecosystem, customer custom silicon and R&D execution.

### Valuation discipline

Use product-cycle and structural moat together; separate design/IP, foundry/IDM, memory, OSAT and equipment. Normalize inventory and utilization; risk capital intensity and node relevance.


## 6. Regulation and Public Funding


Snapshot reviewed through **2026-07-14**. Verify enacted text, implementation dates, litigation, and current guidance.

### Permission chain

Architect/OEM specifies; fabless/IDM designs; EDA/IP enables; foundry fabricates; equipment/material firms supply; OSAT packages/tests; distributor holds; system OEM integrates; cloud/consumer/auto/industrial customer uses; governments regulate trade/security.

### Jurisdiction and regime map

| Jurisdiction or layer | Core regimes and authorities | Economic transmission |
| --- | --- | --- |
| United States | BIS export controls, NIST CHIPS incentives/R&D, foreign investment, trusted defense supply and environmental permitting | Customer/tool access, grants, security and fab location |
| European Union | EU Chips Act, state aid, export coordination, chemical/environmental rules | Fab/equipment support and supply-chain policy |
| Japan, Korea and Taiwan | National incentives, export controls and strategic manufacturing policy | Cluster capacity, materials and trade |
| China | Industrial subsidies, localization, export/import controls and data/security | Demand, capacity, retaliation and technology access |

### Public and private funding

Private funding includes corporate cash/debt/equity, venture, customer prepayments, take-or-pay, foundry and equipment finance. Public funding includes grants, loans, tax credits, R&D, defense procurement and infrastructure through CHIPS-style programs.

### Enforcement and liability

Export-control penalties, incentive clawbacks, IP claims, environmental shutdown, trusted-supply disqualification, product recall and antitrust remedies can reshape markets.

### Update checklist

- Confirm entity, asset, product, customer, location, and authority.
- Separate law, final rule, guidance, permit, litigation, and proposal.
- Date funding, tax, tariff, sanction, quota, and administered-price terms.
- Trace cost, schedule, capacity, price, liability, and funding separately.


## 7. Historical Cases and Failure Patterns


Cases are selected for reusable causal lessons.

### Historical and operating episodes

| Episode | Initial condition or shock | Transmission and outcome | Reusable lesson |
| --- | --- | --- | --- |
| 1980s US-Japan memory cycle | Japanese scale challenged US memory producers | Trade policy and exits changed industry structure | Technology leadership is segment-specific |
| 2011 Japan earthquake | Materials and component clusters were disrupted | Global auto/electronics supply tightened | Small qualified inputs can cap global output |
| 2018–2019 memory downturn | Prior capacity met inventory correction | ASP/bit and margins collapsed despite bit growth | Secular demand does not erase cycles |
| 2020–2022 chip shortage | Demand shifts and double ordering met fixed fab/package capacity | Autos and industrial systems stopped for low-cost chips | Content value differs from system criticality |
| 2023–2026 AI/HBM buildout | Accelerator demand concentrated on leading foundry, HBM and packaging | Bottleneck value migrated across the stack | System throughput, not one chip, sets output |

### Practitioner extraction

- **Leading signals:** Design wins, cloud/OEM capex, wafer starts, utilization, inventory, memory spot/contract, equipment orders, package/HBM lead, export rules.
- **Evidence that breaks the easy thesis:** TAM claims without production sockets, capacity announcements without tools/power/customers, or revenue growth driven by channel inventory.
- **Durable lesson:** The saleable unit is a yielded, packaged, tested and software-enabled chip in a qualified system.


## 8. Data Sources and Monitoring Dashboard


Preserve observation period, unit, definition, geography, and revision vintage.

### Primary source map

| Source | Cadence | Best use | Caveat |
| --- | --- | --- | --- |
| [NIST CHIPS for America](https://www.nist.gov/chips) | program/event-driven | US incentives and R&D | Awards differ from construction/output |
| [BIS export administration](https://www.bis.gov/) | rule-driven | Export controls and entity restrictions | Rapidly changing |
| [SEC EDGAR filings](https://www.sec.gov/edgar/search/) | quarterly/annual | Revenue, inventory, capacity and capex | Company definitions |
| [US Census manufacturing/trade](https://www.census.gov/manufacturing/) | monthly/annual | US output, orders and trade | Broad product classes |
| [Federal Reserve industrial production](https://www.federalreserve.gov/releases/g17/) | monthly | Semiconductor production/utilization indexes | Index and US-focused |

### Indicator stack

- **Leading:** design wins; capex plans; equipment book-to-bill; memory prices; lead times; export rules.
- **Coincident:** shipments; wafer starts; utilization; yield; inventory; ASP/mix.
- **Lagging:** fab deliveries; depreciation; node share; impairments; installed base.

### Minimum dashboard

1. **Leading-edge fab cost** — often roughly $10–30B+ for a new advanced site/phase; Capital barrier.
2. **Fab build/ramp** — roughly 3–5+ years including qualification; Supply response.
3. **Wafer cycle time** — often 2–4 months; process-specific; WIP and response.
4. **Fab utilization** — roughly 80–95% in balanced periods; Fixed-cost absorption.
5. **Mature/leading yield** — wide, often ~60–95% after ramp; Cost and ramp quality.
6. **R&D intensity** — often ~15–30% of sales for design leaders; Innovation burden.
7. **Gross margin** — ~40–70% for many differentiated designers/IDMs; model-specific; Product and foundry economics.
8. **Inventory days** — often ~70–150 across cycle/model; Correction risk.
9. **Equipment service share** — installed-base service as percent of revenue; Recurring quality.
10. **Advanced-package bottleneck** — substrate/interposer/HBM/package output and lead time; System supply.

### Normalization rules

- Use bits/dies/wafers and node separately.
- Track sell-through and channel.
- Adjust yield for die size/package.
- Separate incentive from operating return.

### Evidence traps

- Treating node name as performance.
- Counting wafer capacity without package/test.
- Using end-market TAM as supplier revenue.

## 9. Geographic Operating Models

Geography changes ownership, contracting, cost, funding, regulation and risk; compare like with like.

| Geography / archetype | Operating model | Economic and risk implications |
| --- | --- | --- |
| Taiwan | Leading-edge pure-play foundry plus dense packaging, substrate and electronics supply chains | Earthquake, power/water, geopolitics and customer concentration create system-level risk |
| South Korea | Memory champions and advanced logic/foundry investment supported by conglomerate scale | Memory cycles, HBM packaging and capital intensity drive volatility |
| United States | Fabless design, EDA/IP, equipment and selected leading-edge/analog manufacturing | Design leadership depends on offshore fabrication while industrial policy raises domestic capital |
| China | State-backed expansion across mature-node fabrication, design, packaging and equipment localization | Export controls and self-sufficiency funding reshape global mature-node balance |
| Japan and Europe | Critical materials/equipment plus automotive, industrial, power and specialty semiconductor production | Qualification, reliability and long product cycles support niches despite less leading-edge logic |

## 10. Cross-Industry Dependency Map

| Dependency class | Linked markets and institutions | Transmission into this industry |
| --- | --- | --- |
| Design stack | EDA, processor/interface IP, software, architecture talent and cloud compute | Tool/IP access and developer ecosystems determine whether silicon becomes a usable product |
| Fabrication inputs | Wafers, lithography, deposition/etch, specialty gases, photoresist, masks, power and ultrapure water | A single qualified material/tool bottleneck can cap global output |
| Back end | Assembly, substrates, advanced packaging, HBM, test equipment and logistics | Yielded wafer capacity can be stranded without package/test capacity |
| Customers | Cloud, smartphones, PCs, autos, industrial, networking, defense and consumer electronics | End-demand and customer inventories transmit differently by segment |
| Capital/policy | Customer prepayments, corporate capex, equipment finance, grants, tax credits and export controls | Subsidies alter location, while tool controls segment accessible technology |

The practical test is to trace a shock through availability, delivered cost, working capital, output, customer economics, financing and eventual substitution—not merely name the adjacent market.

## 11. Decision-Grade Unit Economics

> The numerical example below is illustrative, not a current market forecast or universal benchmark. Replace every assumption with asset-, contract-, product- and geography-specific evidence.

**Representative unit:** One 300 mm wafer for a high-value logic product.

**Core equation:** `Wafer contribution = gross die × yield × net ASP/die − wafer processing − mask/design amortization − package/test − allocated fab fixed/capital cost` 

| Bridge item | Illustrative assumption and calculation | Result / interpretation |
| --- | --- | --- |
| Good die | 600 gross die/wafer × 85% final electrical yield | 510 saleable die before package loss |
| Net die revenue | 510 × $80 net ASP | $40.8k/wafer |
| Wafer fabrication | Materials, process tools, power, labor and variable fab cost | $18.0k/wafer |
| Design/mask amortization | Allocated NRE, masks and engineering change cost | $4.0k/wafer |
| Package and test | Advanced package, memory/interface content and final test | $8.0k/wafer |
| Illustrative contribution | $40.8k − $18.0k − $4.0k − $8.0k − $7.0k fixed/capital allocation | $3.8k/wafer; small yield or ASP moves can dominate |

**Decision test:** Underwrite good packaged systems—not wafer starts—using product-specific die size, yield learning, package capacity, ASP decay, customer qualification and full node capital.

## 12. Industry Balance and Marginal Economics

| Balance concept | Industry-specific definition | What to measure |
| --- | --- | --- |
| Marginal supply unit | Highest-cost qualified wafer/package capacity needed for a specific node, process and product | Node labels do not make fabs interchangeable |
| Marginal customer | OEM/cloud/auto buyer able to redesign, dual-source, use inventory or delay systems | Qualification and software switching constrain elasticity |
| Clearing mechanism | Long-term wafer agreements, foundry quotes and negotiated chip pricing; memory also uses spot/contract markets | Channel spot prices may not represent OEM contracts |
| Cash shutdown point | Mature line runs while price covers variable process/package cost and strategic commitments | High fixed cost encourages output, deepening downcycles |
| New-capacity incentive | Expected multiyear utilization and pricing cover fab/tool capital, yield ramp and cost of capital | Customer commitments and policy support reduce but do not remove cycle risk |
| Adjustment lag | Weeks for mix, quarters for yield/tools, years for fabs and ecosystems | Demand can change far faster than qualified supply |

## 13. Terminology and Comparability Traps

| Reported term | Common but invalid interpretation | Required normalization |
| --- | --- | --- |
| Process node | Comparable density, performance or cost | Use product PPA, design rules, yield, die size and actual process variant |
| Wafer capacity | Saleable chip output | Adjust wafer diameter, starts, cycle time, yield, die size, package and test |
| Yield | One standardized metric | Specify wafer, die, parametric, package and final-test yield plus learning stage |
| Design win | Guaranteed revenue | Risk qualification, launch volume, content, share, ASP and lifetime |
| TAM | Serviceable revenue | Constrain by sockets, share, content, production, software and customer economics |


