# Insurance

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

Property/casualty, life and annuity, health insurance, reinsurance, brokers, MGAs and insurance-linked capital.

### Operating taxonomy

| Segment | What is sold | Primary unit | Do not aggregate without |
| --- | --- | --- | --- |
| Personal and commercial P&C | Property, auto, liability and specialty risk | premium, exposure units, limits | Accident year, peril, attachment, limit, geography and wording |
| Life and annuity | Mortality, longevity, savings and guarantees | face amount, account value, policies | Guarantee, lapse, duration, credit and hedging |
| Health insurance | Medical risk, administration and networks | member months, premium, claims | Population, benefit, risk adjustment, network and funding |
| Reinsurance and ILS | Treaty/facultative, retrocession and catastrophe capital | premium, limit, attachment, collateral | Occurrence/aggregate, peril, reinstatement and collectability |
| Brokers, MGAs and services | Distribution, underwriting authority, claims/data | revenue, premium placed, retention | Who owns client, sets price and bears risk |

### Specifications that change value

- State policy period, exposure, peril, geography, trigger, attachment, limit, deductible, exclusions and aggregate.
- Claims need accident/report/payment year, frequency, severity, case/IBNR and gross/net/ceded.
- Life/annuity needs guarantee, account value, surrender, duration, option and hedge.
- Health needs member cohort, benefit, provider contract, risk adjustment and medical trend.
- Reinsurance needs treaty, occurrence/aggregate, reinstatement, collateral and counterparty.

### Role map

Policyholder pays; insured is exposed; beneficiary receives; broker/MGA distributes/underwrites; carrier issues and holds capital; reinsurer/ILS takes tail; claims/vendor network settles; regulator/rating agency constrains.

### Terms that must be explicit

- written versus earned premium
- incurred, paid, case and IBNR loss
- accident year versus calendar year
- gross, ceded and net
- combined ratio versus investment result


## 2. Inputs and Dependencies


Scope note: "Insurance" here spans the risk-transfer value chain — primary P&C (property & casualty / general insurance), life & annuities (L&A), health, and the reinsurance and capital-markets layers that stand behind them. The single most important framing for the reader: **insurance is a business that sells a promise today and pays claims later, funding the gap by investing "float." Its two true raw materials are (1) risk-bearing capital and (2) information about risk. Almost everything else on this list is downstream of those two.**

---

### 1. Financial capital — the binding input

Capital is the raw material that determines how much risk an insurer may underwrite. Regulators cap premium relative to capital (a solvency constraint), so **capital, not factory capacity, is what limits "production."**

