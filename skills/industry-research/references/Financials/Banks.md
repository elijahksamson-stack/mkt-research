# Banks

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

Chartered depository institutions and bank holding companies engaged in deposits, payments, lending, securities, wealth and related balance-sheet intermediation.

### Operating taxonomy

| Segment | What is sold | Primary unit | Do not aggregate without |
| --- | --- | --- | --- |
| Consumer and deposit banking | Transactions, savings, cards and consumer loans | accounts, deposits, loans, customers | Insured/uninsured, operational, rate, credit and channel |
| Commercial and SME banking | Deposits, working capital, term loans and treasury | loans, commitments, deposits | Borrower cash flow, collateral, relationship and concentration |
| Mortgage and real-estate banking | Origination, portfolio, sale and servicing | balances, originations, MSR | Lien, LTV, fixed/ARM, owner type, geography and guarantee |
| Corporate/wholesale banking | Syndicated credit, markets, trade and transaction services | exposure, fees, payment volumes | Counterparty, maturity, collateral and capital |
| Custody, wealth and specialized banks | Safekeeping, trust, private banking and niche lending | AUC/A, assets, deposits | Client asset versus balance-sheet asset and operational risk |

### Specifications that change value

- State average/end balance, fixed/floating, maturity/repricing, risk grade, geography, collateral, guarantee and accrual status.
- Deposits require insured status, customer type, operational behavior, rate, concentration and channel.
- Capital needs CET1, tangible common equity, risk-weighted and leverage denominators.
- Liquidity needs cash, securities, encumbrance, collateral value, contingent draw and run assumptions.
- Credit must separate delinquency, nonaccrual, criticized, charge-off, allowance and lifetime expected loss.

### Role map

Depositor supplies funding and payment relationship; bank underwrites and transforms; borrower uses credit; payment/custody rails settle; guarantor/insurer may absorb loss; central bank and supervisor provide reserve/liquidity/rules; shareholders and debt absorb residual loss.

### Terms that must be explicit

- NIM versus net interest income
- deposit beta and mix
- CET1 versus tangible common equity
- allowance, provision and net charge-off
- liquidity value versus accounting value


## 2. Inputs and Dependencies


Scope: chartered depository institutions (commercial banks, thrifts/savings institutions) whose core business is maturity/liquidity transformation — taking deposits and short-term funding, and holding longer-dated loans and securities. The framing below treats a bank as a *financial manufacturer*: its "raw material" is money (funding), its "machine" is the balance sheet plus a risk-and-compliance apparatus, and its "output" is credit and payment services priced at a spread. The reader should track where pricing power sits at each input and which inputs actually cap capacity or set the margin.

### 1. Funding — the primary raw material

