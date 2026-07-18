# Aerospace & Defense

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

Civil aerospace, defense platforms and systems, space, munitions, electronics, and lifecycle sustainment across primes and qualified suppliers.

### Operating taxonomy

| Segment | What is sold | Primary unit | Do not aggregate without |
| --- | --- | --- | --- |
| Commercial aircraft and aerostructures | Transport aircraft, structures and systems | deliveries, shipsets, seats | Certification, rate, engine availability and airline/lessor demand |
| Engines and propulsion | Civil/defense engines, rocket motors and services | engines, flight hours, shop visits | Installed base, time-on-wing, concessions and maintenance reserves |
| Defense platforms | Aircraft, ships, vehicles and integrated systems | units, funded backlog, readiness | Appropriation, configuration, classified requirements and sustainment |
| Missiles, munitions and sensors | Precision weapons, seekers, radars and mission electronics | rounds, lots, channels, range | Energetics, microelectronics, test and surge capacity |
| Space and services | Launch, satellites, payloads, ground systems and data/services | launches, kg, satellites, contracted service | Reliability, orbit, spectrum, insurance and government demand |

### Specifications that change value

- State configuration/block, customer, mission, certification, production lot and acceptance status.
- Backlog must distinguish options, authorized, appropriated, contracted, funded and executable.
- Capacity is qualified shipsets/engines/rounds per period, including test and customer acceptance.
- Aftermarket needs installed base, age, utilization, shop-visit interval, parts scope and IP rights.
- Cost must state recurring unit, nonrecurring development, customer-funded tooling and learning-curve basis.

### Role map

Legislature funds; ministry/agency/program office procures; prime integrates; tiers supply; regulator/customer certifies; service operates; depot/MRO sustains; ally/export authority controls transfer; lessor/bank finances civil assets.

### Terms that must be explicit

- authorization, appropriation, obligation and outlay
- funded versus unfunded backlog
- EAC and cumulative catch-up
- shipset and learning curve
- readiness, availability and mission-capable rate


## 2. Inputs and Dependencies


Scope: the material upstream inputs that feed the design, manufacture, and sustainment of aircraft, engines, missiles, satellites, and their subsystems. The industry is unusual in that its cost and capacity are gated less by commodity prices than by **certified specialty materials, a security-cleared skilled workforce, and multi-year supplier qualification**. Those are the true bottlenecks.

### 1. Specialty metals and materials (the capacity-defining input)