- **Equity/statutory capital.** US insurers are constrained by NAIC Risk-Based Capital (RBC); European insurers by Solvency II's Solvency Capital Requirement. A carrier writing at, say, a ~1.5–2.0x premium-to-surplus ratio can only grow premium as fast as surplus grows (retained underwriting profit + investment income + new equity). **[Fact]** The industry's surplus swings drive the "underwriting cycle": after capital is destroyed by catastrophes, capacity shrinks and prices harden.
- **Reinsurance capital.** Primary insurers rent balance sheet from reinsurers to write more than their own capital allows. When reinsurance capital contracted, price and terms moved violently: **dedicated reinsurance capital eroded 15.7% to ~$355bn at year-end 2022, the biggest squeeze since 2008**, producing "the hardest property-catastrophe reinsurance market in a generation" at the January 2023 renewals (Insurance Journal, 2023 — https://www.insurancejournal.com/news/international/2023/01/04/701632.htm). **[Fact]**
- **Alternative / capital-markets capital (ILS).** Catastrophe bonds and collateralized reinsurance let pension funds and hedge funds supply risk capital directly. **Cat bond issuance hit a record $17.7bn in 2024, taking outstanding ILS to ~$49.5bn** (Artemis/Aon, 2024 — https://www.reinsurancene.ws/cat-bond-issuance-hits-record-17-7bn-in-2024-report/). **[Fact]** This is the marginal, mobile supply of peak-peril capacity — when it floods in, property-cat rates soften; when it retreats, they spike.

**[Inference]** Pricing power over capital sits with the capital provider precisely when capital is scarce (post-catastrophe hard markets). In soft markets, abundant capital competes away returns. So the industry's margins are set less by claims frequency in any year than by the *supply of risk capital* relative to demand.

---

### 2. Investable assets & interest rates — the "float engine"

Insurers collect premium before paying claims and invest the difference. **Berkshire Hathaway's insurance float reached ~$171bn in 2024, alongside ~$11.4bn of underwriting profit** — i.e. negative-cost float (Berkshire 2024 Annual Report — https://www.berkshirehathaway.com/2024ar/2024ar.pdf). **[Fact]** Float is invested overwhelmingly in **fixed income**, so the yield on high-grade bonds is a direct input to profitability.

- **Cost sensitivity.** A rise in interest rates raises reinvestment yields and is the main reason US P&C net investment income and net income surged in 2024 (net income +89.8% to $169.3bn) (NAIC 2024 P&C report — https://content.naic.org/sites/default/files/2024-annual-property-casualty-and-title-insurance-industries-analysis-report.pdf). **[Fact]** But rate *increases* simultaneously mark down the value of existing bond holdings, hitting statutory surplus and, for life insurers, can trigger surrenders (disintermediation).
- **Life insurers** are the extreme case: their product *is* an interest-rate spread. The private-equity-owned annuity model (Apollo/Athene, KKR/Global Atlantic) turns the insurer into a distribution front-end for a credit-investing machine. **Global Atlantic's AUM grew to ~$158bn from ~$72bn (2020) under KKR; Apollo total AUM was ~$751bn at end-2024** (KKR/Apollo filings via AI-CIO/Insurance Journal, 2024 — https://www.ai-cio.com/news/kkr-announces-acquisition-of-remaining-37-of-global-atlantic-for-2-7b/). **[Fact]** The input here is *investment yield origination*: private credit spread is the raw material that funds annuity crediting rates.

**[Inference]** For life/annuity carriers, the binding input is access to high-yielding, well-matched assets; for P&C, it is high-grade liquid bonds plus enough duration to match short-tail claims. The whole industry is therefore levered to central-bank policy in a way most "product" industries are not.

---

### 3. Information & risk data — the other raw material

Underwriting is manufacturing priced-risk out of data. Key data inputs:

- **Catastrophe models** (Verisk/AIR, Moody's RMS, CoreLogic). These vendor models are near-mandatory infrastructure for property-cat pricing and reinsurance placement; a model version change can reprice an entire book. **[Fact — vendor identities]**; **[Inference]** the modeling duopoly (Verisk + Moody's RMS) holds real pricing power over cat-exposed carriers because switching models means re-explaining capital to regulators and rating agencies.
- **Rating/loss-cost bureaus.** ISO (Verisk) supplies standardized policy forms and advisory loss costs; NCCI supplies workers'-comp loss costs. Small and mid carriers depend on these as a shared statistical backbone.
- **Personal-line behavioral data / telematics.** Usage-based auto insurance (Progressive Snapshot) converts driving data into a rating variable and a selection advantage. Progressive ran combined ratios of ~84.5 (Q1), 91.9 (Q2), 89.0 (Q3) in 2024 — well inside the ~100 breakeven (Progressive 10-Qs, 2024 — https://www.sec.gov/Archives/edgar/data/80661/000008066124000018/pgr-20240331.htm). **[Fact]** **[Inference]** Proprietary data is the one input a carrier can *own*, and it is where durable underwriting moats are built (see LANDSCAPE).
- **Credit/health/third-party data.** Credit-based insurance scores, MVRs, medical/actuarial mortality tables (SOA), and increasingly third-party AI-scored data.

---

### 4. Human capital

- **Actuaries** price risk and set reserves. Scarce and credential-gated (multi-year exam pipeline). **US median wage $125,770 (May 2024); ~33,600 employed; projected +22% growth 2024–34, "much faster than average"** (BLS OOH — https://www.bls.gov/ooh/math/actuaries.htm). **[Fact]** The credentialing bottleneck (years of exams) makes actuarial labor structurally tight; it is a genuine capacity constraint on launching new products/geographies. **[Inference]**
- **Underwriters, claims adjusters, and catastrophe field staff.** Claims labor is surge-demand: a single hurricane requires thousands of adjusters at once, a bottleneck that inflates loss-adjustment expense (LAE) after big events. **[Inference]**
- **Distribution labor** — agents and brokers (see §6).
- **Investment professionals** — critical for the PE-owned L&A model.

---

### 5. Software, IP & technology infrastructure

- **Core systems (policy admin, billing, claims).** Guidewire InsuranceSuite is the reference platform for large P&C carriers; Duck Creek is the closest enterprise competitor (industry buyer analyses, 2026 — https://www.viewpointanalysis.com/post/insurance-software-options-2026). **[Fact — vendor positioning]** Core-system replacement is a multi-year, high-risk program; incumbency gives these vendors strong lock-in and pricing power over carriers. **[Inference]**
- **Cat models, pricing engines, fraud analytics, and increasingly LLM/AI tooling** for claims triage and submission intake.
- **Actuarial/reserving and capital-modeling software.**

**[Inference]** Software is a rising share of the expense ratio but remains small versus claims cost; it competes on the *expense* line, not the *loss* line, so its leverage on margin is real but bounded.

---

### 6. Distribution — the largest controllable cost

Insurance is sold, not bought, and the channel takes a large, sticky cut.

- **Brokers/agents.** **Marsh McLennan (largest broker, 14 years running) reported ~$25.33bn brokerage revenue in 2024 (incl. McGriff pro forma), +13.4%; Aon is #2** (Business Insurance / AM Best 2024 — https://www.businessinsurance.com/top-insurance-brokers-no-1-marsh-mclennan-cos-inc-3/). **[Fact]** Commissions and broker fees are a first claim on premium before the carrier sees a cent.
- **Pricing power.** In commercial/specialty lines, the mega-brokers (Marsh, Aon, Gallagher, WTW) aggregate buyer demand and hold real leverage over carriers; their organic-growth-plus-M&A model has made brokerage arguably more consistently profitable than underwriting. **[Inference]** In personal lines, direct writers (Progressive, GEICO) internalize distribution to compress this cost — a structural margin advantage.

---

### 7. Regulation & legal environment (a "supplied" input)

- **Solvency regimes** (NAIC RBC, Solvency II, Bermuda's BMA) set the capital cost of writing business and, via reserving/asset rules, shape which assets back liabilities.
- **Rate regulation.** In personal lines, state regulators (e.g., California under Prop 103) must approve rate changes. Regulatory rate suppression relative to loss-cost inflation directly caused capacity withdrawal: **State Farm non-renewed ~30,000 California policies in March 2024 and had stopped writing new business in May 2023** as rebuilding-cost and wildfire loss costs outran approved rates (Insurance Journal, 2024 — https://www.insurancejournal.com/news/west/2024/03/20/765883.htm). **[Fact]** This is the clearest live example of a regulatory input capping "production."
- **Legal/tort environment ("social inflation").** Litigation trends and jury verdicts are an uncontrollable cost input to casualty lines, inflating loss severity years after a policy is priced. **[Inference]**

---

### 8. How a shock propagates (worked example)

**Shock: a large hurricane season depletes catastrophe capital.**
1. Reinsurers absorb losses → dedicated reinsurance capital falls (as in 2022, −15.7% to ~$355bn).
2. Reinsurance renewals reprice: rates-on-line jump, attachment points rise, cedents forced to retain more risk (Jan 2023).
3. Primary carriers face higher reinsurance cost and less coverage → they raise primary rates and/or shrink exposure in cat-prone regions.
4. In rate-regulated states where increases lag, carriers exit (California). Residual markets (FAIR Plans) balloon — **California FAIR Plan residential exposure reached ~$458bn by Sept 2024** (Insurance Journal, 2024 — https://www.insurancejournal.com/news/west/2024/03/20/765883.htm). **[Fact]**
5. ILS/cat-bond investors, seeing higher rates-on-line, supply fresh capital (record 2024 issuance) → capacity rebuilds → prices eventually soften.

**[Inference]** The chain shows the master variable: **risk capital supply**. Claims are the trigger, but the price of capital is the transmission mechanism, and the availability of *substitute* capital (ILS vs. traditional reinsurance vs. equity) sets how fast the cycle turns.

---

### 9. What caps capacity vs. what sets margin — summary

- **Caps production capacity:** statutory/regulatory capital, reinsurance availability, and (in the long tail) actuarial talent. **[Inference]**
- **Sets margins:** the loss ratio (claims frequency × severity, driven by cat activity, inflation, and social inflation), the price of risk capital in the cycle, investment yields on float, and the distribution/expense take. **[Inference]**
- **Single points of failure / bottlenecks:** the cat-model duopoly (Verisk/RMS), the core-software incumbents (Guidewire/Duck Creek), reinsurance concentration in a handful of carriers (see LANDSCAPE), and surge claims-labor after mega-events.

---

### 10. Full risk-capacity and service input ledger

Risk exposure is the fundamental raw material: property, liability, mortality, morbidity, longevity, cyber, credit, catastrophe and behavioral/lapse risks enter through policy applications and portfolios. Underwriting requires exposure data, claims history, medical/credit/property records where legal, catastrophe and actuarial models, geospatial/weather data, inspections, legal wording and a credible price. Bad or legally unusable data is an input constraint, not merely an analytical weakness.

Capacity comes from equity and surplus, retained earnings, reinsurance, retrocession, catastrophe bonds/ILS, letters of credit and, for life/annuities, long-duration investment assets and hedging. Distribution requires agents, brokers, MGAs, employer/benefit channels, banks, comparison platforms and brand. Claims production needs adjusters, repair networks, medical providers, lawyers, fraud tools, call centers and salvage/recovery.

The physical/digital substrate includes secure policy/claims systems, cloud/data centers, telecom, payment rails, document storage, cyber defenses and disaster-response facilities. Insurers indirectly consume construction labor/materials, auto parts, healthcare, pharmaceuticals and funeral services through claims; their price and availability are core loss-cost inputs.

Funding includes policyholder premiums and float, debt/equity, holding-company liquidity, reinsurance and capital markets; public flood, crop, health, pension-guarantee and terrorism programs can share or backstop risk. Premium rate, loss trend, investment yield and reinsurance cost set margin; regulatory capital, ratings, aggregate limits, claims capacity, distribution and permissions cap writings. Deductibles, self-insurance, captives, parametric covers, prevention and public pools substitute for traditional insurance but reallocate basis and tail risk.

### Sources
- Swiss Re Institute, sigma 3/2024 & 2/2025 world insurance — https://www.swissre.com/institute/research/sigma-research/sigma-2024-03-world-insurance-global-resilience.html
- NAIC, 2024 Annual P&C and Title Insurance Industries Analysis Report — https://content.naic.org/sites/default/files/2024-annual-property-casualty-and-title-insurance-industries-analysis-report.pdf
- Berkshire Hathaway 2024 Annual Report (float, underwriting profit) — https://www.berkshirehathaway.com/2024ar/2024ar.pdf
- Insurance Journal, "January Renewals See Hardest Property Catastrophe Reinsurance Rates in Generation" (2023) — https://www.insurancejournal.com/news/international/2023/01/04/701632.htm
- Reinsurance News, "Cat bond issuance hits record $17.7bn in 2024" — https://www.reinsurancene.ws/cat-bond-issuance-hits-record-17-7bn-in-2024-report/
- BLS, Occupational Outlook Handbook — Actuaries (May 2024) — https://www.bls.gov/ooh/math/actuaries.htm
- Business Insurance, Top insurance brokers No.1 Marsh & McLennan — https://www.businessinsurance.com/top-insurance-brokers-no-1-marsh-mclennan-cos-inc-3/
- Progressive Corp Form 10-Q, 2024 — https://www.sec.gov/Archives/edgar/data/80661/000008066124000018/pgr-20240331.htm
- Insurance Journal, "State Farm Nonrenewing 30K California Homeowners" (2024) — https://www.insurancejournal.com/news/west/2024/03/20/765883.htm
- AI-CIO, KKR acquisition of Global Atlantic (AUM figures) — https://www.ai-cio.com/news/kkr-announces-acquisition-of-remaining-37-of-global-atlantic-for-2-7b/
- ViewPoint Analysis, core insurance software buyer guide (Guidewire/Duck Creek) — https://www.viewpointanalysis.com/post/insurance-software-options-2026

## 3. Market Landscape


Framing for the reader: the global insurance market was roughly **$5.5 trillion in premium in 2024 — ~$3.1tn life and ~$2.4tn P&C/non-life** (Swiss Re Institute sigma, 2024/2025 — https://www.swissre.com/institute/research/sigma-research/sigma-2024-03-world-insurance-global-resilience.html). **[Fact]** But premium volume is a poor map of *profit*. Profit accrues unevenly along a value chain that runs: **capital providers → reinsurers → primary carriers → MGAs/underwriting agencies → brokers/agents → policyholders**, with data/model/software vendors and rating agencies sitting across the middle. This file maps who holds each link and where the economics actually settle.

---

### 1. The value chain, stage by stage

**(a) Capital providers.** Ultimate risk-bearers: insurer shareholders, reinsurers' shareholders, ILS investors (pension funds, hedge funds via cat bonds — $49.5bn outstanding in 2024), and Lloyd's "Names"/corporate capital. **[Fact]** Increasingly, **private-equity permanent capital**: Apollo (via Athene) and KKR (via Global Atlantic, AUM ~$158bn) use insurance balance sheets as a source of long-duration, low-cost funding for their credit platforms (AI-CIO, 2024 — https://www.ai-cio.com/news/kkr-announces-acquisition-of-remaining-37-of-global-atlantic-for-2-7b/). **[Fact]**

**(b) Reinsurers.** Wholesale risk-warehousers. Highly concentrated: **Swiss Re (~$43.1bn 2024 gross reinsurance premium) overtook Munich Re (~$42.8bn); Hannover Re ~$37.7bn; Berkshire Hathaway Reinsurance ~$26.9bn** lead the segment; all non-life/composite reinsurers wrote ~$293bn of non-life premium in 2024 (S&P Global / AM Best, 2024 — https://www.reinsurancene.ws/swiss-re-overtakes-munich-re-as-top-reinsurer-by-2024-gpw-sp/). **[Fact]** Analyst estimates put Munich Re ~14% and Swiss Re ~11% of global reinsurance premium. **[Estimate]**

**(c) Primary carriers.** Retail risk-takers facing policyholders. Fragmented by line and geography: State Farm, Berkshire (GEICO), Progressive, Allstate, Travelers, Chubb, Liberty Mutual in US P&C; Allianz, AXA, Zurich, Generali in Europe; Ping An, China Life in Asia; MetLife, Prudential, New York Life, and the PE-owned Athene/Global Atlantic in US life/annuity.

**(d) MGAs / underwriting agencies (the fastest-growing link).** These underwrite on *others'* capital for a fee and commission, holding no balance-sheet risk. **[Inference]** They capture the underwriting-selection economics without the capital charge — an asset-light, high-return model that is attracting capital and talent away from traditional carriers.

**(e) Brokers/agents.** Distribution. Commercial brokerage is an oligopoly at the top: **Marsh McLennan (~$25.33bn 2024 brokerage revenue incl. McGriff), Aon #2, then Gallagher and WTW** (Business Insurance, 2024 — https://www.businessinsurance.com/top-insurance-brokers-no-1-marsh-mclennan-cos-inc-3/). **[Fact]** Personal-lines distribution splits between captive agents, independent agents, and direct.

**(f) Cross-cutting infrastructure.** Cat-model vendors (Verisk, Moody's RMS), core-software vendors (Guidewire, Duck Creek), rating agencies (AM Best, S&P, Moody's, Fitch), and bureaus (ISO, NCCI).

---

### 2. Where profit accrues vs. where it is competed away

**[Inference], triangulated from the sourced figures above:**

- **Brokerage is the most consistently profitable link.** Marsh McLennan and Aon earn high-margin, capital-light fee income and have compounded for years regardless of the underwriting cycle. They bear no claims risk; they monetize the *information and access asymmetry* between buyers and carriers. This is where the most durable, cycle-independent profit sits.
- **MGAs capture rising economics** for the same reason — fee-for-underwriting without capital at risk — which is why brokers, PE, and carriers are all building or buying MGA platforms.
- **Reinsurance is highly profitable at the top of the cycle** (2023–24 hard market) and painful at the bottom; its returns are real but cyclical and concentrated in a handful of balance sheets that can hold peak-peril capital.
- **Primary underwriting is where profit is most competed away** — commoditized personal lines especially. The exceptions are scale-and-data players (Progressive, GEICO in auto; Chubb in specialty commercial) whose underwriting edge is defensible.
- **Investment spread (float) is a quiet but massive profit pool**, now increasingly captured by PE-owned life insurers that out-yield traditional carriers on the asset side.

**The through-line:** economic value accrues to (1) proprietary risk *information/selection*, (2) *distribution control*, and (3) *asset-side yield origination* — and is competed away from undifferentiated balance-sheet capacity. **[Inference]**

---

### 3. Moats — who has them and why

- **Progressive / GEICO (personal auto):** scale + proprietary telematics/pricing data → structurally lower loss and expense ratios; Progressive ran sub-90 combined ratios through 2024 (10-Qs). A data-and-scale flywheel competitors can't cheaply copy. **[Fact + Inference]**
- **Chubb, W.R. Berkley (specialty commercial):** underwriting discipline, niche expertise, and reserve conservatism — a talent-and-culture moat.
- **Munich Re / Swiss Re (reinsurance):** balance-sheet scale, diversification, and proprietary risk models; only a few players can absorb a mega-cat. **[Fact — scale]**
- **Marsh McLennan / Aon (brokerage):** network effects, global servicing capability, and data (they see the whole market's pricing) — a two-sided-market moat.
- **Berkshire Hathaway:** unmatched capital plus a genuine willingness to shrink when prices are inadequate — the ability to *not* write business is itself a moat. **[Inference]**
- **Apollo/Athene, KKR/Global Atlantic:** an *asset-side* moat — origination of proprietary private credit at spreads traditional insurers can't match, funded by permanent annuity liabilities. **[Fact — model]**

---

### 4. Geography & regional clusters

- **United States (~40%+ of global premium) [Estimate]:** the largest and most profitable single market; state-regulated (50 DOIs + NAIC coordination). US P&C posted a $22.9bn underwriting gain and $169.3bn net income in 2024 (NAIC — https://content.naic.org/sites/default/files/2024-annual-property-casualty-and-title-insurance-industries-analysis-report.pdf). **[Fact]**
- **Bermuda:** the reinsurance and ILS hub — light-touch-but-credible solvency (BMA), no corporate income tax historically, and proximity to capital markets made it the domicile of choice for start-up reinsurers and cat-bond SPVs. **[Inference]** A genuine cluster built on regulatory arbitrage plus concentration of underwriting talent.
- **London / Lloyd's:** the specialty and complex-risk marketplace — a subscription market where syndicates share large/unusual risks. **2024 GWP £55.5bn, combined ratio 86.9%** (Lloyd's FY2024 — https://www.lloyds.com/insights/media-centre/press-releases/lloyds-reports-2024-full-year-results). **[Fact]** Its moat is the physical/relational concentration of specialty expertise (marine, aviation, energy, political risk).
- **Continental Europe:** Solvency II regime; dominated by Allianz, AXA, Zurich, Generali; strong life/savings orientation.
- **Asia (growth engine):** China (Ping An, China Life), Japan, India — the largest source of future premium growth as insurance penetration rises with incomes. Swiss Re projects emerging Asia to outgrow developed markets. **[Estimate]**

---

### 5. Trade flows, subsidies, national security

- **Reinsurance is the industry's "trade."** Risk is exported from cat-exposed primary markets (US, Japan, Caribbean) to global reinsurance capital (Bermuda, Europe, ILS funds). A US hurricane loss is partly paid by German, Swiss, and Bermudian balance sheets and pension-fund cat-bond holders. **[Inference]** This cross-border risk transfer is why reinsurer solvency is a systemic concern.
- **Government as insurer of last resort / subsidy:** the US National Flood Insurance Program, state FAIR plans (California FAIR Plan residential exposure ~$458bn by Sept 2024 — https://www.insurancejournal.com/news/west/2024/03/20/765883.htm), TRIA (terrorism backstop), and crop insurance (USDA-subsidized). **[Fact]** These exist precisely where private capital withdraws — a signpost of uninsurable-at-regulated-price risk.
- **National-security / systemic angle:** insurers are among the largest holders of government and corporate bonds, so their asset allocation matters to financial stability; the migration of life liabilities into PE-managed illiquid credit (Level 3 assets ~18% of the industry's ~$3.8tn fixed-income holdings by one account) is a live regulatory concern (CEPR, 2025 — https://cepr.net/publications/you-bet-your-life-insurance-private-equity-comes-for-your-annuity/). **[Estimate — attribute to CEPR]**

---

### 6. What is gaining vs. losing relevance

**Gaining:**
- **Capital-light models (brokers, MGAs).** Value migrating from balance-sheet risk-taking to fee-based distribution and underwriting-as-a-service. **[Inference]**
- **PE-owned spread-based life/annuity.** Reshaping the life sector around asset-origination edge; growing AUM rapidly (Global Atlantic $72bn→$158bn). **[Fact]**
- **Alternative capital / ILS.** Record 2024 cat-bond issuance shows capital markets structurally displacing some traditional reinsurance for peak perils. **[Fact]**
- **Data/telematics/AI underwriting and claims automation.** Real efficiency gains in the expense ratio and in segmentation. **[Inference]**
- **Emerging-market premium growth.** Asia the durable volume driver. **[Estimate]**

**Losing / under pressure:**
- **Undifferentiated primary underwriting** without a data or scale edge — squeezed between brokers above and cat/inflation risk below.
- **Rate-suppressed personal-property lines in cat-exposed states** — economically stranded until regulation lets price meet risk (California). **[Fact — case]**
- **Capital-heavy monoline cat reinsurance without diversification** — vulnerable when ILS undercuts pricing. **[Inference]**

**Disruption / obsolescence risks:**
- **Climate change** structurally raising cat frequency/severity faster than models and rates adjust — the existential input-cost problem for property lines. **[Inference]**
- **AI** could commoditize underwriting/claims (compressing the primary carrier's role) *or* entrench incumbents with the most proprietary data — direction unresolved. **[Inference]**
- **Autonomous vehicles** could shrink the personal-auto premium pool (the largest US P&C line) over the long run, shifting liability toward product/manufacturer coverage. **[Inference]**

---

### 7. Signal vs. promotion

- **Real progress:** telematics-driven segmentation (measurable loss-ratio edge), ILS as genuine new capacity, PE asset-origination spreads (real, if risk-laden). **[Inference]**
- **Overpromised:** many pure-play insurtechs (Lemonade, Root, Hippo) promised software-like margins but ran high combined ratios and de-rated once markets demanded a credible path to underwriting profit — the loss ratio is stubborn and cannot be "software-ed" away. **[Inference]** The lasting insurtech value has accrued to *enablers* (Guidewire, data vendors) rather than to full-stack disruptors, and to incumbents who adopted the tools.
- **Where value migrates next [Inference]:** toward whoever controls proprietary risk data, toward capital-light distribution/MGA fee streams, and toward asset-origination platforms behind long-duration liabilities — and *away* from generic balance-sheet capacity, which the ILS market is steadily commoditizing.

---

### 9. Complete output, customer, geography, funding, and policy map

Outputs are indemnity, income protection, healthcare access/funding, savings/annuity guarantees, risk engineering, claims handling and balance-sheet certainty. Claims payments flow into construction, auto repair, healthcare, legal and household markets. Coverage gaps, exclusions, underinsurance, delayed claims and correlated failure are negative system outputs.

Policyholder, insured, beneficiary, sponsor and payer may differ: an employer selects health/life cover, a homeowner's lender requires property insurance, a broker advises, a government subsidizes, and a reinsurer ultimately bears part of loss. Retail, commercial, specialty, group benefits and reinsurance therefore need separate demand maps.

Risk is local—weather, law, healthcare cost, driving, mortality and court systems—while reinsurance and investment capital are global. Primary carriers, mutuals, state insurers, brokers, MGAs, reinsurers, captives, health plans, pension/annuity firms and ILS funds capture different layers. Distribution may own the customer while carriers own regulated capital.

Private capital comes from premiums, equity/debt and reinsurance/ILS; public capital supports residual property markets, flood/crop/health programs, deposit/pension guarantees, disaster aid and terrorism or catastrophe backstops. Policy covers solvency and capital, rates/forms, market conduct, reserving, accounting, reinsurance credit, consumer privacy/discrimination, healthcare benefits, compulsory cover, tort, building codes and climate disclosure. State/provincial and national regimes can produce different prices for the same peril.

Insurance connects climate/weather, real estate, autos, healthcare, rates, credit and capital markets. Higher repair or medical inflation raises claims; high rates lift reinvestment yield but can expose asset duration or lapse behavior; unavailable insurance impairs mortgages and development; public disaster aid can crowd out coverage; prevention and resilient construction can reduce loss while creating new service markets.

### Sources
- Swiss Re Institute, sigma world insurance 2024/2025 (market size) — https://www.swissre.com/institute/research/sigma-research/sigma-2024-03-world-insurance-global-resilience.html
- Reinsurance News / S&P Global, "Swiss Re overtakes Munich Re as top reinsurer by 2024 GPW" — https://www.reinsurancene.ws/swiss-re-overtakes-munich-re-as-top-reinsurer-by-2024-gpw-sp/
- Business Insurance, Top insurance brokers No.1 Marsh & McLennan (2024 revenue) — https://www.businessinsurance.com/top-insurance-brokers-no-1-marsh-mclennan-cos-inc-3/
- NAIC, 2024 Annual P&C Industries Analysis Report — https://content.naic.org/sites/default/files/2024-annual-property-casualty-and-title-insurance-industries-analysis-report.pdf
- Lloyd's of London, Full Year 2024 results — https://www.lloyds.com/insights/media-centre/press-releases/lloyds-reports-2024-full-year-results
- AI-CIO, KKR / Global Atlantic acquisition (AUM) — https://www.ai-cio.com/news/kkr-announces-acquisition-of-remaining-37-of-global-atlantic-for-2-7b/
- Insurance Journal, California FAIR Plan / State Farm nonrenewals (2024) — https://www.insurancejournal.com/news/west/2024/03/20/765883.htm
- Reinsurance News, record 2024 cat-bond issuance / ILS outstanding — https://www.reinsurancene.ws/cat-bond-issuance-hits-record-17-7bn-in-2024-report/
- CEPR, "Private Equity Comes For Your Annuity" (Level 3 assets, PE-owned life) — https://cepr.net/publications/you-bet-your-life-insurance-private-equity-comes-for-your-annuity/

## 4. Operating Mechanics


The reader should internalize one identity above all: **an insurer's profit = underwriting result + investment result.** Underwriting result = premium earned − losses incurred − expenses. Investment result = yield on float and capital. Every metric, method, and valuation technique below is a way of measuring, optimizing, or pricing one of those two engines.

---

### 1. The core workflow (P&C, short-tail example)

1. **Product & rate filing.** Actuaries build a rating plan (base rate × rating factors) and, in regulated lines, file it with the state DOI. Loss-cost inputs often come from bureaus (ISO/Verisk, NCCI).
2. **Distribution & submission.** Risk arrives via agent, broker, or direct channel. Underwriters accept/decline/price it (risk selection).
3. **Underwriting & binding.** The insurer commits capital; premium is booked as *written*, then *earned* over the policy term (unearned premium is a liability until earned).
4. **Reinsurance cession.** The carrier cedes tail risk — quota-share (proportional) or excess-of-loss (non-proportional, above an *attachment point* up to a *limit*). This buys back capacity and smooths volatility.
5. **Claims.** On a covered loss, the insurer pays and books **case reserves** (known claims) plus **IBNR** (incurred but not reported). Reserving accuracy is the single biggest judgment call in the business.
6. **Investing the float.** Between premium receipt and claim payment, assets are invested (see valuation §6).
7. **Reserve development.** Over subsequent years reserves are re-estimated; releasing redundant reserves flatters earnings, strengthening deficient ones hits them.

**Long-tail lines (casualty, workers' comp, D&O)** run the same loop but claims settle over 5–20 years, so reserving risk and investment leverage are far higher, and pricing errors surface years late. **[Inference]** This time structure is why casualty is a "trust me" business and property is a "show me" business.

**Life/annuity workflow** differs: underwriting is mortality/longevity selection at issue; the "claim" is death, surrender, or annuity payout decades out; the profit engine is the **investment spread** between asset yield and credited rate, minus expenses and mortality cost.

---

### 2. Competing methods & technologies — and why players choose differently

**Distribution model:**
- *Independent agent/broker* (Travelers, Chubb, most commercial): broad reach, low fixed cost, but pays ~10–15% commission and cedes customer ownership.
- *Captive agent* (State Farm, Allstate historically): brand control, higher loyalty, high fixed cost.
- *Direct* (GEICO, Progressive Direct, Lemonade): compresses the commission out of the expense ratio and owns the data, but requires huge advertising spend to acquire customers. **[Inference]** Direct wins in high-frequency, commoditized personal auto where scale amortizes ad spend; the agent model persists in complex commercial risk where advice is the product.

**Pricing technology:**
- *Bureau/traditional GLM rating* vs *telematics/behavioral* vs *machine-learning models*. Telematics (Progressive Snapshot) improves the *segmentation* of a risk pool — the insurer keeps the profitable drivers competitors mis-price and sheds the bad ones (adverse selection working in your favor). This is a self-reinforcing data moat. **[Fact — mechanism]**

**Risk-capital sourcing (reinsurance vs. ILS):**
- *Traditional reinsurance* offers reinstatement, relationship continuity, and flexibility. *Cat bonds/ILS* offer fully collateralized, multi-year, fixed-price cover with no counterparty credit risk but less flexibility. **[Inference]** A cedent chooses ILS for peak, well-modeled perils (Florida wind, California quake) where capital-market appetite is deep, and traditional reinsurance for bespoke or casualty risk that markets can't easily model.

---

### 3. Asset types & their economics

- **Underwriting liabilities (reserves + unearned premium)** are the "product inventory." They are estimates, not facts — the core epistemic risk.
- **Float** is the economic asset: policyholder money the insurer invests for its own account until claims come due. Negative-cost float (underwriting profit + investable balance) is the holy grail — Berkshire's model. **[Fact]**
- **Investment portfolio:** P&C = mostly high-grade, shorter-duration bonds (to match short-tail claims and stay liquid for cats); life = long-duration bonds, structured credit, and increasingly private credit under PE ownership.
- **Deferred acquisition costs (DAC)** for life insurers: upfront commissions capitalized and amortized over the policy life — a key accounting lever.

---

### 4. How capacity is measured

Capacity is not tons or units; it is **risk appetite bounded by capital**. Practitioners measure it as:
- **Premium-to-surplus ratio** (how much premium the surplus supports).
- **PML / probable maximum loss** and **1-in-100 / 1-in-250 year cat loss** (from cat models) against available capital — this caps how much cat-exposed business a carrier can write.
- **Reinsurance program limits** (how high the tower goes, attachment points, reinstatements).

---

### 5. Unit economics — the cost stack and the KPIs

The universal P&C scorecard is the **combined ratio (CR) = loss ratio + expense ratio.** CR < 100% = underwriting profit; > 100% = underwriting loss (potentially offset by investment income).

- US P&C swung to a **statutory combined ratio of ~96.6% in 2024 (from 101.8% in 2023)** and a **$22.9bn underwriting gain, the first since 2020** (AM Best / S&P / NAIC, 2024 — https://insurancenewsnet.com/oarticle/bests-special-report-us-property-casualty-industry-swings-to-underwriting-profit-of-22-9-billion-in-2024-marks-first-gain-in-four-years). **[Fact]**
- The **loss ratio** (losses + LAE ÷ earned premium) is the dominant driver — the 2024 improvement came mostly from loss-ratio improvement (S&P Global, 2024 — https://www.spglobal.com/market-intelligence/en/news-insights/research/2024-us-pc-statutory-underwriting-results-from-famine-to-feast). **[Fact]**
- The **expense ratio** (acquisition + underwriting expenses ÷ premium) is where direct writers beat agency writers. Progressive's sub-90 combined ratios in 2024 show the model's edge (Progressive 10-Qs). **[Fact]**

**The marginal unit.** The marginal cost of one more policy is the *expected loss* on it (its actuarially-fair claims cost) + acquisition cost + servicing. There is no meaningful physical marginal cost — the constraint is capital and the risk that the expected loss estimate is wrong. **[Inference]** Gross margin structure is therefore entirely about *pricing accuracy vs. realized losses* plus the *spread earned on float*, not manufacturing efficiency.

**KPIs practitioners actually track:**
- Combined ratio; loss ratio; expense ratio; **accident-year vs. calendar-year** loss ratio (to separate current pricing from reserve development).
- **Prior-year reserve development** (favorable/adverse).
- **Net investment income** and **new-money yield**.
- **Retention/renewal ratio** and **rate change** (price achieved on renewals).
- **Return on equity (ROE)** and, for life, **return on embedded value**.
- **Policies-in-force (PIF)** growth and **customer acquisition cost**.

**Development/lead timelines:** a new rating plan takes months to file/approve; a new core system takes years; a mispriced casualty book can take a decade to reveal itself through adverse development. **[Inference]**

**Characteristic failure points:** (1) under-reserving that masks losses until a "reserve charge" wipes years of earnings; (2) catastrophe aggregation the models missed; (3) pricing that lags loss-cost inflation (California homeowners); (4) asset-liability mismatch / a run on surrenderable life liabilities; (5) reinsurance credit failure or exhausted reinstatements.

---

### 6. Valuation across life-stages

Because insurers earn on both underwriting and investing, and because their liabilities are estimates, **book value and its rate of compounding — not earnings multiples — anchor most insurance valuation.**

#### (a) Mature, cash-generative carriers (P&C, diversified)
- **Primary metric: Price-to-Book (P/B), conditioned on ROE.** The core relationship: a carrier that sustainably earns ROE above its cost of equity trades above book; one below trades below. Regressing P/B on ROAE materially improves valuation accuracy (Nissim, Columbia — http://www.columbia.edu/~dn75/Doron%20Nissim%20-%20Relative%20Valuation%20of%20U.S.%20Insurance%20Companies%20published%20version.pdf). **[Fact — method]**
- **Benchmarks:** average US insurer P/B ~1.2–1.6x and ROE ~13–15% — but this is **2021 data and now stale; treat as order-of-magnitude only** (Raincatcher/microcap valuation notes — https://raincatcher.com/insurance-company-valuation/). **[Estimate, dated]**
- Best-in-class underwriters (Chubb, Progressive) command premium multiples; the market pays up for durable sub-100 combined ratios and reserve conservatism. **[Inference]**
- Secondary: P/E on normalized earnings, and **tangible book value per share (TBVPS) growth + dividends** as a total-return proxy — the metric Berkshire itself emphasizes.

#### (b) Cyclical / balance-sheet-heavy carriers (reinsurers, cat-exposed, specialty) across the cycle
- Value on **mid-cycle normalized ROE**, not peak or trough earnings. In a hard market (2023–24) combined ratios and ROEs look spectacular; capitalizing them is a trap. **[Inference]**
- Watch **rate-on-line trends** and **reinsurance capital levels** as cycle indicators; apply a lower multiple to book when the cycle is peaking and capital is flooding in.
- Reinsurers/Lloyd's vehicles are often valued at or modestly above book because earnings are volatile and cat-exposed. Lloyd's 2024: **combined ratio 86.9%, £55.5bn GWP, £9.6bn pre-tax profit** — a peak-of-cycle print that a valuer should *normalize down* (Lloyd's FY2024 — https://www.lloyds.com/insights/media-centre/press-releases/lloyds-reports-2024-full-year-results). **[Fact]**

#### (c) Life insurers — Embedded Value; and early-stage / "IP-and-capacity" cases
- **Embedded Value (EV)** is the dominant life-insurer method: EV = adjusted net asset value + present value of in-force business (the discounted future profits already locked into existing policies), with explicit cost-of-capital and risk margins. Variants: European EV (EEV), Market-Consistent EV (MCEV). Life insurers are often valued on **Price / EV per share** and on **value of new business (VNB)** to price growth (Stout; Profectus — https://www.stout.com/en/insights/article/unique-aspects-of-valuing-life-insurance-companies). **[Fact — method]**
- Why EV, not P/E: a life policy's profit emerges over decades; GAAP/statutory earnings understate the economic value being created at issue. EV captures the long-duration spread the P/B lens misses. **[Inference]**
- **Early-stage / pre-scale analogues.** Insurance has few "pre-revenue" firms, but the equivalents are: (i) **insurtech start-ups** (Lemonade, Root) valued on growth, loss-ratio trajectory, and unit-economics *path to* an underwriting profit rather than current earnings — many de-rated hard once markets demanded a credible route to sub-100 combined ratios; (ii) **Bermuda/PE start-up reinsurers** valued on committed capital × achievable ROE × a book multiple; (iii) **new Lloyd's syndicates / MGAs** valued on the fee stream and the underwriting franchise being built. **[Inference]** For an MGA (managing general agent, which underwrites on others' capital for a fee), the value is a *fee/EBITDA multiple*, not a book multiple — closer to asset-light software than to a balance-sheet insurer. This distinction is where a lot of value is migrating (see LANDSCAPE).

**Discount rates & risk:** insurance valuations lean on cost-of-equity discounting (CAPM-style) with heavy scrutiny of **reserve adequacy** (an under-reserved book has overstated book value) and **asset quality** (a life insurer stuffed with Level 3 private credit has book value that may not be liquid or accurately marked — a live concern at PE-owned annuity writers). **[Inference]**

---

### 7. Testing, qualification & approval

- **Rate/form approval** by state DOIs (US) or conduct regulators (UK FCA, etc.).
- **Solvency qualification:** RBC ratio (US), Solvency II SCR coverage (EU), BSCR (Bermuda) — falling below thresholds triggers regulatory action.
- **Rating-agency review** (AM Best, S&P, Moody's, Fitch). A financial-strength rating is a *license to trade* in reinsurance and commercial lines; a downgrade can be existential because counterparties won't cede to a weak balance sheet. **[Inference]**
- **Actuarial opinion / reserve certification** signed annually.

---

### 10. Complete policy-to-claim and capital mechanics

The chain is product/rate design → distribution and application → underwriting → bind and collect premium → cede/reinsure and invest float → monitor exposure → receive, investigate and settle claim → recover from reinsurer/salvage/subrogation → renew, reprice or exit. Premium written, earned and collected occur on different schedules; incurred losses include paid claims plus reserve changes.

Analyze underwriting at accident/underwriting year and calendar year. Current-year loss ratio, prior-year development, catastrophe loss, expense ratio and commission should be separated. Life/annuity economics require mortality/morbidity/longevity, lapse, spread, option/guarantee and hedge analysis rather than a P&C combined ratio. Health requires medical-cost and risk-adjustment mechanics.

Cash includes unearned premium, loss and benefit reserves, reinsurance recoverables/payables, collateral, agent balances and investment assets. Reserve releases create earnings without new cash; adverse development consumes capital. Asset-liability duration, liquidity and credit quality determine whether float is a source of strength. Reinsurance attachment, limit, reinstatement, exclusions and counterparty collectability matter more than ceded percentage.

Track rate versus exposure and loss trend, retention/new business, premium and policies, combined/benefit ratio, reserve development, claim frequency/severity, catastrophe load, reinsurance cost, investment yield/spread, lapse, RBC/solvency ratio, rating, book value and ROE. Stress catastrophe clusters, social/medical inflation, repair shortages, cyber aggregation, pandemic, rate fall/rise, credit loss, lapse shock, reinsurer failure and regulatory price constraints.

### Sources
- AM Best via InsuranceNewsNet, "US P/C Industry Swings to $22.9B Underwriting Profit in 2024" — https://insurancenewsnet.com/oarticle/bests-special-report-us-property-casualty-industry-swings-to-underwriting-profit-of-22-9-billion-in-2024-marks-first-gain-in-four-years
- S&P Global Market Intelligence, "2024 US P&C statutory underwriting results: from famine to feast" — https://www.spglobal.com/market-intelligence/en/news-insights/research/2024-us-pc-statutory-underwriting-results-from-famine-to-feast
- NAIC, 2024 Annual P&C Industries Analysis Report — https://content.naic.org/sites/default/files/2024-annual-property-casualty-and-title-insurance-industries-analysis-report.pdf
- Progressive Corp Form 10-Q, 2024 — https://www.sec.gov/Archives/edgar/data/80661/000008066124000018/pgr-20240331.htm
- Lloyd's of London, Full Year 2024 results — https://www.lloyds.com/insights/media-centre/press-releases/lloyds-reports-2024-full-year-results
- Doron Nissim (Columbia), "Relative Valuation of U.S. Insurance Companies" — http://www.columbia.edu/~dn75/Doron%20Nissim%20-%20Relative%20Valuation%20of%20U.S.%20Insurance%20Companies%20published%20version.pdf
- Stout, "Unique Aspects of Valuing Life Insurance Companies" — https://www.stout.com/en/insights/article/unique-aspects-of-valuing-life-insurance-companies
- Raincatcher, "How to Value an Insurance Company" (P/B, ROE benchmarks — 2021 data) — https://raincatcher.com/insurance-company-valuation/
- Berkshire Hathaway 2024 Annual Report (float mechanics) — https://www.berkshirehathaway.com/2024ar/2024ar.pdf

## 5. Economics and Valuation


Benchmark bands are diagnostic starting points; refresh for product, asset, geography, contract, and cycle.

### Core unit-economic identity

P&C profit = earned premium − incurred losses − underwriting expense + investment income. Life/annuity adds spread, mortality/longevity, lapse and hedge results; health adds premium/risk adjustment less medical cost and administration.

### Ten benchmark measures

| Measure | Diagnostic band or unit | Decision use |
| --- | --- | --- |
| Combined ratio | below 100% indicates underwriting profit before investment | P&C core result |
| Loss ratio | claims/earned premium by accident year | Pricing adequacy |
| Expense ratio | underwriting expense/earned premium | Distribution and scale |
| Rate versus loss trend | percentage-point gap | Future margin |
| Reserve development | favorable/adverse as percent of beginning reserves | Prior-year quality |
| Retention | policy/premium percent | Franchise and repricing |
| Reinsurance spend | ceded premium and limit/attachment | Capital and tail protection |
| Solvency/RBC | regime-specific percent or multiple | Regulatory buffer |
| Investment yield/spread | portfolio yield less credited/guaranteed rate | Float economics |
| Health medical-cost ratio | medical claims/premium, rule and mix specific | Health underwriting |

### Accounting-to-cash bridge

Premium written, earned and collected differ; claims paid, incurred and reserved differ. Reconcile prior-year development, catastrophe, reinsurance recoverables, acquisition cost, embedded derivatives, OCI, statutory versus GAAP/IFRS capital and holding-company liquidity.

### Highest-value sensitivities

- Claim frequency/severity, repair/medical/social inflation, catastrophes and wording.
- Rate approval, retention, distribution commissions and reinsurance pricing.
- Interest rates, credit losses, duration, lapses, guarantees and hedges.
- Capital/rating constraints, model change, litigation and public backstops.

### Valuation discipline

Use sum-of-parts: P&C underwriting/franchise and reserves, life spread/embedded value, health membership/margin, brokers' recurring fees, and excess capital. Book value quality depends on reserves and asset marks.


## 6. Regulation and Public Funding


Snapshot reviewed through **2026-07-14**. Verify enacted text, implementation dates, litigation, and current guidance.

### Permission chain

Policyholder pays; insured is exposed; beneficiary receives; broker/MGA distributes/underwrites; carrier issues and holds capital; reinsurer/ILS takes tail; claims/vendor network settles; regulator/rating agency constrains.

### Jurisdiction and regime map

| Jurisdiction or layer | Core regimes and authorities | Economic transmission |
| --- | --- | --- |
| United States | State insurance departments/NAIC solvency/rates; CMS and state health; federal securities/tax where applicable | Capital, rate/forms, reserves, conduct, benefits and distribution |
| European Union | Solvency II, national conduct and product rules, IFRS reporting | Risk capital, disclosure and investment |
| United Kingdom | PRA/FCA solvency and conduct | Capital, consumer duty and matching adjustment |
| Public/private risk pools | Flood, crop, health, terrorism, pension and catastrophe backstops | Risk sharing, pricing and contingent taxpayer exposure |

### Public and private funding

Private funding includes premium/float, equity/debt, reinsurance, retrocession, ILS/cat bonds and broker/MGA capital. Public funding includes social health, flood/crop/property pools, disaster aid, terrorism backstops and guarantee schemes.

### Enforcement and liability

Rate/form disapproval, restitution, market-conduct fines, capital remediation, receivership, bad-faith and class-action claims, reinsurance dispute and license loss are material.

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
| Asbestos and long-tail liability | Broad historic wording met decades-later claims | Reserve inadequacy emerged slowly | Wording and latency dominate long-tail risk |
| 2001 September 11 attacks | Correlated property, aviation, life and business interruption losses occurred | Coverage disputes and terrorism backstops followed | Aggregation crosses product silos |
| 2008 insurer investment stress | Credit and market losses hit capital and guarantees | Some business needed state support or restructuring | Asset risk can overwhelm underwriting |
| 2017 Atlantic hurricanes | Multiple events tested cat models and reinsurance | Loss creep developed through claims and demand surge | Event count and claims inflation matter |
| 2020–2023 pandemic/inflation repricing | Health, mortality, business interruption, auto and repair trends shifted | Rate and reserve response differed by line | Never aggregate insurance lines |

### Practitioner extraction

- **Leading signals:** Rate filings, renewal price/retention, loss trend, catastrophe activity, reinsurance renewals, yields/spreads, lapses and reserve development.
- **Evidence that breaks the easy thesis:** Growth below loss trend, reserve releases funding current earnings, or low cat loss from unusually benign weather treated as structural.
- **Durable lesson:** Insurance sells a legal promise whose true cost may not be known for years.


## 8. Data Sources and Monitoring Dashboard


Preserve observation period, unit, definition, geography, and revision vintage.

### Primary source map

| Source | Cadence | Best use | Caveat |
| --- | --- | --- | --- |
| [NAIC insurance data and model laws](https://content.naic.org/) | quarterly to annual | US statutory, capital and regulation | Detailed data may require access |
| [State insurance departments](https://content.naic.org/state-insurance-departments) | filing-driven | Rates, forms, conduct and solvency | State-specific |
| [CMS health insurance data](https://www.cms.gov/data-research) | monthly to annual | Enrollment, medical and program data | Program definitions |
| [FEMA catastrophe/flood data](https://www.fema.gov/openfema-data-page) | frequent | Disasters and flood insurance | Public-program scope |
| [SEC EDGAR filings](https://www.sec.gov/edgar/search/) | quarterly and annual | GAAP, reserves, reinsurance and investments | Line definitions vary |

### Indicator stack

- **Leading:** renewal rate/retention; exposure; reinsurance; catastrophe forecasts; medical/repair inflation.
- **Coincident:** premium; frequency/severity; loss ratio; claims; yield; lapse.
- **Lagging:** reserve development; litigation; solvency; recoveries; rate approval.

### Minimum dashboard

1. **Combined ratio** — below 100% indicates underwriting profit before investment; P&C core result.
2. **Loss ratio** — claims/earned premium by accident year; Pricing adequacy.
3. **Expense ratio** — underwriting expense/earned premium; Distribution and scale.
4. **Rate versus loss trend** — percentage-point gap; Future margin.
5. **Reserve development** — favorable/adverse as percent of beginning reserves; Prior-year quality.
6. **Retention** — policy/premium percent; Franchise and repricing.
7. **Reinsurance spend** — ceded premium and limit/attachment; Capital and tail protection.
8. **Solvency/RBC** — regime-specific percent or multiple; Regulatory buffer.
9. **Investment yield/spread** — portfolio yield less credited/guaranteed rate; Float economics.
10. **Health medical-cost ratio** — medical claims/premium, rule and mix specific; Health underwriting.

### Normalization rules

- Use accident year for underwriting trends.
- Separate gross/ceded/net.
- Segment by line and geography.
- Align statutory and accounting bases.

### Evidence traps

- Using premium growth as profit growth.
- Treating reserve release as recurring.
- Combining life, health and P&C ratios.

## 9. Geographic Operating Models

Geography changes ownership, contracting, cost, funding, regulation and risk; compare like with like.

| Geography / archetype | Operating model | Economic and risk implications |
| --- | --- | --- |
| United States | State-regulated P&C/life markets with risk-based capital, admitted/nonadmitted channels and deep distribution | Tort, catastrophe, medical cost and state rate approval vary sharply |
| London/Bermuda | Global specialty and reinsurance hubs using brokered subscription markets and alternative capital | Cycle turns through catastrophe loss, retrocession and investor risk appetite |
| European Union/United Kingdom | Large composite/life insurers under market-consistent solvency regimes | Asset-liability duration and capital rules influence product design |
| Japan and mature Asia | Large life/savings books with aging populations and distribution partnerships | Guarantees, duration and currency hedging are central |
| Emerging markets | Low-penetration protection and savings products sold through agents, banks and digital channels | Inflation, collection, regulation and catastrophe data quality shape economics |

## 10. Cross-Industry Dependency Map

| Dependency class | Linked markets and institutions | Transmission into this industry |
| --- | --- | --- |
| Risk environment | Weather/climate, mortality, morbidity, courts, repair costs, cyber and economic activity | Frequency, severity and social inflation move loss ratios |
| Capital markets | Bonds, equities, mortgages, derivatives and reinsurance/insurance-linked securities | Investment income and asset marks interact with liabilities and capital |
| Distribution | Agents, brokers, banks, employers, digital platforms and affinity partners | Acquisition cost and renewal ownership determine lifetime value |
| Claims ecosystem | Hospitals, repair shops, lawyers, adjusters, third-party administrators and data | Provider inflation and settlement duration drive reserve uncertainty |
| Regulation/capital | Rate approval, solvency, accounting, guaranty funds, tax and conduct rules | Capital availability sets underwriting capacity after losses |

The practical test is to trace a shock through availability, delivered cost, working capital, output, customer economics, financing and eventual substitution—not merely name the adjacent market.

## 11. Decision-Grade Unit Economics

> The numerical example below is illustrative, not a current market forecast or universal benchmark. Replace every assumption with asset-, contract-, product- and geography-specific evidence.

**Representative unit:** A $100m earned-premium property-and-casualty book for one accident year.

**Core equation:** `Pre-tax insurance result = earned premium − incurred loss − loss-adjustment expense − acquisition/operating expense + investment income on float`

| Bridge item | Illustrative assumption and calculation | Result / interpretation |
| --- | --- | --- |
| Earned premium | Risk exposure recognized during the period | $100m |
| Losses | Expected ultimate claims at 62% loss ratio | $62m |
| Loss-adjustment expense | Claims handling, legal and adjusting at 8% | $8m |
| Acquisition and operating expense | Commission 12% + operations 10% | $22m |
| Underwriting result | $100m − $62m − $8m − $22m | $8m; 92% combined ratio |
| Investment income | $60m average float × 4% | $2.4m, yielding $10.4m pre-tax before reserve development/cat volatility |

**Decision test:** Price to prospective ultimate loss and required capital, not the latest calendar-year combined ratio; test inflation, catastrophe correlation and reserve tails.

## 12. Industry Balance and Marginal Economics

| Balance concept | Industry-specific definition | What to measure |
| --- | --- | --- |
| Marginal supply unit | Last insurer/reinsurer willing to deploy capital to a peril, layer and geography | Model confidence, diversification and retrocession set capacity |
| Marginal customer | Policyholder choosing retention, limit, deductible, mitigation or alternative risk transfer | Balance-sheet tolerance and lender/regulatory requirements set demand |
| Clearing mechanism | Brokered/agent-negotiated premium, terms, attachment, exclusions and limits | Rate-on-line without terms is incomplete |
| Cash shutdown point | Renewal capacity exits when premium fails to cover prospective loss, expense and capital charge | Existing claims remain payable long after underwriting stops |
| New-capacity incentive | Expected underwriting + investment return exceeds cost of capital after tail/correlation risk | Large losses and high rates attract traditional and alternative capital |
| Adjustment lag | Annual renewals for price, years/decades for casualty and life claims | Calendar results mix multiple underwriting vintages |

## 13. Terminology and Comparability Traps

| Reported term | Common but invalid interpretation | Required normalization |
| --- | --- | --- |
| Combined ratio | Total profitability | Add investment income, capital cost, reserve development and catastrophe normalization |
| Premium growth | Exposure growth or price | Separate rate, insured value, payroll/sales exposure, mix, reinstatement and acquisitions |
| Reserves | Known cash liability | Analyze accident year, paid/incurred, discount, inflation, tail and adverse-development history |
| Float | Free permanent funding | Match duration, liquidity, loss volatility and policyholder obligation |
| ROE | Underwriting quality | Separate leverage, reserve releases, asset returns, tax and catastrophe cycle |