Banks do not "use" money the way a factory uses steel; funding *is* the input, and its cost is the dominant cost line. The U.S. industry funds ~$25.0 trillion of assets (total assets $24,989B in Q2 2025) [Fact] (FDIC Statistics at a Glance, 2025 — https://www.fdic.gov/quarterly-banking-profile/statistics-glance-industry-pdf-second-quarter-2025.pdf). Funding sources, cheapest to most expensive:

- **Core deposits** (checking, savings, small time deposits, operating balances). The strategic prize. Core deposits are ~78% of average earning assets [Fact] (Kansas City Fed community banking bulletin, 2025 — https://www.kansascityfed.org/banking/community-banking-bulletins/highlight-funding-profiles-benefit-from-core-deposit-growth/). Their power is that a chunk pays near-zero interest and is *sticky* — the classic zero-cost demand deposit is the closest thing in finance to a free input, which is why deposit franchises, not loan books, are the durable moat. Domestic deposits rose for a sixth consecutive quarter in Q4 2025 (+$318.3B, +1.8%) [Fact] (FDIC QBP Q4 2025 — https://www.fdic.gov/news/speeches/2026/fdic-quarterly-banking-profile-fourth-quarter-2025).
- **Wholesale funding** — FHLB advances, brokered deposits, repo, fed funds purchased. More expensive and more flight-prone, but flexible for growth. Wholesale funding was 14.9% of assets in 2024, its lowest since March 2023 but above the 10-year average of 11.5% [Fact] (First Business Bank / regulatory data, 2024 — https://firstbusiness.bank/resource-center/wholesale-funding-asset-liability-management/).
- **Equity capital** (see §5), the most expensive and regulatorily mandated slice.

**Pricing power / cost sensitivity.** The key variable is **deposit beta** — the fraction of a change in the policy rate that passes through to deposit costs. When the Federal Reserve raises rates, asset yields reprice fast but well-run retail franchises can hold deposit costs down (low beta), widening the net interest margin (NIM); the reverse happens for banks reliant on rate-sensitive or brokered money (high beta). Industry NIM was 3.34% in Q3 2025 and 3.39% in Q4 2025, above the pre-pandemic average of ~3.25% [Fact] (FDIC QBP Q3 2025 — https://www.fdic.gov/news/speeches/2025/fdic-quarterly-banking-profile-third-quarter-2025). Community banks run structurally wider NIMs (3.73% Q3 2025, same source) because they hold more relationship deposits and higher-yielding local loans. **[Inference]** A 100bp rise in funding cost not offset by asset repricing is roughly a 100bp NIM hit — on a 3.3% margin that is a third of the spread, so funding cost is *the* margin lever. This is the single most important sentence in this file.

**Bottleneck / single point of failure.** Deposit flight is the industry's characteristic kill mechanism. Silicon Valley Bank (2023) failed not from credit losses but from a run once uninsured depositors coordinated — funding is the input whose sudden withdrawal ends the firm in days. The industry still carries $337.1B of unrealized losses on securities (Q3 2025) [Fact] (FDIC QBP Q3 2025, above), the latent asset-side wound that a funding run converts into insolvency.

### 2. Credit demand and creditworthy borrowers (the "order book")

A bank cannot deploy funding profitably without loan demand and borrowers who repay. Loan growth ran +4.7% year-over-year in Q3 2025 [Fact] (FDIC QBP Q3 2025). Credit quality is an input in the sense that the *supply of good risk* caps profitable lending: the past-due-and-nonaccrual rate was 1.49% and net charge-offs 0.61% in Q3 2025 [Fact] (same). **[Inference]** In a downturn the binding constraint flips from funding to credit quality — provisions and charge-offs, not deposit costs, become the swing factor in earnings.

### 3. Risk-transfer and data inputs from outside industries

- **Credit bureaus and scores.** Underwriting depends on FICO scores and the three bureaus (Equifax, Experian, TransUnion) plus FICO Inc. as the score developer. These are near-monopoly external suppliers with strong pricing power over banks; a bank cannot practically originate consumer credit without them. [Inference] This is a genuine external dependency where the supplier, not the bank, holds pricing power.
- **Payment networks.** Card issuance depends on Visa and Mastercard rails (and Amex's closed loop). Networks set interchange economics and extract per-transaction fees; banks are simultaneously customers and beneficiaries (they earn interchange but pay network fees). [Fact/Inference] Regulation (the Durbin Amendment caps debit interchange for banks >$10B) shows the government, not the bank, ultimately controls this revenue-linked input.
- **Reinsurance / capital markets** for securitization and risk transfer — banks offload mortgage and credit risk to GSEs (Fannie Mae, Freddie Mac) and to structured markets, which recycles balance-sheet capacity.

### 4. Technology, software and IP

Banks are increasingly software companies with a charter. Key layers:

- **Core banking systems** — the system of record for accounts, deposits and transactions. The U.S. market is an oligopoly: the "Big Three" **FIS, Fiserv, and Jack Henry** dominate, with Temenos, Finastra, Oracle and Infosys serving broader or international clients [Fact] (Federal Reserve Bank of Kansas City, market structure of core providers — https://www.kansascityfed.org/research/payments-system-research-briefings/market-structure-of-core-banking-services-providers/). The global core banking software market was ~$17.5B in 2024 [Estimate] (Straits Research, 2024 — https://straitsresearch.com/report/core-banking-software-market). **[Inference]** Because switching cores is a multi-year, high-risk migration, core vendors hold strong pricing power over small and mid-size banks — a real margin drag and a strategic dependency, and a major reason community banks struggle to match megabank technology.
- **Digital channels, fraud, and analytics** — mobile apps, fraud engines, KYC/AML screening. Megabanks build in-house (JPMorgan spends well over $15B/year on technology [Estimate, from company disclosures]); smaller banks rent from the same core vendors, widening the scale gap.

### 5. Financial capital and regulation (the true capacity constraint)

This is where a bank differs most from a normal company: **regulatory capital, not physical plant, caps output.** A bank can only grow assets to the extent its capital ratios permit.

- **Basel III / risk-based capital.** Assets are risk-weighted; the bank must hold Common Equity Tier 1 (CET1) against risk-weighted assets. JPMorgan carried a 14.6% standardized CET1 ratio at end-2024 [Fact] (JPMorgan 2024 10-K — https://www.sec.gov/Archives/edgar/data/19617/000001961725000270/jpm-20241231.htm). The pending **Basel III "endgame"** re-proposal would raise or reshape these requirements — the original 2023 proposal implied ~16% higher aggregate CET1 for large holding companies; the 2025 re-proposal eases that, with comments due June 2026 [Fact] (Congress.gov CRS R47855, 2024 — https://www.congress.gov/crs-product/R47855; Moody's, 2025 — https://www.moodys.com/web/en/us/insights/regulatory-news/us-proposes-final-basel-rules-transition-period-to-start-in-july-2025.html). **[Inference]** Every increment of required capital lowers achievable return on equity for a given asset base — capital rules are literally the industry's capacity ceiling and margin governor, functioning like a factory's regulatory production quota.
- **Deposit insurance (FDIC).** Banks pay assessments into the Deposit Insurance Fund ($150.1B, reserve ratio 1.40%, Q3 2025) [Fact] (FDIC QBP Q3 2025). This is a mandatory input cost that also underwrites the deposit franchise's stickiness.
- **Compliance/regulatory labor.** BSA/AML, CRA, stress testing (CCAR/DFAST for large banks) require large control staffs — a rising, non-productive cost input.

### 6. Labor

Salaries and benefits are the largest slice of non-interest expense, typically **50–60% of total operating costs** [Estimate] (Stealth Agents / industry data, 2026 — https://stealthagents.com/research/banking-industry-staffing-costs-2026). The efficiency ratio (non-interest expense / net operating revenue) was 58.7% in Q1 2024 [Fact] (FDIC QBP, 2024 — https://www.fdic.gov/system/files/2024-08/2024-q1-qbp_0.pdf). Scarce, expensive talent concentrates in: quantitative risk/modeling, technology/engineering (competing with Big Tech pay), commercial relationship managers (revenue producers), and compliance. Average cost per employee rose from ~$91,800 to ~$104,500 across a 60-bank sample even as headcount fell [Estimate] (OCC "On Point," 2024 — https://occ.treas.gov/publications-and-resources/publications/economics/on-point/pub-on-point-banks-face-rising-labor-costs.pdf). **[Inference]** Automation is shrinking branch/teller headcount while raising per-head cost as the mix shifts to engineers and risk staff — a structural cost re-mix, not simple savings.

### 7. Physical infrastructure and energy

Branches, ATMs, and data centers. Branch networks are a legacy fixed cost being rationalized as deposits migrate to mobile. Data-center compute and (increasingly) cloud spend are the growing physical input; energy is a modest direct cost but matters via cloud/data-center intensity. These are secondary to funding and capital in determining economics. [Inference]

### 8. How a shock propagates (worked example)

A sharp Fed rate hike: (1) wholesale and rate-sensitive deposit costs jump immediately; (2) low-beta core-deposit banks widen NIM, high-beta/wholesale-funded banks compress; (3) fixed-rate securities and mortgages fall in value, inflating unrealized losses (the $337B latent loss above); (4) if depositors sense weakness, uninsured balances flee to money-market funds or stronger banks, forcing asset sales that crystallize the losses (the SVB sequence). A single input (short-rate funding cost) thus cascades through margin, asset value, and solvency. Conversely, a credit shock enters from §2 — rising charge-offs consume provisions and CET1, tightening the §5 capacity ceiling and choking new lending. **[Inference]** The two great input shocks — funding/rates and credit — hit through different channels but converge on capital.

### 9. Full financial, physical, and institutional input ledger

The funding stack includes insured and uninsured transaction/savings deposits, time deposits, brokered deposits, sweep balances, secured repo, central-bank or home-loan-bank advances, senior and subordinated debt, securitization, equity and retained earnings. Each source has a rate, duration, collateral need, behavioral stability, legal priority and resolution treatment. Capital is not interchangeable with liquidity: common equity absorbs loss, while cash and unencumbered securities meet outflows.

Credit production also requires borrower income/cash flow, collateral, guarantees, appraisals, credit bureaus, payment history, legal enforceability and servicing/collection capacity. Mortgage lending depends on real-estate supply, title, insurance and secondary agencies; commercial lending depends on customers' commodity, inventory, receivables and project markets. Loan demand and credit quality therefore import the input risks of every borrower industry.

The physical/digital substrate includes branches, ATMs, call centers, cash logistics, data centers/cloud, telecom, core processors, cards, identity/KYC, payment rails, clearing/custody, cybersecurity, fraud data, models and vendor continuity. Scarce labor includes relationship bankers, underwriters, risk/model specialists, compliance, security and workout teams. Charter, deposit insurance, central-bank access, licenses and trust are permission inputs.

Rates, deposit beta/mix, wholesale spread, credit cost and fees set margin; capital, liquidity, concentration limits, collateral, operational resilience, skilled underwriting and supervisory restrictions cap balance-sheet capacity. Fintech partnerships, private credit, securitization and government guarantees can substitute for holding loans, but move economics and risk rather than eliminate them.

### Sources
- FDIC, Quarterly Banking Profile Q3 2025 — https://www.fdic.gov/news/speeches/2025/fdic-quarterly-banking-profile-third-quarter-2025
- FDIC, Quarterly Banking Profile Q4 2025 — https://www.fdic.gov/news/speeches/2026/fdic-quarterly-banking-profile-fourth-quarter-2025
- FDIC, Statistics at a Glance Q2 2025 — https://www.fdic.gov/quarterly-banking-profile/statistics-glance-industry-pdf-second-quarter-2025.pdf
- FDIC, Q1 2024 QBP — https://www.fdic.gov/system/files/2024-08/2024-q1-qbp_0.pdf
- Kansas City Fed, core deposit funding profiles — https://www.kansascityfed.org/banking/community-banking-bulletins/highlight-funding-profiles-benefit-from-core-deposit-growth/
- Kansas City Fed, market structure of core banking providers — https://www.kansascityfed.org/research/payments-system-research-briefings/market-structure-of-core-banking-services-providers/
- First Business Bank, wholesale funding / ALM — https://firstbusiness.bank/resource-center/wholesale-funding-asset-liability-management/
- Straits Research, core banking software market — https://straitsresearch.com/report/core-banking-software-market
- JPMorgan Chase 2024 Form 10-K — https://www.sec.gov/Archives/edgar/data/19617/000001961725000270/jpm-20241231.htm
- Congressional Research Service R47855, Basel III Endgame — https://www.congress.gov/crs-product/R47855
- Moody's, US Basel rules finalized — https://www.moodys.com/web/en/us/insights/regulatory-news/us-proposes-final-basel-rules-transition-period-to-start-in-july-2025.html
- OCC, "Banks Face Rising Labor Costs" On Point — https://occ.treas.gov/publications-and-resources/publications/economics/on-point/pub-on-point-banks-face-rising-labor-costs.pdf
- Stealth Agents, banking staffing costs — https://stealthagents.com/research/banking-industry-staffing-costs-2026

## 3. Market Landscape


This file maps who does what across the banking value chain, where profits accrue versus get competed away, the geography of the industry, and where economic value is migrating. The reader should end able to reason about which positions win and lose as the industry evolves.

### 1. The value chain and who sits at each stage

Banking is not a linear supply chain; it is a stack of functions a single balance sheet performs. Decompose it into where money accrues:

1. **Funding / deposit gathering** — the profit engine. Whoever controls cheap, sticky deposits controls the industry's margin (see INPUTS §1). This is where megabanks and strong community franchises win.
2. **Underwriting / origination** — increasingly contestable. Non-banks and fintechs originate loans (mortgages, consumer, small-business) without deposits, then sell them. Origination fee income is being competed away; the durable value stays with whoever *funds and holds* the risk.
3. **Balance sheet / risk-warehousing** — where regulated banks retain an edge because deposit funding + FDIC backstop makes them the cheapest holders of credit risk. Basel capital rules both protect this moat (barriers to entry) and tax it (capital cost).
4. **Servicing and payments** — high-volume, fee-based, technology-intensive; ceded largely to processors (FIS, Fiserv, Jack Henry) and networks (Visa, Mastercard). Banks earn interchange but the rails' owners capture rich, capital-light margins. [Inference] This is the clearest example of value having *already migrated* out of banks to their suppliers.
5. **Distribution / customer interface** — the new battleground. Fintechs, neobanks and Big Tech own the app and the relationship; banks risk becoming invisible balance-sheet utilities behind someone else's brand (the "banking-as-a-service" dynamic).

**[Inference] Where profit accrues vs. competes away:** Deposit franchise value and balance-sheet risk-warehousing are the durable profit pools (protected by charter, insurance, and capital barriers). Origination, servicing, and customer interface are being commoditized and are migrating to specialists and platforms. The strategic question for any bank is whether it owns the deposit + balance-sheet layer or is being reduced to a rented one.

### 2. Participants by size tier (US)

- **Megabanks / G-SIBs**: JPMorgan Chase (~$4T assets, 5th largest globally), Bank of America (~$3.4T), Citigroup, Wells Fargo [Fact] (S&P Global, world's largest banks 2025 — https://www.spglobal.com/market-intelligence/en/news-insights/articles/2025/4/the-worlds-largest-banks-by-assets-2025-88424232). Universal models spanning consumer, commercial, cards, markets and wealth. Moats: scale, funding cost, technology budgets, product breadth, regulatory relationships.
- **Super-regionals**: PNC, U.S. Bancorp, Truist, Capital One (post-Discover), M&T. Compete on regional density and commercial banking.
- **Community banks**: thousands of institutions under ~$10B assets; wider NIMs (3.73% Q3 2025) from relationship deposits and local lending [Fact] (FDIC QBP Q3 2025 — https://www.fdic.gov/news/speeches/2025/fdic-quarterly-banking-profile-third-quarter-2025).
- **Total universe**: 4,379 FDIC-insured institutions in Q3 2025, down from 4,421 the prior quarter — a decades-long consolidation [Fact] (FDIC / FRED, 2025 — https://www.fdic.gov/quarterly-banking-profile/fdic-statistics-glance). Only 57 were "problem banks" (1.3%) [Fact] (FDIC QBP Q3 2025). **[Inference]** The institution count has fallen for 40 years via M&A and few de-novos; scale economics and compliance fixed costs mean the long-run trend is fewer, larger banks.

### 3. Customers, suppliers, regulators

- **Customers**: retail depositors/borrowers, small businesses, corporations (treasury, lending, capital markets), institutions (custody, prime brokerage), governments.
- **Suppliers**: core-tech vendors (FIS, Fiserv, Jack Henry, Temenos), card networks (Visa, Mastercard), credit bureaus (Equifax, Experian, TransUnion), FHLBs (wholesale funding), the Fed (reserves, discount window, payment rails).
- **Regulators** (US, overlapping): OCC (national banks), Federal Reserve (holding companies, systemic), FDIC (insurance, resolution), CFPB (consumer protection), state regulators. Capital is governed by Basel III as implemented domestically; the pending endgame re-proposal would reshape RWA and CET1 [Fact] (CRS R47855 — https://www.congress.gov/crs-product/R47855; Moody's, 2025 — https://www.moodys.com/web/en/us/insights/regulatory-news/us-proposes-final-basel-rules-transition-period-to-start-in-july-2025.html).

### 4. Geography and regional clusters

- **China dominates by assets**: ICBC (~$6.6T), Agricultural Bank of China, China Construction Bank, and Bank of China hold the top four global spots; 15 Chinese banks sit in the top 100 [Fact] (S&P Global, 2025 — above). These are state-directed, deposit-rich, domestically focused; scale reflects China's high savings rate and bank-centric financial system, not global competitiveness.
- **US** has the deepest, most profitable, and most fragmented system — thousands of banks but with megabanks capturing outsized profit and capital-markets revenue.
- **Europe**: HSBC is the largest (~$2.99T) [Fact] (S&P Global, 2025 — above); European banks are chronically lower-returning (structural overcapacity, negative-rate legacy, fragmented across borders), which is why they trade below US peers on P/TBV.
- **Clusters exist for different functions**: New York/London for capital markets and wholesale banking (talent, exchanges, regulators co-located); regional US hubs (Charlotte, Minneapolis, Pittsburgh) around super-regional headquarters. [Inference] Wholesale/capital-markets banking clusters where liquidity, talent and legal infrastructure concentrate; retail banking is inherently local and disperses.

### 5. Trade flows, industrial policy, national security

- Banking is not a physical-goods trade, but **cross-border capital flows, correspondent banking, and USD clearing** are the analog. The US exports financial services and, critically, exports the dollar system: USD clearing runs through US banks and Fedwire/CHIPS, giving Washington sanctions leverage (a national-security asset).
- **Industrial policy** is largely regulatory: deposit insurance, the Fed backstop, and too-big-to-fail treatment are implicit subsidies to large banks; the CRA directs lending to underserved areas. Post-2023 (SVB, Signature, First Republic), regulators effectively backstopped uninsured deposits, reinforcing that the sovereign underwrites the system.
- **National security**: payment-system control, sanctions enforcement, AML/CFT, and cyber resilience make large banks quasi-state infrastructure. Foreign ownership of US banks is tightly screened.

### 6. Business models gaining vs losing relevance

**Gaining:**
- **Scale universal banks** — technology and compliance fixed costs favor size; megabanks are taking deposit and payments share.
- **Payments and card networks / processors** — capital-light, high-margin, network-effect businesses (Visa, Mastercard, Fiserv, FIS) that sit atop banks and capture value.
- **Private credit / non-bank lenders** — Apollo, Blackstone, Ares and others now warehouse credit that banks once held, funded by insurance and institutional capital rather than deposits. [Inference] This is the most important structural migration: credit risk is moving off bank balance sheets to non-banks that face lighter capital rules — value migrating from the "balance-sheet" layer to unregulated warehousers.
- **Stablecoin / tokenized-money issuers** — see §7.

**Losing:**
- **Branch-heavy, sub-scale community banks** without a differentiated deposit niche — squeezed by tech costs and deposit competition; likely consolidation targets.
- **Monoline consumer lenders reliant on wholesale funding** — the SVB/First Republic lesson: no sticky deposit base equals fragility.
- **Banks reduced to BaaS balance-sheet rental** — thin, commoditized economics behind fintech brands.

### 7. Disruption vectors — real progress vs promotional claims

- **Stablecoins (the credible disruptor).** The GENIUS Act (signed July 18, 2025) created a US regulatory regime for payment stablecoins; outstanding USD stablecoins reached ~$280B at end-2025, up from ~$25B in 2020, and stablecoin transaction volumes have surpassed Visa's [Fact] (Richmond Fed, 2025 — https://www.richmondfed.org/banking/banker_resources/news_flash/2025/20251118_genius_act; Brookings, 2025 — https://www.brookings.edu/articles/next-steps-for-genius-payment-stablecoins/). The OCC conditionally granted national trust charters to Circle, Paxos and others in December 2025 [Fact] (same sources). **[Inference]** The genuine threat is *deposit disintermediation*: if consumers and corporates hold balances in stablecoins instead of bank deposits, banks lose their cheapest funding — the exact input that sets NIM (INPUTS §1). The GENIUS Act's yield prohibition currently blunts this (stablecoins can't pay interest), which is why banks lobby to keep that loophole closed. Real, but the magnitude for *core* deposits is still contested.
- **Tokenized deposits (banks' counter-move).** Banks issuing their own on-chain deposits (JPMorgan's Kinexys/JPM Coin) to keep programmable-money volume inside the regulated perimeter. [Inference] This is the incumbents defending the funding layer rather than ceding it.
- **AI in underwriting, fraud, and operations (real, incremental).** Lowers the compensation cost line (50–60% of non-interest expense) and improves credit models; helps scale players most because they can amortize the build.
- **Neobanks / fintech (partly real, partly hype).** Chime, Revolut et al. won customer interface and interchange economics, but most rely on partner-bank charters and struggle to build sticky, low-cost deposits or profitable lending. [Inference] They disrupt *distribution and fees*, not the *balance-sheet* core — value migrates to them at the interface layer but the funding/credit profit pool has proven defensible.
- **Distinguishing signal from noise.** [Inference] "Blockchain will replace banks" is largely promotional; what is actually happening is narrower and more dangerous to incumbents — (1) private credit pulling lending off bank balance sheets, and (2) stablecoins/fintech skimming payments and potentially deposits. Both attack specific profit pools rather than the whole institution.

### 8. Where value is set to migrate (synthesis)

- **Toward**: payment networks and processors (capital-light tolls), private-credit warehousers (lighter capital rules), and scale universal banks (cost and funding advantage), plus stablecoin/tokenized-money rails if regulation permits yield.
- **Away from**: sub-scale deposit-taking banks, wholesale-funded lenders, and any institution reduced to renting its balance sheet. The FDIC's 40-year consolidation trend (down to 4,379 institutions) and the rise of non-bank credit both point the same direction: **the charter's value is the deposit franchise and the sovereign backstop; everything else is increasingly contestable** [Inference].
- **The wildcard**: whether regulation lets non-banks (stablecoin issuers, private credit, fintechs) capture deposit-like funding and credit warehousing without bank-equivalent capital and insurance. If it does, value migrates decisively out of the regulated sector; if regulators pull those activities inside the perimeter, banks retain the core.

### 9. Complete output, customer, geography, funding, and policy map

Outputs include deposits/safekeeping, payments, liquidity, loans and commitments, mortgages, trade finance, treasury services, FX/derivatives, custody and financial advice. Credit losses, fraud, data breaches, foreclosures and systemic externalities are negative outputs. The borrower uses credit, the depositor supplies funding, merchants/payees use payment acceptance, and taxpayers or industry-funded insurance may backstop failure—four distinct customer/stakeholder roles.

Customers range from underbanked households and affluent clients to SMEs, large corporates, governments and financial institutions. Branch density and local information matter in small-business/consumer banking; global networks matter in wholesale services. Banking remains jurisdictional because charters, currencies, deposit guarantees, payment systems and insolvency law are national, even when capital and corporate clients cross borders.

Participants include community and regional banks, global systemically important banks, cooperatives/credit unions, state-owned and development banks, digital banks, nonbank lenders, card/payment firms, private credit, mortgage agencies and capital markets. Concentration can improve technology scale while increasing systemic and political constraints.

Private funding is the bank's own deposit, debt and equity stack; public influence arrives through central-bank reserves and liquidity, deposit insurance, government guarantees, development programs, emergency facilities and sovereign securities. Rules cover chartering, capital and liquidity, leverage, resolution, deposit insurance, consumer/fair lending, AML/sanctions, privacy, cyber/operational resilience, market conduct and concentration. Global Basel standards are implemented differently by each jurisdiction.

Cross-market links connect banks and monetary policy to real estate, consumers, business investment, government finance and markets. Higher rates can initially lift asset yield, then raise deposit cost and credit loss; falling collateral values tighten credit; government deficits affect securities supply and rates; private credit and securitization disintermediate assets while banks may still supply leverage, lines and payment rails. Geography must include borrower and collateral exposure, not branch address alone.

### Sources

- Bank for International Settlements, Basel Framework — https://www.bis.org/basel_framework/
- S&P Global, world's largest banks by assets 2025 — https://www.spglobal.com/market-intelligence/en/news-insights/articles/2025/4/the-worlds-largest-banks-by-assets-2025-88424232
- FDIC, Quarterly Banking Profile Q3 2025 — https://www.fdic.gov/news/speeches/2025/fdic-quarterly-banking-profile-third-quarter-2025
- FDIC, Statistics at a Glance — https://www.fdic.gov/quarterly-banking-profile/fdic-statistics-glance
- Congressional Research Service R47855, Basel III Endgame — https://www.congress.gov/crs-product/R47855
- Moody's, US Basel rules finalized — https://www.moodys.com/web/en/us/insights/regulatory-news/us-proposes-final-basel-rules-transition-period-to-start-in-july-2025.html
- Richmond Fed, Stablecoins and the GENIUS Act — https://www.richmondfed.org/banking/banker_resources/news_flash/2025/20251118_genius_act
- Brookings, Next steps for GENIUS payment stablecoins — https://www.brookings.edu/articles/next-steps-for-genius-payment-stablecoins/
- Congress.gov, Public Law 119-27 (GENIUS Act) — https://www.congress.gov/119/plaws/publ27/PLAW-119publ27.pdf
- Kansas City Fed, market structure of core banking providers — https://www.kansascityfed.org/research/payments-system-research-briefings/market-structure-of-core-banking-services-providers/

## 4. Operating Mechanics


The bank's core trick is **maturity, liquidity and credit transformation**: fund short and liquid (deposits repayable on demand), lend long and illiquid (mortgages, business loans), and earn the spread while managing the mismatch. Everything below is machinery around that one arbitrage. The reader should leave able to (a) trace the workflow, (b) compute the unit economics, and (c) value a bank at any life-stage.

### 1. The production workflow

1. **Gather funding.** Open deposit accounts; issue debt; borrow wholesale. Target: maximize the share of cheap, sticky core deposits (see INPUTS §1).
2. **Underwrite and originate assets.** Score/underwrite borrowers, price loans at a spread over a funding benchmark, set covenants and collateral. Alternatively buy securities (Treasuries, agency MBS) with surplus funding.
3. **Hold or distribute.** *Originate-to-hold* (keep the loan, earn NII, bear the credit risk) vs *originate-to-distribute* (sell/securitize, earn fees, recycle capital). The choice hinges on capital cost and fee economics.
4. **Service and monitor.** Collect payments, manage delinquencies, re-margin, provision for losses under CECL (Current Expected Credit Loss) — a forward-looking reserve booked at origination.
5. **Manage the balance sheet (ALM).** Asset-Liability Management hedges interest-rate and liquidity risk (duration matching, swaps, deposit-beta modeling). This is the survival function.
6. **Recycle capital.** Retained earnings and buybacks/dividends manage the CET1 ratio; growth is rationed by capital.

### 2. Competing methods and technologies — the real trade-offs

- **Spread banking (hold) vs fee/capital-light banking (distribute).** Holding loans earns NII but consumes capital and risk-weighted-asset (RWA) capacity; distributing earns fee income and frees capital but forfeits recurring spread. *Method A (hold) beats Method B (distribute) when* the loan spread comfortably exceeds the cost of the capital it ties up and funding is cheap and stable; *B beats A when* capital is scarce/expensive (post-Basel-endgame) or the bank has a low-cost origination engine but weak deposit base. This is why capital-constrained banks and non-banks favor originate-to-distribute, while deposit-rich banks portfolio their best loans.
- **Relationship vs transactional models.** Community/regional banks compete on local relationships and higher-touch underwriting (wider NIM: 3.73% for community banks vs 3.34% industry, Q3 2025 [Fact], FDIC QBP Q3 2025 — https://www.fdic.gov/news/speeches/2025/fdic-quarterly-banking-profile-third-quarter-2025). Megabanks compete on scale, technology and product breadth (payments, cards, capital markets). *Relationship banking wins* where information is soft and local (small-business, CRE); *scale banking wins* in commoditized, data-rich products (credit cards, mortgages, treasury services).
- **Build vs rent core technology.** Megabanks build proprietary stacks; smaller banks rent from FIS/Fiserv/Jack Henry (INPUTS §4). Building costs billions but yields product velocity and unit-cost advantage; renting is cheaper up front but caps differentiation and cedes pricing power to vendors. [Inference] The build/rent divide is now a primary driver of the widening scale gap.
- **Universal vs specialist.** Universal banks (JPMorgan, BofA) cross-subsidize and diversify revenue; monoline specialists (card banks, custody banks, mortgage banks) optimize one economic engine. Diversification lowers earnings volatility but dilutes returns; specialization raises both.

### 3. Asset types and their economics

- **Loans** — the RWA-heavy, spread-earning core. Commercial & industrial, commercial real estate (CRE — the current stress point), residential mortgage, consumer/card. Card is highest-yield/highest-loss; mortgage is low-yield/low-loss and rate-sensitive.
- **Securities** — Treasuries and agency MBS held for liquidity and yield. Classified **Available-for-Sale (AFS)** — marked to market through equity (AOCI) — or **Held-to-Maturity (HTM)** — held at cost, not marked. [Inference] The HTM/AFS choice is where the industry's $337.1B of unrealized losses (Q3 2025, FDIC QBP Q3 2025) partly hides: HTM losses don't hit reported equity unless the bank is forced to sell, which is exactly what a run forces.
- **Deposits (a liability that behaves like an asset)** — non-maturity deposits have franchise value because their effective duration and low cost make them worth more than par to an acquirer; this is captured as a **core deposit intangible** in M&A.

### 4. Unit economics — the cost stack

For a marginal dollar of earning assets, the P&L waterfall is:

1. **Asset yield** (e.g., loan/securities yield) minus
2. **Funding cost** (deposit + wholesale cost) = **Net interest margin**, ~3.34–3.39% industry (Q3–Q4 2025) [Fact] (FDIC QBP Q3/Q4 2025). Minus
3. **Provision for credit losses** (through-cycle ~0.5–0.7%; net charge-offs were 0.61% Q3 2025 [Fact], same). Plus
4. **Non-interest (fee) income** — cards/interchange, service charges, wealth management, investment banking, trading. Minus
5. **Non-interest expense** — of which compensation is 50–60% [Estimate] (Stealth Agents, 2026 — https://stealthagents.com/research/banking-industry-staffing-costs-2026); measured by the **efficiency ratio** (58.7% Q1 2024 [Fact], FDIC — https://www.fdic.gov/system/files/2024-08/2024-q1-qbp_0.pdf). Equals
6. **Pre-tax, pre-provision profit → net income → ROA / ROE / ROTCE.**

Industry ROA was 1.27% in Q3 2025 [Fact] (FDIC QBP Q3 2025); a ~1% ROA on ~10x leverage (assets/equity) produces a ~10%+ ROE, and best-in-class franchises reach ROTCE in the low-20s — JPMorgan posted 22% ROTCE in 2024 [Fact] (JPMorgan 2024 10-K — https://www.sec.gov/Archives/edgar/data/19617/000001961725000270/jpm-20241231.htm). **[Inference]** The "marginal unit" cost is dominated by funding and the capital it must carry; a bank's whole game is widening (1)–(2), suppressing (3) and (5), and growing (4) without adding RWA.

### 5. KPIs practitioners actually track

- **NIM** (spread), **efficiency ratio** (cost discipline), **ROTCE / ROA / ROE** (returns), **CET1 ratio** (capacity/safety; JPM 14.6% end-2024, above), **net charge-off and non-performing/nonaccrual rates** (credit; 1.49% past-due Q3 2025), **reserve coverage ratio** (allowance vs bad loans; 178.4% Q3 2025 [Fact], FDIC QBP Q3 2025), **loan-to-deposit ratio** (funding tightness), **deposit beta and % non-interest-bearing deposits** (funding quality), **tangible book value per share** (the valuation anchor), and for large banks **liquidity coverage ratio (LCR)** and **supplementary leverage ratio (SLR)**.

### 6. Capacity, lead times, failure points

- **Capacity** is measured in risk-weighted assets against CET1, not physical throughput. A bank "at capacity" must raise equity, retain earnings, sell assets, or slow lending.
- **Lead times**: a de-novo charter takes 1–3 years to approve and years to reach profitability; a core-system migration is a 2–5 year program; loan seasoning (time to reveal credit quality) is quarters to years.
- **Characteristic failures**: (i) **liquidity run** (SVB 2023 — duration mismatch + uninsured deposits + speed of digital withdrawal); (ii) **credit blow-up** (concentrated CRE or consumer losses exhausting reserves and CET1); (iii) **rate/ALM mismatch** (borrowing short, lending long fixed into a hiking cycle); (iv) **operational/fraud/compliance** (AML fines, cyber). All four end at the same place: capital depletion below the regulatory minimum, triggering FDIC resolution.

### 7. Valuation across life-stages

Banks are valued differently from industrials because leverage, mark-to-model assets, and regulation distort earnings and book value.

**(a) Mature, cash-generative banks (JPMorgan, regionals).**
- **Primary method: Price-to-Tangible-Book-Value (P/TBV) regressed against forward ROTCE.** The core identity is **P/TBV ≈ (ROTCE − g) / (COE − g)**, and empirically P/TBV = P/E × ROTCE [Fact] (FIG IB Guide — https://ibinterviewquestions.com/guides/fig-investment-banking/roe-ptbv-regression-fair-value-analysis). Analysts plot forward ROTCE (x) vs P/TBV (y) across a peer set; the regression line is "fair value," with R² typically 47–68% [Fact] (same). A bank earning ROTCE above its cost of equity trades above 1.0x TBV; one earning below trades at a discount. Median bank P/TBV reached ~1.55x by November 2024 [Fact] (Victaurs / IB Guide, 2024 — https://www.victaurs.com/p/update-bank-ptbv-and-rotce-scatter).
- **Why P/TBV not P/E alone:** book value is the loss-absorbing capital base and TBV strips goodwill/intangibles created by acquisitions, so it reflects *real* equity at risk [Fact] (BankSift — https://banksift.org/faq/what-is-rotce). **Dividend discount / residual income models** are also used because payout capacity is capital-constrained. P/E multiples (typically 9–13x) are a cross-check.

**(b) Cyclical / asset-heavy banks across the cycle (regionals, CRE-heavy, capital-markets-heavy).**
- Value on **normalized (through-the-cycle) earnings**, not peak or trough. In a benign year, low provisions flatter ROTCE; in a downturn, provisions and charge-offs spike and can turn ROTCE negative. **[Inference]** The mistake is capitalizing peak earnings — the correct approach applies a mid-cycle charge-off assumption and a mid-cycle NIM, then a P/TBV consistent with normalized ROTCE. **Stress-test / capital-adequacy overlays** (how much CET1 survives a severe scenario) set the floor; a bank that would breach minimums in stress deserves a discount or a recapitalization haircut. Tangible book value per share is the anchor because it is far less cyclical than earnings.

**(c) Pre-revenue / early / distressed (de-novos, fintech banks, thrifts converting, failing banks).**
- **De-novo / early-stage banks** are valued on **capital raised plus a franchise-build option** — essentially book value with a small premium for the charter and growth optionality; there is no earnings stream to capitalize, so P/TBV near or slightly above 1.0x plus a multiple on *projected* steady-state ROTCE discounted back. The charter itself has scarcity value.
- **Fintech "banks" / BaaS players** are valued on customer/deposit unit economics (customer acquisition cost vs lifetime value, deposits per user, take-rate) more like a platform than a balance sheet, until they scale into spread economics.
- **Distressed / failing banks** are valued on **liquidation / resolution value**: mark the loan book and securities (including HTM) to fair value, subtract deposit-run risk, and what remains for equity is often zero — which is why failed-bank equity is typically wiped out and the FDIC sells the deposit franchise (the valuable part) to an acquirer at a **core-deposit-intangible** premium. The asset that survives is the deposit relationship, not the equity.

**Cross-cutting caveat.** [Inference] Reported book value can overstate true equity when AFS/HTM losses are unrealized (the $337B latent loss), so a rigorous valuation marks securities and stresses the loan book before trusting TBV. This is the single most important adjustment in bank valuation post-2023.

### 9. Complete balance-sheet, liquidity, and failure mechanics

The full workflow is acquire and verify customer → gather funding/payment relationship → underwrite and price → originate or purchase asset → fund and hedge → service/monitor → collect, modify or work out → charge off/recover → recycle capital and liquidity. Commitments consume contingent capacity before funding. Loan sale, securitization and syndication separate origination, funding, servicing and ultimate risk holder.

Net interest income must be decomposed by asset yield, funding cost, volume/mix, nonaccrual and hedge effects; fees by payments, service, origination, wealth and market activity. Expected credit loss, realized charge-offs and recoveries occur on different timelines. Accounting capital, regulatory capital, tangible equity and loss-absorbing debt answer different questions.

Working-capital, cash and liquidity analysis includes deposit segmentation and concentration, uninsured and operational balances, maturity ladder, contingent draws, collateral calls, encumbrance, available central-bank capacity and monetizable securities. Mark-to-market loss may not reduce current earnings but can still undermine tangible capital or depositor confidence. Resolution value depends on asset quality and speed, not only reported book value.

Minimum KPIs include average balances, loan/deposit growth, deposit beta and mix, NIM and sensitivity, fees, efficiency, delinquency/nonaccrual, net charge-offs, allowance coverage, criticized loans, concentration, CET1 and tangible common equity, risk-weighted assets, liquidity sources, uninsured deposits, securities duration/losses and ROTCE. Stress rapid deposit flight, parallel and nonparallel rate shocks, unemployment, property-price fall, borrower-sector shock, cyber/payment outage, wholesale closure and a capital-rule change together rather than in isolation.

### Sources
- FDIC, Quarterly Banking Profile Q3 2025 — https://www.fdic.gov/news/speeches/2025/fdic-quarterly-banking-profile-third-quarter-2025
- FDIC, Quarterly Banking Profile Q4 2025 — https://www.fdic.gov/news/speeches/2026/fdic-quarterly-banking-profile-fourth-quarter-2025
- FDIC, Q1 2024 QBP (efficiency ratio) — https://www.fdic.gov/system/files/2024-08/2024-q1-qbp_0.pdf
- JPMorgan Chase 2024 Form 10-K — https://www.sec.gov/Archives/edgar/data/19617/000001961725000270/jpm-20241231.htm
- FIG IB Guide, ROE–P/TBV regression — https://ibinterviewquestions.com/guides/fig-investment-banking/roe-ptbv-regression-fair-value-analysis
- FIG IB Guide, P/B vs P/TBV — https://ibinterviewquestions.com/guides/fig-investment-banking/price-to-book-value-tangible-book-value
- Victaurs, Bank P/TBV & ROTCE scatter update — https://www.victaurs.com/p/update-bank-ptbv-and-rotce-scatter
- BankSift, ROTCE explainer — https://banksift.org/faq/what-is-rotce
- BankSift, efficiency ratio — https://banksift.org/metrics/efficiency-ratio
- Stealth Agents, banking staffing costs — https://stealthagents.com/research/banking-industry-staffing-costs-2026

## 5. Economics and Valuation


Benchmark bands are diagnostic starting points; refresh for product, asset, geography, contract, and cycle.

### Core unit-economic identity

Pre-provision profit = average earning assets × yield − average funding × cost + fees − operating expense. Net income then subtracts credit provision, tax and other losses; value creation depends on return on tangible equity above its cost through the cycle.

### Ten benchmark measures

| Measure | Diagnostic band or unit | Decision use |
| --- | --- | --- |
| Net interest margin | often roughly 2–4% for US commercial banks; model-specific | Core spread |
| Efficiency ratio | roughly 40–70%; lower is better, mix-dependent | Operating productivity |
| Loan/deposit ratio | often ~70–100% | Funding reliance |
| CET1 ratio | commonly ~10–15% for large banks, rule-specific | Regulatory loss buffer |
| Tangible common equity/assets | often mid-single to high-single digits | Simple balance-sheet buffer |
| Deposit beta | 0–100% of policy-rate move by product/cycle | Funding repricing |
| Net charge-offs | basis points of average loans by portfolio/cycle | Realized credit |
| Allowance coverage | percent of loans or nonperformers | Expected loss reserve |
| ROTCE | through-cycle percent versus cost of equity | Value creation |
| Liquidity runway | cash/borrowing capacity versus stressed outflows | Survival under run |

### Accounting-to-cash bridge

Reconcile average balances, purchase accounting, nonaccrual, securities marks, hedges, provision/allowance, charge-offs, fee deferrals, mortgage servicing, regulatory capital and OCI. Reported maturity does not equal behavioral duration.

### Highest-value sensitivities

- Parallel and curve rate shocks, deposit beta/mix, prepayments and hedge basis.
- Unemployment, borrower cash flow, property/collateral, vintage and concentration.
- Deposit run, contingent draws, collateral haircuts and wholesale closure.
- Capital/liquidity rules, operational/cyber failure, fraud and conduct.

### Valuation discipline

Use normalized ROTCE, tangible book, growth and risk; residual income is preferable to a generic earnings multiple. Separate credit, duration, liquidity, operational and franchise value.


## 6. Regulation and Public Funding


Snapshot reviewed through **2026-07-14**. Verify enacted text, implementation dates, litigation, and current guidance.

### Permission chain

Depositor supplies funding and payment relationship; bank underwrites and transforms; borrower uses credit; payment/custody rails settle; guarantor/insurer may absorb loss; central bank and supervisor provide reserve/liquidity/rules; shareholders and debt absorb residual loss.

### Jurisdiction and regime map

| Jurisdiction or layer | Core regimes and authorities | Economic transmission |
| --- | --- | --- |
| United States | Fed/OCC/FDIC/state supervision, Basel implementation, deposit insurance, CFPB/consumer, AML/sanctions and resolution | Capital, liquidity, funding, conduct, mergers and failure |
| European Union/Euro area | ECB/SSM, EBA/CRR/BRRD, national conduct and deposit schemes | Capital, MREL, resolution, rates and sovereign-bank links |
| United Kingdom | PRA/FCA, ring-fencing and resolution framework | Prudential, conduct and structure |
| Global/cross-border | Basel standards, correspondent/FX/payment, sanctions and host-country rules | Capital fragmentation, liquidity and market access |

### Public and private funding

Private funding is deposits, repo/secured borrowing, wholesale debt, securitization, equity and retained earnings. Public support includes central-bank reserves/liquidity, deposit insurance, government guarantees, development lending, mortgage agencies and crisis facilities.

### Enforcement and liability

Supervisors can impose capital/liquidity add-ons, growth/dividend limits, remediation, fines, restitution, management removal, resolution or charter loss. AML, sanctions, fair-lending and consumer failures can be franchise-level.

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
| 1980s US savings-and-loan crisis | Rate mismatch and weak asset quality met deregulation and insurance | Institutions failed after net worth eroded | Duration and moral hazard compound |
| 2007–2009 global financial crisis | Weak mortgage vintages were leveraged and distributed | Funding, collateral and credit failed together | Origination transfer does not remove system risk |
| 2011–2012 euro-area sovereign-bank loop | Banks and governments held each other's risk | Funding and sovereign spreads reinforced | Currency and fiscal backstop matter |
| March 2023 US regional-bank failures | Uninsured concentrated deposits met duration losses | Digital runs forced securities realization and resolution | Liquidity value can differ from accounting capital |
| Private-credit/stablecoin expansion | Nonbanks target lending and payment/deposit interfaces | Banks retain rails but face funding and asset competition | Disruption attacks specific balance-sheet layers |

### Practitioner extraction

- **Leading signals:** Deposit flow/rate, H.8 balances, wholesale spread, collateral marks, delinquencies, criticized loans, allowance, capital and supervisory actions.
- **Evidence that breaks the easy thesis:** NIM growth from duration risk, deposit growth via expensive brokered funds, or low charge-offs despite rising early delinquency/criticized balances.
- **Durable lesson:** A bank is a confidence-sensitive balance sheet; capital, liquidity, credit and operations must work simultaneously.


## 8. Data Sources and Monitoring Dashboard


Preserve observation period, unit, definition, geography, and revision vintage.

### Primary source map

| Source | Cadence | Best use | Caveat |
| --- | --- | --- | --- |
| [FDIC BankFind and Quarterly Banking Profile](https://www.fdic.gov/quarterly-banking-profile) | quarterly | Industry balance sheet, earnings and failures | US insured institutions |
| [FFIEC Call Reports](https://cdr.ffiec.gov/public/) | quarterly | Bank-level regulatory data | Complex schedules and restatements |
| [Federal Reserve H.8 and Financial Accounts](https://www.federalreserve.gov/releases/h8/) | weekly/quarterly | Credit and deposit aggregates | Seasonal and consolidation effects |
| [HMDA data](https://ffiec.cfpb.gov/) | annual | Mortgage applications/origination and demographics | Reporting scope changes |
| [BIS Basel Framework](https://www.bis.org/basel_framework/) | rule-driven | Global prudential standard | Local implementation differs |

### Indicator stack

- **Leading:** deposit rates/flows; early delinquency; criticized loans; lending standards; wholesale spread.
- **Coincident:** NIM; loan/deposit growth; provisions; fees; liquidity; capital.
- **Lagging:** charge-offs; foreclosures; resolution; restitution; capital rebuild.

### Minimum dashboard

1. **Net interest margin** — often roughly 2–4% for US commercial banks; model-specific; Core spread.
2. **Efficiency ratio** — roughly 40–70%; lower is better, mix-dependent; Operating productivity.
3. **Loan/deposit ratio** — often ~70–100%; Funding reliance.
4. **CET1 ratio** — commonly ~10–15% for large banks, rule-specific; Regulatory loss buffer.
5. **Tangible common equity/assets** — often mid-single to high-single digits; Simple balance-sheet buffer.
6. **Deposit beta** — 0–100% of policy-rate move by product/cycle; Funding repricing.
7. **Net charge-offs** — basis points of average loans by portfolio/cycle; Realized credit.
8. **Allowance coverage** — percent of loans or nonperformers; Expected loss reserve.
9. **ROTCE** — through-cycle percent versus cost of equity; Value creation.
10. **Liquidity runway** — cash/borrowing capacity versus stressed outflows; Survival under run.

### Normalization rules

- Use average balances for yields/margins.
- Segment credit by vintage, type and geography.
- Separate accounting, regulatory and tangible capital.
- Stress behavior rather than contractual maturity alone.

### Evidence traps

- Treating uninsured deposits as homogeneous.
- Using book equity without marks/duration.
- Calling provision a realized loss.

## 9. Geographic Operating Models

Geography changes ownership, contracting, cost, funding, regulation and risk; compare like with like.

| Geography / archetype | Operating model | Economic and risk implications |
| --- | --- | --- |
| United States | Thousands of community/regional banks plus money-center institutions under deposit insurance and multi-agency supervision | Deposit franchise, securities duration, local credit and scale in compliance/technology differentiate |
| Euro area/United Kingdom | Universal banks operating across lending, deposits, payments, markets and wealth | Negative/positive rate transmission, sovereign exposure and cross-border rules shape returns |
| China | State-influenced banks funding policy priorities with large deposit bases | Administered credit, property/local-government exposure and state support alter loss recognition |
| Emerging markets | High-spread banks with lower financial penetration and greater sovereign/currency volatility | Inflation, dollar funding, concentration and political intervention can dominate |
| Offshore/financial centers | Wholesale, private banking and cross-border booking models | Liquidity, tax transparency, sanctions and parent support are central |

## 10. Cross-Industry Dependency Map

| Dependency class | Linked markets and institutions | Transmission into this industry |
| --- | --- | --- |
| Funding | Retail/corporate deposits, central banks, secured borrowing, wholesale debt and equity | Deposit beta and run behavior reprice faster than contractual maturity suggests |
| Borrowers/collateral | Households, businesses, real estate, governments and marketable securities | Income, leverage and collateral cycles convert macro shocks into credit loss |
| Payments/market infrastructure | Card networks, clearing, settlement, custody, data centers and cyber vendors | Operational failure can trigger liquidity and conduct loss |
| Policy/regulation | Central banks, deposit insurance, capital/liquidity rules, resolution and consumer law | Policy rates move margins while prudential rules constrain growth and payouts |
| Adjacent finance | Private credit, fintech, money funds, capital markets and insurers | Substitution removes prime assets or deposits and can return risk through commitments |

The practical test is to trace a shock through availability, delivered cost, working capital, output, customer economics, financing and eventual substitution—not merely name the adjacent market.

## 11. Decision-Grade Unit Economics

> The numerical example below is illustrative, not a current market forecast or universal benchmark. Replace every assumption with asset-, contract-, product- and geography-specific evidence.

**Representative unit:** A $1.0bn average earning-asset banking book supported by $100m tangible common equity.

**Core equation:** `Net income = earning-asset yield − funding cost + fees − operating expense − expected credit loss − tax/other; ROTCE = net income ÷ average tangible common equity`

| Bridge item | Illustrative assumption and calculation | Result / interpretation |
| --- | --- | --- |
| Asset revenue | $1.0bn × 7.0% average yield | $70m |
| Funding cost | Deposit/wholesale funding burden | $24m |
| Net interest income | $70m − $24m | $46m |
| Fees less operating expense | $8m fees − $25m operating expense | −$17m net |
| Credit and tax | $8m through-cycle credit loss + $4m tax/other | $12m |
| Illustrative net income/ROTCE | $46m − $17m − $12m = $17m; $17m ÷ $100m | $17m and 17% ROTCE before unusual marks/reserve changes |

**Decision test:** Reprice the entire behavioral balance sheet under rate, deposit-run and credit scenarios; current NIM or provision is not a through-cycle return.

## 12. Industry Balance and Marginal Economics

| Balance concept | Industry-specific definition | What to measure |
| --- | --- | --- |
| Marginal supply unit | Last lender/security buyer willing to fund a borrower at required capital and liquidity return | Funding cost, risk weight and loss expectation set loan pricing |
| Marginal customer | Borrower able to defer investment, refinance elsewhere or issue securities | Debt-service capacity and alternatives determine demand |
| Clearing mechanism | Loan spread/fees over benchmark plus underwriting terms and collateral | Nominal coupon does not equal risk-adjusted yield |
| Cash shutdown point | New lending stops when risk-adjusted spread fails to cover funding, operations, expected loss and capital | Existing loans cannot be exited at par in stress |
| New-capacity incentive | Incremental retained earnings/equity and stable funding support asset growth above hurdle ROTCE | Capital and liquidity—not deposits alone—gate capacity |
| Adjustment lag | Immediate market repricing, quarters for deposits, years for credit vintages and workouts | Rate and credit cycles appear in different periods |

## 13. Terminology and Comparability Traps

| Reported term | Common but invalid interpretation | Required normalization |
| --- | --- | --- |
| Deposits | Stable low-cost funding | Segment insured/uninsured, operational/nonoperational, concentration, beta, tenure and channel |
| Net interest margin | Rate sensitivity or profitability | Bridge asset/funding mix, purchase accounting, hedges, nonaccrual and balance growth |
| CET1 ratio | Excess distributable capital | Apply binding standardized/stress requirements, losses, growth and OCI treatment |
| Provision | Current-period credit loss | Separate allowance build/release, charge-offs, recoveries and portfolio change |
| Tangible book value | Liquidation value | Stress credit, securities, deposits, tax assets, intangibles and franchise value |