**Titanium.** Aerospace-grade titanium is the single most strategically fragile material input. Before Russia's 2022 invasion of Ukraine, Airbus sourced an estimated ~60% and Boeing ~80% of their titanium from Russia's VSMPO-AVISMA [Estimate] (AeroTime, 2022 — https://www.aerotime.aero/articles/32464-titanium-supply-crisis-what-does-this-mean-for-aerospace). VSMPO alone represents roughly 25% of the global titanium sponge market and runs ~40,000–45,000 tonnes/year of capacity [Estimate] (Global Growth Insights, 2024 — https://www.globalgrowthinsights.com/market-reports/titanium-sponge-market-104732). The remaining Western/allied supply is concentrated among a handful of names: TIMET (owned by Precision Castparts / Berkshire Hathaway), ATI Inc. (Allegheny), Toho Titanium and Osaka Titanium (Japan), and Kobe Steel — together only ~38–42% of global capacity [Estimate] (same source). The U.S. is import-dependent for **more than 90%** of the titanium sponge used in defense applications [Fact] (Aero Magazine, 2024 — https://www.aero-mag.com/titanium-grip-by-russia-china-threatens-western-aerospace-supply-chains).

Why this is a hard bottleneck: qualifying a new titanium supplier — or even a new part from an existing supplier — typically takes **more than a year** of technical and commercial validation because every heat lot must be traceable and metallurgically certified to airframe/engine specs (AeroTime, 2022 — same URL). So a supply shock cannot be resolved by simply buying elsewhere; the substitute must be re-qualified. Titanium's value is its strength-to-weight ratio and heat tolerance in fan blades, engine cases, and airframe structure; the main substitutes (aluminum, steel, carbon-fiber composites) trade off weight, temperature limits, or galvanic compatibility with composites, so titanium is effectively non-substitutable in hot-section and high-load structure. **[Inference]** Pricing power sits firmly with the sponge/mill producers on aerospace grades because demand is inelastic and qualification locks buyers in; this is why counterfeit/mis-certified titanium (the 2024 Boeing/Airbus fake-documentation scare) is a systemic risk rather than a one-off (SupplyChainBrain, 2024 — https://www.supplychainbrain.com/blogs/1-think-tank/post/40637-how-boeings-counterfeit-titanium-crisis-was-predictable-and-preventable).

**Other critical materials.**
- **Nickel-based superalloys** (Inconel, René, single-crystal turbine-blade alloys) for engine hot sections — cobalt, nickel, rhenium and hafnium are the pinch-point elements; rhenium and cobalt supply is thin and partly China/DRC-exposed. **[Inference]**
- **Carbon fiber composites** (Toray, Hexcel/Solvay-Syensqo) — Toray is the qualified supplier for Boeing 787 primary structure; composite prepreg is a qualification-locked input like titanium. **[Inference, industry-known]**
- **Rare earths and magnets** for actuators, radar, and electric-propulsion motors — China dominates processing; a recognized single-point-of-failure for defense electronics. **[Inference]**
- **Aluminum-lithium alloys**, high-strength fasteners, and **semiconductors** (rad-hardened and RF/GaN for radar and missiles) round out the list.

**Cost sensitivity.** Raw metal is a modest share of an airframe's cost, so a titanium price spike hits margins less through the commodity line and more through **schedule disruption and yield loss** — a grounded line or slipped qualification is far more expensive than the metal. **[Inference]**

### 2. Propulsion and major bought-in systems

Engines are the highest-value single input to an airframe and are supplied by an oligopoly: CFM International (GE Aerospace + Safran JV), Pratt & Whitney (RTX), Rolls-Royce, and GE Aerospace. CFM holds roughly 40–44% of the installed commercial-engine base and supplies over 60% of narrow-body engines; on widebodies GE powers ~52% and Rolls-Royce ~33% of aircraft [Estimate] (Simple Flying / Statista, 2024 — https://simpleflying.com/rolls-royce-pratt-whitney-ge-dominate-engine-market/). The global aircraft-engine market was worth over $81 billion in 2024 [Estimate] (Global Market Insights via AeroTime — https://www.aerotime.aero/articles/32417-who-are-the-world-s-largest-aircraft-engine-manufacturers). Airframers do not make their own engines, so the engine OEMs capture enormous downstream value (see MECHANICS). Avionics (Collins/RTX, Honeywell, Thales), landing gear (Safran, Héroux-Devtek), and structures (Spirit AeroSystems, GKN) are the other major bought-in systems.

### 3. Labor — the binding constraint after materials

The workforce is arguably the tightest input today. The U.S. A&D industry employed over 2.2 million workers across the supply chain in 2024 (AIA, 2025 — https://www.aia-aerospace.org/news/american-aerospace-defense-industry-continues-economic-dominance/). Both Boeing and Airbus have missed production schedules for lack of machinists, welders, and specialized engineers (Aerospace Manufacturing & Design, 2024 — https://www.aerospacemanufacturinganddesign.com/article/manufacturing-skilled-workforce-shortage--will-hamper-aerospace-s-take-off/). Two structural features make labor a bottleneck rather than a market that clears on wages:
- **Security clearances and ITAR.** Upwards of 90% of technical jobs in U.S. aerospace are ITAR-restricted to U.S. persons [Estimate] (Amtec, 2026 — https://www.amtec.co/blog/aerospace-defense-workforce-report), and cleared defense work narrows the pool further. The industry cannot import the marginal engineer.
- **Demographics.** Retirement and attrition run roughly 10% above the national industrial average, draining tacit process knowledge as every segment expands simultaneously and bids for the same finite talent (Amtec, 2026 — same URL).

**[Inference]** Because skilled labor caps throughput at the airframers and at the fragile Tier 2/3 base, wage inflation flows into unit cost with a lag and, more importantly, delivery rates — the real scarce output — are gated by headcount, not order books.

### 4. Software, IP, and certification data

Modern aircraft and weapons are software-defined: flight control, mission systems, and digital-engineering models are core IP. The certification basis itself (DO-178C for software, AS9100 quality systems, type certificates) is an intangible input — a qualified design and its FAA/EASA/DoD approvals are an asset that takes years and hundreds of millions to create and cannot be bought on the market. **[Inference]** This is why incumbents' certified type designs are a moat (see LANDSCAPE).

### 5. Capital, energy, logistics, and regulation

- **Financial capital.** Programs are extraordinarily capital- and working-capital-intensive: a clean-sheet airframe or engine runs into the tens of billions and a decade-plus before positive cash flow, so access to patient capital (and, in practice, government development funding / launch aid) is itself an input. Boeing's 2024 net loss of $11.83 billion illustrates how thin the cash margin is when programs slip (Economy Middle East, 2025 — https://economymiddleeast.com/news/boeing-reports-net-loss-11-83-billion-2024-largest-since-2020/).
- **Energy.** Melting titanium/superalloys, autoclave curing of composites, and machining are energy-intensive, but energy is a second-order cost line versus materials and labor. **[Inference]**
- **Logistics.** Just-in-time, single-source structures (e.g., Spirit AeroSystems shipping 737 fuselages by rail) mean transport disruptions or a single supplier's quality escape can halt final assembly — a recognized single point of failure (Spirit AeroSystems 10-K, FY2024 — https://www.sec.gov/Archives/edgar/data/1364885/000162828025009088/spr-20241231.htm).
- **Regulation as input.** Airworthiness regulation (FAA/EASA), export control (ITAR/EAR), and defense-acquisition rules (FAR/DFARS, CMMC cybersecurity) are non-optional inputs that set the cost of entry and the pace of change. Regulation both protects incumbents and gates capacity.

### 6. How a shock propagates

**[Inference]** A titanium shock is the canonical example. (1) A sponge/mill disruption (sanctions, a plant fire, a counterfeit-cert scandal) removes qualified metal. (2) Because re-qualification takes 12+ months, airframers and engine OEMs cannot substitute quickly; they draw down inventory and reprioritize. (3) Missing structural or hot-section parts stop **final assembly**, so the loss cascades to finished-unit deliveries — the industry's true output and cash trigger, since customers pay heavily on delivery. (4) Deliveries slip, revenue is deferred, penalty/parking-cost clauses bite, and the effect shows up as negative working-capital swings and margin catch-up charges quarters later. The same topology applies to a superalloy, casting (Precision Castparts is near-sole-source on many turbine castings), or Tier-1 structures shock: **the choke point is always the least-substitutable, hardest-to-qualify node feeding final assembly**, not the cheapest commodity.

**Which inputs cap capacity or set margins:** capacity is capped by (a) skilled/cleared labor and (b) qualified specialty-material and casting supply; margins are set by (c) the engine/aftermarket value split (captured by engine OEMs, not airframers) and (d) fixed-price development risk on defense programs, where input-cost and labor overruns fall on the contractor.

### 9. Full mission-system input and dependency ledger

Trace each platform through raw and processed materials: aluminum, titanium, nickel superalloys, specialty and electrical steels, copper, carbon fiber, glass fiber, resins, ceramics, rubber, fuels, energetic chemicals and rare-earth magnets. Those inputs depend on bauxite/alumina, titanium sponge, nickel/cobalt/chromium, iron ore or scrap, metallurgical coal, petrochemical precursors, graphite, mineral separation, high-purity processing, heat treatment and qualified mills. Castings, forgings, bearings, fasteners, wiring, connectors, printed circuit boards, semiconductors, sensors, optics, batteries, engines, avionics, landing gear, actuators and munitions energetics are the high-value intermediate chain.

Productive capacity also requires cleared engineers and software developers, machinists, welders, composite technicians, test pilots, quality inspectors, program security, certified tooling, clean rooms, wind tunnels, ranges, simulators, depots, airfields/shipyards and secure data infrastructure. Drawings, technical data rights, export classifications and customer-approved suppliers are inputs because an unqualified substitute cannot simply replace a constrained component.

Funding comes from annual public appropriations, multiyear procurement, foreign military sales, allied budgets, commercial airline orders, customer advances, corporate cash/debt/equity, private venture/growth capital and government-backed loans or industrial-base investments. Progress payments and cost reimbursement reduce contractor working capital on some programs; fixed-price development and inventory for rate increases can consume it.

Commodity prices influence cost, but qualification and long lead times dominate capacity: castings/forgings, rocket motors, solid propellant, seekers, microelectronics, submarine and shipyard capacity, skilled/cleared labor, test assets and sole-source tooling can gate output. Repair, cannibalization, additive manufacturing, life extension, commercial-off-the-shelf content and allies provide partial substitutes, constrained by airworthiness, configuration control, cybersecurity and export rules.

### Sources
- AeroTime, "The titanium supply chain crisis" (2022) — https://www.aerotime.aero/articles/32464-titanium-supply-crisis-what-does-this-mean-for-aerospace
- Aero Magazine, "Titanium grip by Russia, China threatens Western aerospace supply chains" (2024) — https://www.aero-mag.com/titanium-grip-by-russia-china-threatens-western-aerospace-supply-chains
- Global Growth Insights, "Titanium Sponge Market" (2024) — https://www.globalgrowthinsights.com/market-reports/titanium-sponge-market-104732
- SupplyChainBrain, "How Boeing's Counterfeit Titanium Crisis Was Predictable" (2024) — https://www.supplychainbrain.com/blogs/1-think-tank/post/40637-how-boeings-counterfeit-titanium-crisis-was-predictable-and-preventable
- Simple Flying, "Rolls-Royce vs Pratt & Whitney vs GE" (2024) — https://simpleflying.com/rolls-royce-pratt-whitney-ge-dominate-engine-market/
- AeroTime, "World's largest aircraft engine manufacturers" — https://www.aerotime.aero/articles/32417-who-are-the-world-s-largest-aircraft-engine-manufacturers
- AIA, "2025 Facts & Figures" (2025) — https://www.aia-aerospace.org/news/american-aerospace-defense-industry-continues-economic-dominance/
- Aerospace Manufacturing & Design, "Skilled Workforce Shortage" (2024) — https://www.aerospacemanufacturinganddesign.com/article/manufacturing-skilled-workforce-shortage--will-hamper-aerospace-s-take-off/
- Amtec, "U.S. Aerospace & Defense Workforce Data" (2026) — https://www.amtec.co/blog/aerospace-defense-workforce-report
- Economy Middle East, "Boeing reports net loss of $11.83 billion in 2024" (2025) — https://economymiddleeast.com/news/boeing-reports-net-loss-11-83-billion-2024-largest-since-2020/
- Spirit AeroSystems Form 10-K FY2024 (SEC EDGAR) — https://www.sec.gov/Archives/edgar/data/1364885/000162828025009088/spr-20241231.htm

## 3. Market Landscape


The industry is a set of deep, government-entangled oligopolies. At the top, two commercial airframers, four engine makers, and roughly five Western defense primes control the platforms; below them a long, fragile supplier tail; alongside them, an aftermarket that captures most of the lifetime profit. Value accrues wherever there is **sole-source proprietary content and a certified installed base**, and is competed away wherever a supplier is interchangeable.

### 1. Value-chain structure and where profit accrues

**Airframe OEMs (systems integrators).** Boeing and Airbus form a global duopoly in large commercial aircraft; other airframers (Embraer, COMAC, Bombardier/Textron in bizjets) sit in adjacent or smaller segments. Boeing's total 2024 revenue was $66.5 billion but it posted an $11.83 billion net loss, with Commercial Airplanes ($22.9B revenue, –$8.0B operating) and Defense/Space ($23.9B, –$5.4B) both loss-making while Global Services earned $3.6 billion (Boeing FY2024 — https://economymiddleeast.com/news/boeing-reports-net-loss-11-83-billion-2024-largest-since-2020/; segment detail via AeroTime — https://www.aerotime.aero/articles/boeing-results-q4-full-year-2024). **[Inference]** This split is the whole thesis: new-build integration is thin-to-negative margin; **services is where the money is**, even inside a struggling OEM.

**Engine OEMs — the profit pool.** CFM (GE + Safran) holds ~40–44% of the installed base and >60% of narrow-body engines; GE powers ~52% and Rolls-Royce ~33% of widebodies (Simple Flying/Statista, 2024 — https://simpleflying.com/rolls-royce-pratt-whitney-ge-dominate-engine-market/). GE Aerospace earns ~70% of revenue from aftermarket (see MECHANICS). Their moat: a certified engine locked to a platform for 30 years plus sole-source spare parts — the durable profit center of the whole industry. **[Inference]**

**Defense primes.** Lockheed Martin (2024 net sales $71.0B; segments Aeronautics $28.6B, RMS $17.3B, Space $12.5B, Missiles & Fire Control $12.7B; record $176B backlog; $5.3B FCF) leads; RTX, Northrop Grumman, General Dynamics, and Europe's BAE Systems round out the tier (Lockheed FY2024 — https://news.lockheedmartin.com/2025-01-28-Lockheed-Martin-Reports-Fourth-Quarter-and-Full-Year-2024-Financial-Results). Their moat is the certified/qualified platform, security clearances, and being the only qualified integrator for a given weapon — buyers cannot switch mid-program.

**Tier-1 structures & components.** Spirit AeroSystems (fuselages), Safran, GKN, Howmet. This tier is squeezed between powerful OEMs above and materials above that; margins are thinnest where content is build-to-print. Spirit's near-insolvency and re-acquisition by Boeing (with Airbus taking its work) shows how the OEMs re-internalize a failing single point of failure (Spirit 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/1364885/000162828025009088/spr-20241231.htm).

**Proprietary-component & aftermarket specialists — the hidden winners.** TransDigm and HEICO earn OEM-like margins because their parts are sole-source, IP-protected, and small-value-but-mission-critical, so buyers cannot economically re-qualify a substitute. **[Inference]** This is the same moat as the engine OEMs, applied to niche components.

**Value-accrual summary [Inference]:** profit pools sit at (1) engine aftermarket, (2) sole-source proprietary components, (3) sustainment/services on defense platforms. Profit is competed away in (a) commodity build-to-print structures, (b) new-build airframe integration, and (c) fixed-price development, where risk is dumped on the contractor.

### 2. Customers, suppliers, regulators

Customers are **airlines and lessors** (commercial) and **governments** (defense) — highly concentrated, sophisticated buyers with real leverage on new-build price, but locked into the aftermarket. Suppliers are the tiered base above. Regulators (FAA, EASA and equivalents for airworthiness; DoD/DCMA, DDTC/ITAR, BIS/EAR for defense and export) set the barriers to entry and the pace of change — and, in doing so, protect incumbents.

### 3. Geography, clusters, and why they exist

Civil final-assembly clusters concentrate in **Seattle/Everett (Boeing), Toulouse (Airbus), Montreal (Bombardier/aerospace ecosystem), and Wichita** — hub-and-spoke agglomerations where specialized suppliers, test infrastructure, and skilled labor co-locate around an anchor OEM (APEX — https://apex.aero/articles/aerospace-hubs/; Greater Wichita Partnership — https://greaterwichitapartnership.org/industry-selectors/aerospace). Wichita alone anchors 350+ suppliers. **[Inference]** These clusters persist because the tacit process knowledge, certified supplier networks, and skilled workforce are almost impossible to relocate — a structural moat for incumbent regions. The U.S. leads defense and engines; Europe (UK, France, Germany) holds Airbus, Rolls-Royce, Safran, BAE; Japan supplies critical materials and structures; China (COMAC, AVIC) is building a state-backed challenger.

### 4. Trade, subsidies, and industrial policy

The U.S. A&D industry generated over $995 billion in economic activity and $138.6 billion in exports in 2024 — one of the largest positive-trade-balance U.S. sectors (AIA, 2025 — https://www.aia-aerospace.org/news/american-aerospace-defense-industry-continues-economic-dominance/). Government money is structural, not incidental: the decades-long **Boeing–Airbus WTO dispute** (U.S. filed 2005; EU counterclaim) turned on U.S. R&D/tax support to Boeing versus EU "launch aid" to Airbus — both governments subsidize their champion (Opportunity Lost/Substack — https://opportunitylost.substack.com/p/planes-subsidies-and-trade-disputes). On defense, procurement budgets ARE the market. **[Inference]** Industrial policy is thus a first-order driver of who wins, not a footnote.

### 5. National-security considerations and demand

Global military expenditure hit **$2,718 billion in 2024, up 9.4%** — the steepest rise since at least 1988 — with the U.S. at $997 billion (37% of the world total) and the top-five spenders at 60% (SIPRI, 2025 — https://www.sipri.org/publications/2025/sipri-fact-sheets/trends-world-military-expenditure-2024). European and Middle East spending surged on the Ukraine war and regional conflict. **[Inference]** This is a durable, decade-plus demand tailwind for defense primes and munitions makers, and it explains the ~12x defense M&A multiples versus ~8x elsewhere (see MECHANICS). National-security logic also drives reshoring of titanium, castings, rare earths, and semiconductors (INPUTS) and keeps ~90% of technical jobs ITAR-locked.

### 6. What's gaining vs. losing relevance

**Gaining [Inference]:**
- **Aftermarket/services and digital sustainment** — recurring, high-margin, cycle-resistant; the clearest value-migration destination.
- **Munitions and air-and-missile defense** — Raytheon's 2024 bookings included $2.4B (Patriot, Germany), $1.9B (LTAMDS), $1.6B (SM-3) — restocking and Ukraine/Middle East demand (RTX 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/101829/000010182925000005/rtx-20241231.htm).
- **Uncrewed/autonomous systems and defense software** — drones, loitering munitions, autonomy, space/ISR; new entrants (Anduril, SpaceX/Starlink-class) attacking software-and-mass-production seams the primes are slow on. Increasingly valued on software multiples.
- **New space / reusable launch** — SpaceX's reusability collapsed launch cost and is displacing legacy expendable launch economics.

**Losing / at risk [Inference]:**
- **Pure commodity build-to-print structures** — margin-squeezed, disintermediated (Spirit's fate).
- **Expendable launch and legacy space primes** — losing share to reusable launch.
- **Boeing's commercial franchise position** — six straight years of Airbus delivery leadership and repeated quality/production crises have eroded a once-even duopoly (Flight Global, 2025 — https://www.flightglobal.com/airframers/boeings-2024-orders-and-deliveries-slipped-as-airbus-widened-edge/161372.article). Airbus's ~8,658-aircraft backlog vs Boeing's ~5,595 embeds years of relative advantage.

### 7. Disruption vectors and real vs. promotional progress

**Potential disruptors:** (1) COMAC/AVIC breaking the Boeing–Airbus duopoly with state backing — real over a long horizon, gated by engine dependence (still Western-engined) and certification. (2) Sustainable aviation — SAF, hydrogen, hybrid-electric; near-term SAF is real-but-supply-constrained, hydrogen/electric airliners are largely promotional on today's energy density. [Inference] (3) eVTOL/advanced air mobility — genuine flight-test progress at a few players, but most valuations rest on renders and non-binding LOIs; certification and unit economics are unproven. (4) Defense-tech software/autonomy — real and already winning contracts.

**How to tell real from promotional [Inference]:** weight flight-proven hardware, signed/funded contracts and backlog, passed certification milestones, and qualified supply chains; discount TAM slides, LOIs, and "disruption" narratives lacking a regulatory path. The industry's certification and qualification barriers mean **disruption is slow and capital-heavy** — the durable winners are those converting technical milestones into locked-in, sole-source, recurring aftermarket positions.

### 8. Where value is likely to migrate

**[Inference]** Away from new-build integration and commodity structures, toward: (1) engine and platform **aftermarket/sustainment**; (2) **sole-source proprietary content** (TransDigm/HEICO model); (3) **munitions and missile defense** on the rearmament cycle; (4) **autonomy, space, and defense software** valued on recurring-revenue multiples. Airframers and primes that own more services and IP-rich content, and fewer thin-margin build-to-print activities, capture the migrating value; those left holding integration and commodity fabrication see it compete away.

### 9. Complete output, customer, geography, capital, and legislation map

Outputs include aircraft, spacecraft, ships, ground vehicles, missiles, munitions, engines, sensors, communications, cyber/command systems and spares; equally important services include training, readiness, sustainment, upgrades, depot maintenance and mission data. Test articles, scrap composites, hazardous energetics, emissions and demilitarization/disposal are residual outputs. Availability and mission effect—not deliveries alone—are what end customers buy.

The buyer/payer/user chain is unusually split: legislatures appropriate, ministries/agencies contract, program offices specify, armed services operate, allies may purchase through government channels, and taxpayers fund. In commercial aerospace, airlines/lessors buy or finance while passengers and freight customers generate demand; regulators certify. This makes political, budget, mission and residual-value risk distinct.

Supply chains are global but controlled by sovereignty, alliance, export and security rules. US and European primes coordinate broad tiers; engine, avionics and structures clusters persist around certified talent and infrastructure. Defense localization, offsets and security-of-supply can duplicate capacity; commercial production follows global traffic and lessor capital. Prime concentration coexists with fragile lower tiers and sole sources.

Public funding dominates defense R&D and procurement; private capital funds dual-use startups, commercial space and supplier consolidation; export-credit and lessors support civil aircraft; strategic-capital programs can crowd private money into critical suppliers. Laws and rules cover appropriations/procurement, competition, cost accounting, cybersecurity, classified information, export controls, foreign investment, sanctions, domestic content, arms transfers, airworthiness/space licensing, environmental and weapons treaties.

The sector connects to airlines, satellites/telecom, semiconductors, shipbuilding, metals, energy, software/AI and sovereign credit. Conflict depletes inventory faster than annual production; commercial downcycles damage shared suppliers; export controls can protect security while shrinking supplier scale; civil technologies can migrate to defense and vice versa. Backlog must therefore be separated into funded, authorized, appropriated, contracted, executable and cancellable demand.

### Sources
- Boeing FY2024 net loss — Economy Middle East (2025) — https://economymiddleeast.com/news/boeing-reports-net-loss-11-83-billion-2024-largest-since-2020/
- AeroTime, "Boeing Q4 & full-year 2024 results" (2025) — https://www.aerotime.aero/articles/boeing-results-q4-full-year-2024
- Simple Flying, "Rolls-Royce vs P&W vs GE" (2024) — https://simpleflying.com/rolls-royce-pratt-whitney-ge-dominate-engine-market/
- Lockheed Martin FY2024 Financial Results (2025) — https://news.lockheedmartin.com/2025-01-28-Lockheed-Martin-Reports-Fourth-Quarter-and-Full-Year-2024-Financial-Results
- Spirit AeroSystems Form 10-K FY2024 (SEC EDGAR) — https://www.sec.gov/Archives/edgar/data/1364885/000162828025009088/spr-20241231.htm
- APEX, "World's Leading Aerospace Hubs" — https://apex.aero/articles/aerospace-hubs/
- Greater Wichita Partnership, "Aerospace Industry Overview" — https://greaterwichitapartnership.org/industry-selectors/aerospace
- AIA, "2025 Facts & Figures" (2025) — https://www.aia-aerospace.org/news/american-aerospace-defense-industry-continues-economic-dominance/
- Opportunity Lost, "Planes, Subsidies, and Trade Disputes" — https://opportunitylost.substack.com/p/planes-subsidies-and-trade-disputes
- SIPRI, "Trends in World Military Expenditure, 2024" (2025) — https://www.sipri.org/publications/2025/sipri-fact-sheets/trends-world-military-expenditure-2024
- RTX Corp Form 10-K FY2024 (SEC EDGAR) — https://www.sec.gov/Archives/edgar/data/101829/000010182925000005/rtx-20241231.htm
- Flight Global, "Boeing's 2024 orders and deliveries slipped" (2025) — https://www.flightglobal.com/airframers/boeings-2024-orders-and-deliveries-slipped-as-airbus-widened-edge/161372.article

## 4. Operating Mechanics


The industry sells two very different things: **long-lived capital equipment** (aircraft, engines, satellites, weapons) and, more profitably, the **decades of mandated sustainment** that equipment generates. Understanding the economics means separating the loss-leading "razor" from the high-margin "blades," and understanding how program accounting turns multi-decade contracts into reported earnings.

### 1. The production workflow

**Commercial airframe (illustrative).** (1) Design & certification — clean-sheet programs cost tens of billions and take ~5–10 years to a type certificate. (2) Tiered supply — the OEM (Boeing/Airbus) is a **systems integrator**; Tier-1s build major sections (Spirit AeroSystems fuselages, Safran/Collins landing gear and avionics, engine OEMs), Tier-2/3s make parts and materials. (3) Final assembly line (FAL) — sections are joined, engines and systems installed, at a metered takt rate. (4) Ground/flight test and airworthiness sign-off. (5) Delivery — the cash event: customers pay pre-delivery deposits during the build but the bulk of the price lands at delivery. (6) In-service sustainment — parts, MRO, upgrades for 20–30+ years. Airbus delivered 766 aircraft in 2024 versus Boeing's 348, the sixth straight year Airbus led, as Boeing worked through a manufacturing/quality crisis (Flight Global, 2025 — https://www.flightglobal.com/airframers/boeings-2024-orders-and-deliveries-slipped-as-airbus-widened-edge/161372.article).

**Defense.** Similar integration structure but the customer (a government) funds development via cost-plus or fixed-price contracts, buys in "lots" (e.g., F-35 Lots 18–19), and drives multi-decade sustainment. Lockheed delivered 110 F-35s in 2024 (Lockheed Martin FY2024 results — https://news.lockheedmartin.com/2025-01-28-Lockheed-Martin-Reports-Fourth-Quarter-and-Full-Year-2024-Financial-Results).

### 2. Competing methods and the real trade-offs

- **Composites vs. aluminum airframes.** Carbon-fiber (Boeing 787, Airbus A350) cuts weight and fatigue, enabling longer range and lower fuel burn, but requires expensive autoclave/automated-fiber-placement tooling and is hard to inspect and repair. Aluminum is cheaper, faster to build, and easily repaired. **Composites win on long-haul widebodies where fuel savings over a 20-year life dominate; aluminum still wins on shorter-life, cost-sensitive, high-rate narrow-bodies.** [Inference]
- **Geared turbofan (Pratt & Whitney GTF) vs. direct-drive (CFM LEAP).** The GTF's reduction gearbox lets fan and turbine spin at optimal speeds for better fuel efficiency, but added early-life durability problems (powder-metal disk issues) causing costly fleet inspections; the LEAP is a more conventional, arguably more robust architecture. **The trade is theoretical efficiency vs. maturity/reliability risk** — airlines split their fleets partly to hedge it. [Inference]
- **Cost-plus vs. fixed-price contracting.** Cost-plus shifts overrun risk to the government and suits R&D-heavy development; fixed-price caps government cost but dumps overrun risk on the contractor — the mechanism behind Boeing's $5.4 billion 2024 defense loss on fixed-price development programs (KC-46, T-7, Starliner) (Boeing FY2024 via AeroTime — https://www.aerotime.aero/articles/boeing-results-q4-full-year-2024). **[Inference]** This is why primes now resist firm fixed-price development.

### 3. Asset types and their economics

- **Airframers (Boeing BCA, Airbus):** high fixed cost, steep learning curve, thin new-build margins; value is the certified type design and order backlog.
- **Engine OEMs (GE Aerospace, RTX/P&W, Rolls-Royce, Safran):** the best model in the industry — sell the engine near breakeven, earn for 30 years on parts and service.
- **Defense primes (Lockheed, RTX, Northrop, General Dynamics, BAE):** program-based, backlog-visible, moderate but stable margins, government-funded capex.
- **Tier-1 suppliers & MRO (Spirit, Howmet, TransDigm, HEICO):** proprietary-part suppliers can earn OEM-like aftermarket margins; commodity build-to-print suppliers are margin-thin.

### 4. Unit economics and the cost stack

A new commercial engine or airframe is often sold at low or negative margin to win a **20–30 year installed-base position**; the OEM then earns "multiples of that" on proprietary spare parts and service, where aftermarket operating margins average ~2.5x new-build margins for industrial OEMs and can reach 40–60%+ on sole-source parts (IB Interview Questions primer — https://ibinterviewquestions.com/guides/industrials-investment-banking/engine-oems-aftermarket-mro-business-model). The clearest data point: **GE Aerospace derived roughly 70% of revenue from aftermarket parts and services** on ~$45.9 billion FY2025 revenue [Fact, fiscal-2025 figure] (per industry reporting summarized in the same primer). Engines are the dominant MRO driver, forecast toward ~53% of the whole aftermarket by the mid-2030s [Estimate] (Umbrex MRO primer — https://umbrex.com/resources/industry-primers/aerospace-defense-industry-primers/aerospace-mro-aftermarket-services-industry-primer/).

The marginal-unit cost stack is dominated by **bought-in systems and materials** (engines, avionics, structures — often >60% of an airframe's cost) plus touch labor; the OEM's own value-add is integration, test, and certification. Because much cost is bought-in and labor is scarce, **the learning curve** (unit cost falling ~10–15% per doubling of cumulative output) is the central economic engine of a program — early units lose money, later units on a mature line print cash. [Inference]

### 5. KPIs practitioners actually track

- **Book-to-bill** (orders ÷ deliveries) — >1 signals backlog growth. The global aircraft backlog reached ~14 years of production at 2024 delivery rates (CAPA, 2025 — https://centreforaviation.com/analysis/reports/global-aircraft-order-backlog-another-new-record-at-14-years-airbus-outsells-boeing-again-707386).
- **Backlog** — Lockheed carried a record $176.0 billion at end-2024; RTX defense backlog rose to $63 billion from $52 billion (Lockheed FY2024 — URL above; RTX 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/101829/000010182925000005/rtx-20241231.htm).
- **Free cash flow** — the honest earnings metric given program accounting; Lockheed generated $5.3 billion FCF in 2024 (Lockheed FY2024 — URL above).
- **Deliveries and production rate** (e.g., 737 monthly rate), **segment operating margin**, **cumulative catch-up (cum) adjustments** on long-term contracts, **aftermarket/OE revenue mix**, **flight hours / shop visits** driving MRO demand.
- **Program margin (EAC)** — estimate-at-completion booking rates on long-duration contracts; a slip triggers a "reach-forward loss."

### 6. Development timelines and characteristic failure points

Clean-sheet aircraft: ~5–10 years and $10–30 billion; engines similar; both then run 20–40 years in service. **Failure points:** (1) fixed-price development overruns (Boeing KC-46/Starliner); (2) new-engine durability escapes (P&W GTF, RR Trent 1000) that ground fleets and blow up warranty/AOG costs; (3) single-source supplier quality escapes halting final assembly (Spirit); (4) certification delays; (5) demand cyclicality on the commercial side colliding with fixed cost.

### 7. Valuation across company life-stages

**(a) Mature, cash-generative businesses (engine OEMs, aftermarket specialists, defense primes).** Value on **free cash flow and EV/EBITDA**, because program accounting distorts GAAP earnings. Sector EV/EBITDA averaged ~11.8x in Q2 2024 (down 17.8%), with a 12.5x median and an 8.3x–33.3x range across names; defense M&A cleared ~12x vs ~8x for other subsectors (First Page Sage / Objective, 2024 — https://firstpagesage.com/business/aerospace-ebitda-valuation-multiples/; https://www.objectiveibv.com/wp-content/uploads/2024/07/Objective-Aerospace-Defense-Industry-Report-Q2-2024-1.pdf). By early 2026 the listed group traded richer — ~20.6x EV/EBITDA, 2.1x sales, ~2.9% FCF yield, 6.8x book (CSIMarket, Q1 2026 — https://csimarket.com/Industry/industry_valuation_ttm.php?ind=201). **[Inference]** Aftermarket-heavy names (TransDigm, HEICO, GE Aerospace) command premium multiples because their cash flows are recurring and margin-rich; pure new-build airframers get lower multiples. Also watch **P/FCF**, **backlog coverage (backlog ÷ revenue)**, and dividend/buyback capacity.

**(b) Cyclical, asset-heavy businesses (commercial airframers, structures suppliers).** Value **across the cycle**, not on a single year. Use **mid-cycle margins / normalized EBIT**, **EV/EBITDA on normalized numbers**, and cash conversion through the trough (Boeing's negative 2024 shows why trailing GAAP is misleading — Economy Middle East, 2025 — https://economymiddleeast.com/news/boeing-reports-net-loss-11-83-billion-2024-largest-since-2020/). Key inputs: **backlog and delivery ramp** (Airbus ~8,658 vs Boeing ~5,595 aircraft backlog end-2024 — Flight Global, URL above), production-rate trajectory, working-capital swings, and program cash breakeven. Sum-of-the-parts is common because a conglomerate's aftermarket/services arm deserves a higher multiple than its OE arm. **[Inference]**

**(c) Pre-revenue / early-stage (new-space launchers, eVTOL/advanced-air-mobility, defense-tech startups).** No earnings to capitalize, so value rests on **probability-adjusted milestones**: certified/qualified IP, secured launch or production contracts and backlog, technical milestones passed (successful flight test, engine qualification), addressable capacity/order pipeline, and government funding awarded. Methods: **risk-adjusted (rNPV) DCF** with milestone probability weights, **EV/backlog or EV/order-book**, comparable **funding-round or SPAC-implied multiples**, and real-options framing for optionality (a certification is a call option on a market). **[Inference]** The analyst's job here is to separate **real technical progress** (flight-proven hardware, signed offtake, regulatory path) from **promotional claims** (renders, non-binding LOIs, TAM slides) — see LANDSCAPE. Defense-tech (autonomy, drones, software) is increasingly valued on **software/SaaS-like multiples (EV/revenue)** when recurring, which is a genuine multiple-expansion lever versus hardware primes.

### 9. Complete program, contract, and cash mechanics

The lifecycle is requirement and budget → technology maturation → competition and award → design/development → qualification/test and certification → tooling and low-rate production → rate ramp → delivery/acceptance → training and sustainment → upgrade → retirement/demilitarization. Cost and schedule risk fall slowly because design changes propagate through software, tooling, suppliers, tests and certification.

Contract mechanics include cost-plus, fixed-price incentive, firm-fixed-price, time-and-material, IDIQ/task order, service/performance-based logistics and commercial sale/lease. Revenue recognition by cost-to-cost can precede delivery and cash; estimates-at-completion changes create catch-up gains or charges. Progress payments, advances, milestone billing, retainage, inventory, unbilled receivables and supplier financing explain cash conversion. A loss-making fixed-price development program can generate accounting revenue while consuming cash for years.

Capacity is configuration-specific. Track qualified supplier output, engineering releases, shipsets, learning curve, takt time, rework, yield, shortages, engine availability, flight/test capacity and customer acceptance. Sustainment economics depend on installed base, utilization, spares provisioning, repair turnaround, intellectual-property rights and readiness incentives. Maintenance and industrial-base capex must be separated from program-funded tooling and growth capacity.

Minimum KPIs include funded and unfunded backlog, book-to-bill, backlog burn, deliveries, program margin and EAC changes, cash conversion, supplier advances, R&D mix, unit cost, schedule variance, quality escapes, rework, readiness, spares fill and aftermarket share. Stress appropriation delay, continuing resolution, fixed-price overrun, production-rate change, sole-source loss, export-license delay, customer acceptance, inflation, commercial-air downturn and conflict-driven surge.

### Sources
- Flight Global, "Boeing's 2024 orders and deliveries slipped as Airbus widened edge" (2025) — https://www.flightglobal.com/airframers/boeings-2024-orders-and-deliveries-slipped-as-airbus-widened-edge/161372.article
- Lockheed Martin, Q4/FY2024 Financial Results (2025) — https://news.lockheedmartin.com/2025-01-28-Lockheed-Martin-Reports-Fourth-Quarter-and-Full-Year-2024-Financial-Results
- AeroTime, "Boeing Q4 & full-year 2024 results" (2025) — https://www.aerotime.aero/articles/boeing-results-q4-full-year-2024
- IB Interview Questions, "Engine OEMs and the Aftermarket MRO Business Model" — https://ibinterviewquestions.com/guides/industrials-investment-banking/engine-oems-aftermarket-mro-business-model
- Umbrex, "Aerospace MRO & Aftermarket Services Industry Primer" — https://umbrex.com/resources/industry-primers/aerospace-defense-industry-primers/aerospace-mro-aftermarket-services-industry-primer/
- CAPA, "Global aircraft order backlog: another new record at 14 years" (2025) — https://centreforaviation.com/analysis/reports/global-aircraft-order-backlog-another-new-record-at-14-years-airbus-outsells-boeing-again-707386
- RTX Corp Form 10-K FY2024 (SEC EDGAR) — https://www.sec.gov/Archives/edgar/data/101829/000010182925000005/rtx-20241231.htm
- First Page Sage, "Aerospace EBITDA & Valuation Multiples 2025" — https://firstpagesage.com/business/aerospace-ebitda-valuation-multiples/
- Objective, "Aerospace & Defense Industry Report Q2 2024" — https://www.objectiveibv.com/wp-content/uploads/2024/07/Objective-Aerospace-Defense-Industry-Report-Q2-2024-1.pdf
- CSIMarket, "Aerospace & Defense Industry Valuation Q1 2026" — https://csimarket.com/Industry/industry_valuation_ttm.php?ind=201
- Economy Middle East, "Boeing reports net loss of $11.83 billion in 2024" (2025) — https://economymiddleeast.com/news/boeing-reports-net-loss-11-83-billion-2024-largest-since-2020/

## 5. Economics and Valuation


Benchmark bands are diagnostic starting points; refresh for product, asset, geography, contract, and cycle.

### Core unit-economic identity

Program margin = contract revenue recognized − supplier, labor, overhead, test, warranty and estimated remaining cost. Cash = billings/progress payments/advances − inventory, development, supplier support, capex and customer acceptance timing.

### Ten benchmark measures

| Measure | Diagnostic band or unit | Decision use |
| --- | --- | --- |
| Commercial aircraft lead | years from order to delivery in tight markets | Backlog duration and cancellation |
| Production learning | unit labor/cost declines with cumulative output | Rate economics |
| Engine shop interval | flight cycles/hours by engine and mission | Aftermarket timing |
| Book-to-bill | orders or awards divided by revenue | Backlog direction |
| Funded backlog cover | years of revenue | Visibility |
| Cash conversion | operating cash relative to earnings | Program and payment quality |
| R&D intensity | percent of sales, customer versus company funded | Future platform burden |
| Fixed-price development exposure | remaining cost and EAC range | Loss risk |
| Supplier lead time | months/years for forgings, engines, electronics | Rate bottleneck |
| Readiness/service level | availability, fill, turnaround | Outcome value |

### Accounting-to-cash bridge

Percentage-of-completion estimates, EAC revisions, progress payments, advances, customer-funded R&D/tooling, inventory, supplier advances, pension and warranty require reconciliation. Backlog is not GAAP revenue and civil concessions can be acquisition cost.

### Highest-value sensitivities

- Production rate, engine/forging/electronics availability, learning, rework and quality.
- Appropriation, continuing resolution, program milestone, export approval and customer mix.
- Airline traffic/credit, lessor finance, residual value and aftermarket utilization.
- Inflation clauses, fixed-price design change, strike, cybersecurity and test failure.

### Valuation discipline

Use program/segment sum-of-parts: civil OE, aftermarket, defense production, services and development options. Normalize EAC charges and working capital; do not capitalize unfunded political aspirations.


## 6. Regulation and Public Funding


Snapshot reviewed through **2026-07-14**. Verify enacted text, implementation dates, litigation, and current guidance.

### Permission chain

Legislature funds; ministry/agency/program office procures; prime integrates; tiers supply; regulator/customer certifies; service operates; depot/MRO sustains; ally/export authority controls transfer; lessor/bank finances civil assets.

### Jurisdiction and regime map

| Jurisdiction or layer | Core regimes and authorities | Economic transmission |
| --- | --- | --- |
| United States defense | Federal Acquisition Regulation/DFARS, appropriations, ITAR/EAR, CMMC/security, cost accounting | Contract type, data rights, domestic content, export and cyber |
| Civil aviation and space | FAA and international certification, launch/reentry, spectrum and safety | Time to market, grounding and operating permissions |
| Allied and European defense | National procurement, EU/NATO frameworks, offsets/local content and export controls | Industrial workshare and market access |
| International arms and investment | Arms-transfer regimes, sanctions, foreign investment and classified handling | Customer eligibility, ownership and supply chain |

### Public and private funding

Public funding dominates defense R&D, procurement, stockpiles, infrastructure and foreign military sales. Private funding includes civil customer advances, corporate markets, lessors/export credit, supplier finance and venture/growth capital for space and dual-use firms.

### Enforcement and liability

Debarment, False Claims exposure, cost disallowance, export penalties, security clearance loss, grounding, stop-work, warranty and product liability can eliminate a program or supplier.

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
| 787 development and battery issues | New materials, global outsourcing and systems integration increased complexity | Delay, rework and grounding raised cost | Risk transfer does not remove integration risk |
| F-35 concurrency | Production began while testing/design continued | Retrofit and EAC burden rose | Schedule acceleration can move cost downstream |
| 737 MAX grounding | Design/certification and safety failures stopped a global fleet | Cash, inventory, liability and trust effects persisted | Certification and safety are balance-sheet assets |
| Post-2022 munitions demand | Inventory draw and allied orders met limited energetic/motor/test capacity | Lead times exposed lower-tier bottlenecks | Funded demand cannot instantly create qualified capacity |
| Commercial aerospace pandemic shock | Traffic and airline finance collapsed abruptly | Rates fell, suppliers lost skills, recovery faced shortages | Shared supply chains transmit demand whiplash |

### Practitioner extraction

- **Leading signals:** Appropriations, budget documents, awards, book-to-bill, rates, supplier lead times, quality, flight hours, shop visits, and readiness.
- **Evidence that breaks the easy thesis:** Backlog lacking funding, rate plans unsupported by engines/shipsets, or margin improvement driven by favorable EAC without cash.
- **Durable lesson:** Aerospace output is a certified configuration and accepted mission capability—not an assembled unit.


## 8. Data Sources and Monitoring Dashboard


Preserve observation period, unit, definition, geography, and revision vintage.

### Primary source map

| Source | Cadence | Best use | Caveat |
| --- | --- | --- | --- |
| [US DoD budget materials](https://comptroller.defense.gov/Budget-Materials/) | annual and supplemental | Program funding and priorities | Request differs from enacted appropriation |
| [USASpending](https://www.usaspending.gov/) | frequent | Awards, obligations and recipients | Contract modifications and timing |
| [FAA aerospace data](https://www.faa.gov/data_research) | monthly to annual | Traffic, fleet, safety and forecasts | Jurisdiction and revisions |
| [SEC EDGAR filings](https://www.sec.gov/edgar/search/) | quarterly and annual | Backlog, program charges, cash and rates | Company definitions |
| [SAM.gov](https://sam.gov/) | continuous | Solicitations and award notices | Pipeline is not revenue |

### Indicator stack

- **Leading:** budgets; RFPs; orders; supplier POs; rate plans; flight hours.
- **Coincident:** deliveries; shipsets; awards; revenue; quality; shop visits.
- **Lagging:** readiness; EAC; cash conversion; claims; fleet retirement.

### Minimum dashboard

1. **Commercial aircraft lead** — years from order to delivery in tight markets; Backlog duration and cancellation.
2. **Production learning** — unit labor/cost declines with cumulative output; Rate economics.
3. **Engine shop interval** — flight cycles/hours by engine and mission; Aftermarket timing.
4. **Book-to-bill** — orders or awards divided by revenue; Backlog direction.
5. **Funded backlog cover** — years of revenue; Visibility.
6. **Cash conversion** — operating cash relative to earnings; Program and payment quality.
7. **R&D intensity** — percent of sales, customer versus company funded; Future platform burden.
8. **Fixed-price development exposure** — remaining cost and EAC range; Loss risk.
9. **Supplier lead time** — months/years for forgings, engines, electronics; Rate bottleneck.
10. **Readiness/service level** — availability, fill, turnaround; Outcome value.

### Normalization rules

- Map budget request to authorization, appropriation, obligation and outlay.
- Use funded executable backlog.
- Separate OE deliveries from aftermarket utilization.
- Normalize EAC and customer advances.

### Evidence traps

- Treating budget headlines as contracted revenue.
- Ignoring lower-tier qualification.
- Using unit deliveries without configuration/margin.

## 9. Geographic Operating Models

Geography changes ownership, contracting, cost, funding, regulation and risk; compare like with like.

| Geography / archetype | Operating model | Economic and risk implications |
| --- | --- | --- |
| United States | Large defense primes under federal cost-plus/fixed-price programs plus globally dominant commercial aerospace and suppliers | Budget appropriations, certification, export controls, program accounting and customer advances shape cash |
| European Union and United Kingdom | National champions and multinational programs with launch aid, workshare and government procurement | Cross-border governance, sovereign budgets and industrial participation complicate execution |
| China and Russia | State-directed civil/defense ecosystems pursuing domestic supply chains | Technology controls, captive demand and state funding segment competition |
| Middle East and Asia-Pacific importers | Sovereign procurement, offsets, local assembly and long-term sustainment packages | Geopolitics, financing, training, availability guarantees and local content determine awards |
| Global commercial aviation hubs | Airframers, engine OEMs, lessors, airlines and MRO networks linked by certification | Travel demand matters, but engine/shop capacity and supplier quality often set deliveries |

## 10. Cross-Industry Dependency Map

| Dependency class | Linked markets and institutions | Transmission into this industry |
| --- | --- | --- |
| Critical materials/components | Titanium, aluminum, nickel alloys, composites, forgings, castings, semiconductors, sensors and explosives | Qualification and single-source parts make low-value components schedule-critical |
| Government demand | Defense budgets, appropriations, foreign military sales, space agencies and security alliances | Political authorization must become funded backlog before production economics improve |
| Commercial demand | Airlines, lessors, cargo, business aviation and passenger travel | Traffic, airline balance sheets and lease rates determine delivery and aftermarket pull |
| Certification and sustainment | Aviation authorities, test infrastructure, MRO, spare parts and technical data | Groundings or shop bottlenecks shift value from new units to availability and support |
| Capital and risk transfer | Customer advances, progress payments, export credit, supplier finance, insurance and pensions | Milestone terms and fixed-price risk can invert accounting profit and cash |

The practical test is to trace a shock through availability, delivered cost, working capital, output, customer economics, financing and eventual substitution—not merely name the adjacent market.

## 11. Decision-Grade Unit Economics

> The numerical example below is illustrative, not a current market forecast or universal benchmark. Replace every assumption with asset-, contract-, product- and geography-specific evidence.

**Representative unit:** One narrow-body commercial aircraft delivery, excluding lifetime aftermarket.

**Core equation:** `Delivery contribution = contractual net price − engines/structures/systems − direct labor − warranty − delivery cost − allocated recurring program overhead`

| Bridge item | Illustrative assumption and calculation | Result / interpretation |
| --- | --- | --- |
| Net delivery revenue | Illustrative price after customer discounts and escalation | $65m |
| Purchased content | Engines, avionics, aerostructures, interiors and systems | $30m |
| Direct labor and factory conversion | Assembly, test, rework and quality | $10m |
| Warranty and delivery | Provision, flight/customer acceptance and logistics | $3m |
| Recurring program overhead | Engineering support, tooling upkeep and production overhead | $8m |
| Illustrative delivery contribution | $65m − $30m − $10m − $3m − $8m | $14m before nonrecurring development, abnormal cost and working-capital unwind |

**Decision test:** Compare mature-unit recurring contribution with remaining learning, concessions, advances, inventory and development recovery; a profitable delivery can still consume cash.

## 12. Industry Balance and Marginal Economics

| Balance concept | Industry-specific definition | What to measure |
| --- | --- | --- |
| Marginal supply unit | Last certified production slot, engine shop visit or qualified supplier capacity needed for demand | Bottlenecks are program- and part-specific, not measured by factory floor alone |
| Marginal customer | Airline/lessor deferring a delivery or government reallocating procurement | Financing, mission need and fleet commonality determine willingness to pay |
| Clearing mechanism | Negotiated multiyear contracts, escalation formulas, tenders and delivery slots | List price and headline backlog do not clear the market |
| Cash shutdown point | Programs continue below current unit cost when cancellation, strategic or learning value exceeds incremental loss | Contract and sovereign obligations override simple closure math |
| New-capacity incentive | Funded backlog and durable rate support tooling, supplier capital and skilled labor with adequate risk return | Qualification lead time makes customer commitments essential |
| Adjustment lag | Months for shifts/overtime, years for certified suppliers, engines, aircraft and defense programs | Backlog conversion depends on the slowest qualified node |

## 13. Terminology and Comparability Traps

| Reported term | Common but invalid interpretation | Required normalization |
| --- | --- | --- |
| Backlog | Firm, funded and profitable revenue | Separate options, unfunded awards, cancellations, escalation, customer credit and cost-to-complete |
| Book-to-bill | Demand strength across programs | Adjust for lumpy awards, duration, mix and funded status |
| Deliveries | Cash generation | Bridge advances, inventory, milestone payments, concessions and receivables |
| Program margin | Current unit margin | Identify program accounting block, learning assumptions and forward-loss provisions |
| Installed base | Addressable aftermarket | Adjust for utilization, warranty, shop intervals, contractual coverage and retirements |


