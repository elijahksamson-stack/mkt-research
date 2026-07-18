# Interactive Media & Internet Services

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

Search, social, online video, marketplaces, creator platforms, maps, messaging, app/platform ecosystems and ad-supported or transaction-funded internet services.

### Operating taxonomy

| Segment | What is sold | Primary unit | Do not aggregate without |
| --- | --- | --- | --- |
| Search and discovery | Queries, ranking, ads and referral | queries, users, clicks, revenue | Intent, default/distribution, TAC, vertical and AI answer |
| Social and creator media | Feeds, video, messaging and creator monetization | DAU/MAU, time, content, ads | Network, geography, age, format, moderation and payout |
| Marketplaces and local platforms | Buyer-seller matching, listings and transactions | GMV, orders, take rate | Category, geography, owned/agent, liquidity and fulfillment |
| App/developer platforms | Stores, identity, APIs and ecosystem services | developers, apps, transactions | Rule, take, distribution, review and competition |
| AI assistants and internet utilities | Generative answers, agents, maps and productivity services | queries, tokens, tasks, conversion | Model, data, source rights, compute, accuracy and workflow |

### Specifications that change value

- Users need DAU/MAU, cohort, geography, logged-in, age, paid/free and bot filtering.
- Engagement needs time/query/content/transaction and denominator; more is not always better.
- Ads need load, impressions, price, click/conversion, attribution, TAC and invalid traffic.
- Marketplace needs GMV, net revenue, take, refund/chargeback, seller payout and fulfillment.
- AI needs task success, hallucination/safety, latency, tokens/compute, source rights and human review.

### Role map

User supplies attention/data/content; creator/publisher/merchant/developer supplies complements; platform ranks/distributes; advertiser/merchant/subscriber pays; cloud/chip/payment supports; moderator/regulator controls; end user receives.

### Terms that must be explicit

- registered, MAU, DAU and paying user
- GMV/gross bookings versus revenue
- take rate versus contribution
- traffic-acquisition cost and distribution share
- engagement versus welfare and monetization


## 2. Inputs and Dependencies


**Scope.** GICS sub-industry "Interactive Media & Services": companies that create/distribute content and information through proprietary platforms and monetize primarily via pay-per-click advertising — search engines, social/networking platforms, online classifieds, and review/dating sites (MSCI GICS methodology, 2023 — https://www.msci.com/indexes/documents/methodology/1_MSCI_Global_Industry_Classification_Standard_GICS_Methodology_20240801.pdf). Representative constituents: Alphabet, Meta, Tencent, Baidu, Naver/Kakao, Pinterest, Snap, Reddit, Match Group. Unlike a manufacturer, this industry's "raw materials" are user attention, data, compute, and engineering talent. The dominant business input is **advertiser demand**, and the dominant physical constraint is now **compute and the power to run it**.

### 1. The core "raw material": user attention and data
The industry's saleable good is targeted access to human attention, inventoried as ad impressions. **[Fact]** U.S. internet ad revenue reached $258.6B in 2024, +15% YoY, with search $102.9B, social $88.7B, video $62.1B, display $74.3B (IAB/PwC, 2025 — https://www.iab.com/wp-content/uploads/2025/04/IAB_PwC-Internet-Ad-Revenue-Report-Full-Year-2024.pdf). Attention is self-generated (users produce both the content and the audience), so the "input cost" is really the cost of acquiring/retaining users plus the R&D to keep them engaged. **[Inference]** This is why the industry has near-zero marginal cost of goods and unusually high gross margins — the raw material is contributed free by users, and the marginal impression costs only the compute to serve it.

### 2. Compute: GPUs, custom silicon, servers
The largest and fastest-growing capital input is AI/ML compute for ranking, recommendation, ad auctions, and generative features. **[Estimate]** Nvidia holds ~80–90% of the AI accelerator market by revenue (Silicon Analysts, 2025 — https://siliconanalysts.com/analysis/nvidia-ai-accelerator-market-share-2024-2026). **[Fact]** Meta's 2024 capex was ~$37–39B, "predominantly for data centers and technical infrastructure to support AI" (Meta Q4 2024 release / 10-K summary — https://www.libertify.com/interactive-library/meta-platforms-10k-2024/). **[Estimate]** Alphabet 2024 capex ~$52B, guided to ~$75B in 2025 (Alphabet Q4 2024 earnings release — https://fortune.com/company-assets/1500/quartr/earnings-release-8-k-d7d50-2025-02-04-09-12-03.pdf).

**Bottleneck / single point of failure:** TSMC advanced packaging (CoWoS) and HBM memory. **[Estimate]** CoWoS capacity has been reported sold out through 2026, with Nvidia securing the majority of CoWoS-L capacity and H100/H200 lead times of 36–52 weeks (Silicon Analysts, 2025 — same URL). **[Inference]** Pricing power here sits firmly *upstream* (Nvidia, TSMC, SK Hynix/Micron for HBM), not with the platforms. The counter-move is vertical integration into custom ASICs — Google TPUs, Meta MTIA. **[Estimate]** ASICs are projected to reach ~45% of CoWoS-based AI accelerator shipments by 2026, up from 20–30% in 2024 (industry estimates, 2025 — same URL). **[Inference]** Custom silicon is the industry's principal lever to reclaim margin and secure supply; it substitutes captive design + TSMC fab access for merchant-GPU dependence, but does not remove the TSMC/HBM chokepoint.

### 3. Energy and physical data-center infrastructure
Compute is useless without power and cooling. **[Fact]** U.S. data centers consumed ~176 TWh in 2023 (~4.4% of U.S. electricity) and are projected at 325–580 TWh by 2028 (6.7–12% of U.S. electricity) (Lawrence Berkeley National Laboratory, Dec 2024 — https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf). **[Inference]** Power availability — grid interconnection queues, transformer/turbine lead times, local generation — is becoming the binding constraint on how fast the industry can add capacity, arguably ahead of chips. This creates a new upstream dependency on utilities, gas turbines, nuclear (SMRs, PPAs), and land near substations. Pricing power on electricity sits with utilities/regulators; platforms respond with long-term PPAs and self-generation. Cooling water and specialized equipment (liquid cooling, switchgear, gensets) are secondary bottlenecks with multi-quarter lead times [inference].

### 4. Labor
Three distinct pools with very different economics:
- **Elite engineering / ML research.** Scarce and expensive. **[Fact]** Median SWE total comp ~$387K at Meta and ~$308K at Google (Levels.fyi, 2024/2025 — https://www.levels.fyi/companies/meta/salaries/software-engineer). Top AI researchers command far more via equity/retention [estimate]. This input most directly determines product quality and thus engagement. Pricing power sits with the talent for the top tier; below it, the 2022–2023 layoffs show platforms regained leverage over generalist engineering labor [inference].
- **Content moderation / data labeling.** Cheap, outsourced, ethically fraught. **[Fact]** Outsourced Meta moderators in Nairobi (via Sama) were reportedly paid as little as ~$1.50/hour; 81% of a cohort were diagnosed with severe psychological disorders per court filings (TIME 2022; LSE 2025 — https://time.com/6147458/facebook-africa-content-moderation-employee-treatment/ , https://blogs.lse.ac.uk/africaatlse/2025/11/03/there-is-a-dark-side-to-content-moderation-in-east-africa/). **[Inference]** A small cost line but a large legal/reputational liability; AI classifiers are steadily substituting for it.
- **Sales / operations.** Direct-response advertising is largely self-serve (automated), so sales headcount scales sublinearly with revenue — a structural margin advantage over legacy media [inference].

### 5. Traffic acquisition and distribution (a paid input unique to search)
To reach users, search platforms pay device makers and browsers for default placement. **[Fact]** Alphabet's Search & Network traffic acquisition costs (TAC) were ~$51B in 2024; Google pays Apple ~36% of Safari search revenue, estimated at ~$20B+/year (Pichai testimony via CNBC, 2023 — https://www.cnbc.com/2023/11/14/google-pays-apple-36percent-of-safari-search-revenue-sundar-pichai.html). **[Inference]** TAC is simultaneously Alphabet's largest single cost of distribution and the mechanism a court found anticompetitive. Apple holds real pricing power because it controls the default slot on 1B+ iPhones. The August 2024 *U.S. v. Google* liability ruling and 2025 remedies (1-year default contracts, no tying, data-sharing with "qualified competitors") threaten to reprice or unwind this input (Mehta ruling 2024; remedies 2025 — https://www.goodwinlaw.com/en/insights/publications/2024/08/alerts-technology-antc-google-is-an-illegal-monopoly-federal-court-rules , https://www.cnbc.com/2025/12/05/judge-finalize-remedies-in-google-antitrust-case.html).

### 6. Content and IP inputs
- **User-generated content (UGC):** free, but requires moderation and, increasingly, legal licensing. **[Fact]** Reddit's corpus became a paid data input for AI training — a new revenue stream and cost consideration (Reddit 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/1713445/000171344525000018/rddt-20241231.htm).
- **Licensed content:** YouTube pays content-acquisition costs to creators/media; music, news, and creator payouts are real COGS. Alphabet cited rising content-acquisition costs as a 2024 margin offset (Alphabet 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm).
- **Software/IP stack:** open-source (PyTorch, Linux, Kubernetes) plus proprietary ranking models. Low cash cost, high dependency; a foundational-model shift (needing far larger models) raises compute demand nonlinearly [inference].

### 7. Financial capital
Mature leaders are self-funding (Alphabet FY2024 net income $100.1B; Meta FY2024 net income ~$62B — Alphabet/Meta 2025 releases). **[Inference]** Access to cheap capital matters most for sub-scale players (Snap, Reddit historically) and for the capex arms race: only firms with tens of billions in annual free cash flow can fund the AI build-out, which is itself becoming a moat and a barrier to entry.

### 8. Regulation as an input constraint
Regulation is a de-facto input because it caps addressable data and monetization. Key items: EU GDPR and Digital Markets Act (gatekeeper obligations), Digital Services Act (moderation duties), Apple's App Tracking Transparency (2021, which cut targeting signal industry-wide), and U.S./state privacy laws. **[Inference]** ATT is the clearest "input shock": by degrading identifiers it forced Meta to rebuild targeting on first-party data and AI modeling, temporarily compressing ad efficiency before recovery. Data availability is thus a *regulated* input, and its scarcity directly determines ad pricing power.

### 9. How a shock propagates (worked examples)
- **GPU/CoWoS shortage → capacity cap.** Constrained packaging → platforms can't expand model-serving fast enough → ranking/ads quality plateaus, generative features rationed → engagement and ad-price growth slow; margin compresses if they overpay for scarce merchant GPUs [inference].
- **Electricity price/availability shock → capex delay.** Interconnection delays push out data-center energization → capex is stranded (depreciation without revenue) → ROIC on the AI build falls; the central 2025–2026 investor worry [inference].
- **TAC repricing (antitrust) → margin swing.** Shorter/unwound default deals mean either Alphabet pays less (margin up) or loses default traffic to rivals (revenue down) — a genuinely two-sided outcome [inference].
- **Privacy shock (another ATT).** Degraded signal → lower ad relevance → lower price-per-ad and advertiser ROI → revenue growth slows until first-party data and modeling compensate [fact of the 2021–2022 episode].

### 10. Which inputs set margins vs. cap capacity
**[Inference]** Margins are set primarily by (a) engineering/talent cost efficiency, (b) TAC for search, and (c) content-acquisition costs — all opex levers on an already high gross margin. Production **capacity** (how many high-quality impressions can be ranked/served, and how good targeting is) is capped by **compute and power**. The strategic squeeze of 2024–2026: the input that caps capacity (compute/energy) is controlled by suppliers with pricing power (Nvidia, TSMC, utilities), so value the platforms create is increasingly shared upstream — the opposite of the last decade when their inputs were nearly free.

### 11. Full attention, compute, data, marketplace, and trust ledger

Supply begins with users/creators, merchants/developers, content/catalog, advertiser demand, query/social/transaction data and legally usable identity or interest signals. Quality requires moderation, integrity, fraud prevention, recommendation/search models, language/local knowledge and customer support. Third-party websites, publishers and app developers are often unpaid or revenue-shared suppliers of the ecosystem.

Physical compute requires accelerators/CPUs, memory, storage, networking, servers, data-center land, grid connections, transformers, cooling/water, backup power and fiber/subsea capacity; cloud rental moves rather than removes these dependencies. Devices, operating systems, browsers, app stores, payment networks, ad tech and telecom provide access.

Talent includes AI/recommendation/search engineers, security, privacy, product/design, sales, policy, moderation and operations. Licenses, content rights, data consent/provenance, APIs, developer terms, model weights and open-source software are intangible inputs. Trust and safety, age assurance, advertiser brand safety and merchant quality are capacity constraints.

Funding includes ads/subscriptions/transactions, corporate cash/debt/equity, venture/growth capital, merchant/user balances and public research/procurement; startups often depend on cloud credits and platform distribution. Traffic-acquisition, creator/merchant share, compute, moderation and sales set margin; accelerators/power, data rights, platform placement, network liquidity, regulation and trust gate scale. Direct navigation, rival platforms, open protocols, offline retail/media and subscription or transaction models are substitutes.

### Sources
- MSCI GICS Methodology (2023/2024): https://www.msci.com/indexes/documents/methodology/1_MSCI_Global_Industry_Classification_Standard_GICS_Methodology_20240801.pdf
- IAB/PwC Internet Advertising Revenue Report FY2024 (Apr 2025): https://www.iab.com/wp-content/uploads/2025/04/IAB_PwC-Internet-Ad-Revenue-Report-Full-Year-2024.pdf
- Lawrence Berkeley National Laboratory, 2024 U.S. Data Center Energy Usage Report (Dec 2024): https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf
- Alphabet Form 10-K FY2024 (SEC): https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm
- Alphabet Q4/FY2024 earnings release: https://fortune.com/company-assets/1500/quartr/earnings-release-8-k-d7d50-2025-02-04-09-12-03.pdf
- Meta Platforms 10-K FY2024 summary (Libertify): https://www.libertify.com/interactive-library/meta-platforms-10k-2024/
- Silicon Analysts, Nvidia AI accelerator share / CoWoS (2025): https://siliconanalysts.com/analysis/nvidia-ai-accelerator-market-share-2024-2026
- Levels.fyi Meta/Google SWE compensation (2024/2025): https://www.levels.fyi/companies/meta/salaries/software-engineer
- CNBC, Google pays Apple 36% of Safari search revenue (2023): https://www.cnbc.com/2023/11/14/google-pays-apple-36percent-of-safari-search-revenue-sundar-pichai.html
- Goodwin, Google illegal-monopoly ruling (Aug 2024): https://www.goodwinlaw.com/en/insights/publications/2024/08/alerts-technology-antc-google-is-an-illegal-monopoly-federal-court-rules
- CNBC, Google antitrust remedies finalized (Dec 2025): https://www.cnbc.com/2025/12/05/judge-finalize-remedies-in-google-antitrust-case.html
- TIME, Facebook Africa content moderation (2022): https://time.com/6147458/facebook-africa-content-moderation-employee-treatment/
- LSE Africa blog, content moderation in East Africa (Nov 2025): https://blogs.lse.ac.uk/africaatlse/2025/11/03/there-is-a-dark-side-to-content-moderation-in-east-africa/
- Reddit Form 10-K FY2024 (SEC): https://www.sec.gov/Archives/edgar/data/1713445/000171344525000018/rddt-20241231.htm

## 3. Market Landscape


The complete industry structure: participants across the value chain, geographic clusters, where profit accrues vs. where it is competed away, and where economic value is migrating.

### 1. The value chain, stage by stage
1. **Compute & infrastructure suppliers (upstream, outside the sub-industry).** Nvidia (AI accelerators, ~80–90% share — Silicon Analysts 2025, https://siliconanalysts.com/analysis/nvidia-ai-accelerator-market-share-2024-2026), TSMC (fabrication + CoWoS packaging), SK Hynix/Micron/Samsung (HBM), plus power utilities and data-center builders. **Profit accrues heavily here now** because supply is constrained.
2. **The platforms themselves (the sub-industry).** Search (Alphabet, Microsoft Bing, Baidu), social/feed (Meta, Tencent, ByteDance/TikTok, Snap, Pinterest, Reddit, X, LinkedIn), classifieds/marketplaces (many regional), dating/reviews (Match, Yelp). **This is where the largest absolute profit pools sit.**
3. **Ad-tech intermediaries.** DSPs (The Trade Desk), SSPs, exchanges, ad servers, measurement/verification (DoubleVerify, Integral Ad Science). They monetize the open web that the walled gardens don't own. **Margins here are competed away** by the walled gardens' scale [inference].
4. **Advertisers & agencies (customers).** From SMBs (self-serve, the growth engine) to global brands via holding companies (WPP, Omnicom, Publicis). **[Inference]** SMB long-tail advertisers are the highest-margin demand because they are price-insensitive and automated.
5. **Users & content creators (both input and audience).** Creators are increasingly paid partners (YouTube, TikTok), shifting some value down to them.
6. **Regulators & governments.** Antitrust (DOJ, EU), privacy (GDPR, state laws), platform-conduct (DMA/DSA), and national security (data localization, TikTok).

### 2. Who leads and why — the moats
- **Alphabet (Google).** **[Fact]** FY2024 total revenue $350B, net income $100.1B; Google Services operating income $121.3B (Alphabet 10-K FY2024 / release — https://fortune.com/company-assets/1500/quartr/earnings-release-8-k-d7d50-2025-02-04-09-12-03.pdf). Moat: search default distribution + data + brand + owned compute (TPUs) + YouTube. The default-distribution leg is now legally contested (below).
- **Meta.** **[Fact]** FY2024 revenue $164.5B (+22%), family ARPU $49.63 (Meta 10-K FY2024 summary — https://www.libertify.com/interactive-library/meta-platforms-10k-2024/). Moat: the social graph across Facebook/Instagram/WhatsApp (~3.3B daily users), network effects, and an AI ad-ranking engine that turned ATT signal loss into a first-party-data advantage.
- **Tencent.** **[Fact]** FY2024 revenue RMB660.3B (~$91.9B), marketing services +20% to RMB121.4B, ad gross margin up to 55% (Tencent 2024 results — https://www.prnewswire.com/apac/news-releases/tencent-announces-2024-annual-and-fourth-quarter-results-302405688.html). Moat: WeChat super-app lock-in — messaging, payments, mini-programs, and Video Accounts feed in one graph.
- **ByteDance/TikTok.** Private; moat is the world's best recommendation algorithm (interest graph rather than social graph), which lets it monetize attention without needing a friend network — a genuine technical edge [inference].
- **Sub-scale specialists (Snap, Pinterest, Reddit, Match).** Moats are narrower — a demographic (Snap: teens), an intent (Pinterest: shopping/planning), a community structure (Reddit), or a category (Match: dating). Their vulnerability: they depend on Apple/Google platforms and lack the data scale to match Meta/Google ad targeting [inference].

### 3. Where profit accrues vs. is competed away
**[Inference]** Within the sub-industry, profit concentrates violently in the **owned-and-operated walled gardens** (Google, Meta, Tencent, ByteDance) because they own both the audience and the demand, capture the full ad dollar, and enjoy near-zero marginal cost. The **open programmatic web** (exchanges, SSPs, most publishers) is where margin is competed away — many intermediaries each taking a cut of a shrinking non-walled-garden pie; the "ad-tech tax" is under constant fee compression and antitrust pressure (the DOJ's separate ad-tech case against Google). **[Inference]** Increasingly, profit is *migrating upstream* to Nvidia/TSMC/utilities as the AI-capex arms race transfers value to whoever controls scarce compute and power — a structural change from the 2010s when the platforms' inputs were nearly free.

### 4. Geographic clusters and why they exist
- **U.S. (Silicon Valley/Seattle):** the dominant cluster. Exists because of the venture-capital ecosystem, elite engineering talent concentration, deep capital markets, and first-mover network effects. Hosts Alphabet, Meta, Snap, Pinterest, Reddit, plus the compute suppliers' customers.
- **China (Shenzhen/Beijing/Hangzhou):** a parallel, largely closed ecosystem (Tencent, ByteDance, Baidu, Alibaba) shielded by the Great Firewall from U.S. platforms — a state-created moat that let domestic super-apps flourish [inference].
- **South Korea/Japan:** Naver, Kakao, LINE — regional-language and local-service moats that resisted Google/Meta.
- **Europe:** consumes the platforms but produces few global winners; instead exports **regulation** (GDPR, DMA, DSA) as its principal influence on the industry [inference].

### 5. Trade flows, industrial policy, national security
- **Data localization & platform bans:** the clearest trade barrier is the U.S.–China platform split. **[Fact]** The U.S. enacted a law forcing ByteDance to divest TikTok or face a ban, on national-security grounds (data access + algorithmic influence); enforcement has been repeatedly delayed into 2025–2026. This is the defining national-security theme of the sub-industry.
- **Compute export controls:** U.S. restrictions on advanced-GPU exports to China directly constrain Chinese platforms' AI capacity, pushing them toward domestic silicon (Huawei) and models like DeepSeek [inference].
- **Antitrust as de facto industrial policy:** **[Fact]** In *U.S. v. Google* (Aug 2024) Judge Mehta ruled Google an illegal monopolist in search; 2025 remedies bar exclusive one-year-plus defaults, prohibit tying, and force data-sharing with "qualified competitors" but stopped short of a Chrome divestiture (Goodwin 2024; CNBC Dec 2025 — https://www.goodwinlaw.com/en/insights/publications/2024/08/alerts-technology-antc-google-is-an-illegal-monopoly-federal-court-rules , https://www.cnbc.com/2025/12/05/judge-finalize-remedies-in-google-antitrust-case.html). A separate DOJ ad-tech case targets Google's exchange/ad-server stack. The EU's DMA imposes parallel gatekeeper obligations.

### 6. What is gaining vs. losing relevance
**Gaining [inference, with sourced anchors]:**
- **AI-native answer engines and AI-assisted search.** **[Fact]** Google's AI Overviews and chatbots are reshaping query behavior: searches per U.S. user reportedly fell ~20% YoY as AI answers reduce queries-per-task, and zero-click searches rose from ~56% to ~69% after AI Overviews (Similarweb via search-industry reporting, 2025 — https://www.contentgrip.com/google-search-market-share-decline/). ChatGPT leads generative-AI chatbot visits at ~54% (Momentic, 2026 — https://momenticmarketing.com/blog/top-ai-chatbots).
- **Short-form video & recommendation-first feeds** (TikTok, Reels, Shorts) — the interest graph is displacing the social graph.
- **Retail/commerce media.** **[Fact]** Retail media reached $53.7B in the U.S. in 2024, +23% (IAB/PwC 2025 — https://www.iab.com/wp-content/uploads/2025/04/IAB_PwC-Internet-Ad-Revenue-Report-Full-Year-2024.pdf) — Amazon and retailers are capturing lower-funnel intent that once went to Google.
- **First-party data + AI modeling** as the post-cookie/post-ATT targeting substrate.

**Losing relevance [inference]:**
- **Third-party cookies and the open programmatic long tail** — squeezed by privacy rules and walled-garden concentration.
- **Text-link "ten blue links" search** as the primary interface, as AI answers intermediate the query.
- **Social graphs built on reciprocal friendship** (early Facebook) versus algorithmic interest feeds.

### 7. Disruption and obsolescence risks
- **The AI-search disruption to Google is the single largest tail risk in the sub-industry [inference].** If users get answers from chatbots (ChatGPT, Gemini, Perplexity) instead of clicking ads, the $100B+ search-ad profit pool could compress or migrate. Google's defense is to embed its own AI in search and leverage distribution; the offense comes from OpenAI/Microsoft and Perplexity. **The unresolved question is monetization: no one has yet proven that conversational AI monetizes as richly per query as intent-based search ads** [inference]. Distinguish *real* progress (measurable query-share and click shifts, per Similarweb) from *promotional* claims (unverified "Google is dead" narratives) — as of 2026 Google still holds ~90% of conventional search and grew ad revenue, so disruption is real but gradual.
- **Regulatory unbundling** (default remedies, DMA choice screens) could slowly erode Google's distribution moat.
- **Platform dependency** remains an existential risk for Snap/Meta vis-à-vis Apple/Google OS control.
- **Compute/energy cost inflation** could turn the AI build from margin-accretive to margin-dilutive if monetization lags capex.

### 8. Who is set to gain vs. lose
**[Inference]** *Likely gainers:* firms that own both a proprietary distribution surface and enough compute/data to run superior AI — Meta (proven ATT recovery + open-source Llama leverage), Google *if* it wins the AI-search transition, ByteDance (best recommendation tech), and Amazon (commerce-media intent). Upstream, Nvidia/TSMC keep capturing value while supply is tight. *Likely losers:* independent ad-tech intermediaries whose "tax" is squeezed; sub-scale ad platforms that can't fund AI targeting at Meta/Google scale; and any player whose value rests on a distribution default that antitrust unwinds. *Wildcard:* whoever cracks conversational-AI monetization first re-rates the entire search profit pool.

### 9. Where value is migrating (summary)
**[Inference]** Three simultaneous migrations: (1) *downstream to upstream* — from platforms toward compute/energy suppliers, as scarce inputs capture rents; (2) *open web to walled gardens* — advertising consolidating into Google/Meta/Amazon/TikTok; and (3) *within the platforms, from link-based search toward AI-answer and commerce-media surfaces*. The durable winners will be those who own a defensible attention surface AND vertically integrate enough compute to keep the AI flywheel spinning cheaply. Value is leaving the middle (intermediaries, undifferentiated publishers, sub-scale ad networks) and concentrating at the two ends: those who make the compute, and those who own the audience at global scale.

### 10. Complete output, customer, geography, funding, and policy map

Outputs include search/discovery, social connection, marketplaces, maps, messaging, creator distribution, advertising conversion, identity and developer/platform services. User-generated content and data are co-produced outputs; misinformation, fraud, addiction/harm, privacy loss, market dependence and compute emissions are negative outputs.

User, creator/publisher, advertiser, merchant, developer, subscriber and payment partner occupy different sides. A zero-price user supplies attention/data/content; advertisers or merchants pay; creators attract demand and receive a share; developers add complements but can be competed with by the platform. Welfare and revenue must not be inferred from user count alone.

Platforms distribute globally but localize for language, culture, payments, content law, data residency, competition and state access. Network effects can cross borders while moderation and political risk remain local. Search, social, video, marketplaces, app stores, ad tech, creator platforms and AI assistants increasingly converge.

Funding is mostly private/venture/public-market capital, with government research, digital infrastructure and procurement upstream. Rules cover privacy/data transfer, online safety/minors, content liability and moderation, copyright, advertising/consumer protection, competition/gatekeepers, interoperability, payments, labor/gig status, AI and election/foreign influence. EU digital-platform and AI rules can affect global product design.

The sector connects media/advertising, retail, payments, cloud/chips, telecom and labor. AI assistants may displace search clicks while raising compute; retailer media competes for ads; app-store rules alter developer take rates; privacy reduces targeting signals and raises first-party data value; power constraints can become growth constraints for compute-heavy services.

### Sources
- Silicon Analysts, Nvidia AI accelerator share (2025): https://siliconanalysts.com/analysis/nvidia-ai-accelerator-market-share-2024-2026
- Alphabet Q4/FY2024 earnings release: https://fortune.com/company-assets/1500/quartr/earnings-release-8-k-d7d50-2025-02-04-09-12-03.pdf
- Meta Platforms 10-K FY2024 summary (Libertify): https://www.libertify.com/interactive-library/meta-platforms-10k-2024/
- Tencent 2024 Annual & Q4 Results (PRNewswire): https://www.prnewswire.com/apac/news-releases/tencent-announces-2024-annual-and-fourth-quarter-results-302405688.html
- IAB/PwC Internet Advertising Revenue Report FY2024 (Apr 2025): https://www.iab.com/wp-content/uploads/2025/04/IAB_PwC-Internet-Ad-Revenue-Report-Full-Year-2024.pdf
- Goodwin, Google illegal-monopoly ruling (Aug 2024): https://www.goodwinlaw.com/en/insights/publications/2024/08/alerts-technology-antc-google-is-an-illegal-monopoly-federal-court-rules
- CNBC, Google antitrust remedies finalized (Dec 2025): https://www.cnbc.com/2025/12/05/judge-finalize-remedies-in-google-antitrust-case.html
- ContentGrip / Similarweb, Google search share decline & zero-click (2025): https://www.contentgrip.com/google-search-market-share-decline/
- Momentic, top generative-AI chatbots by share (2026): https://momenticmarketing.com/blog/top-ai-chatbots
- MSCI GICS Communication Services sector research (2018): https://www.msci.com/documents/10199/bbdd3ff9-b66e-975b-d35d-1028d1013837

## 4. Operating Mechanics


How the industry technically and economically works: the workflow from user session to monetized impression, the competing monetization methods and why players pick different ones, unit economics, KPIs, and — critically — how to value these businesses across life-stages.

### 1. The production workflow: from attention to cash
Every ad-funded platform runs the same loop:
1. **Acquire/retain a user** (organic virality, SEO, app-store presence, or paid TAC for search defaults).
2. **Generate a session** — the user searches or scrolls, producing a stream of "requests" (a query, a feed refresh). Each request creates ad inventory (slots).
3. **Rank organic content** to maximize engagement — the recommendation/ranking model decides what to show. This is the compute-intensive core; the better the model, the longer the session and the more inventory produced.
4. **Run an ad auction** for the monetizable slots. Advertiser bids are combined with a predicted engagement/conversion probability to compute an "ad rank," and the auction clears.
5. **Serve and measure** — the impression is served, and clicks/conversions are attributed back to advertisers, closing the feedback loop that trains both the ranking and the bidding models.

**[Inference]** The economic engine is this compounding loop: more users → more data → better ranking → more engagement → more inventory → more auction competition → higher price-per-impression → more cash to fund R&D and content that acquires more users. Data and scale are the flywheel; that is the industry's moat expressed as a process.

### 2. Competing monetization methods (and why players choose them)
- **Search/intent advertising (Google, Baidu, Amazon).** Ads keyed to explicit query intent. Highest ROI for advertisers and highest price-per-click because intent is revealed. **[Fact]** Search was $102.9B of U.S. digital ad spend in 2024 (IAB/PwC 2025 — https://www.iab.com/wp-content/uploads/2025/04/IAB_PwC-Internet-Ad-Revenue-Report-Full-Year-2024.pdf). Chosen by platforms that own the query.
- **Feed/interest advertising (Meta, TikTok, Pinterest, Snap, Reddit).** No explicit intent, so value comes from inferred interest via behavioral data + AI. Lower price-per-impression than search but vastly larger inventory. **[Fact]** Meta's 2024 ad growth came from +11% impressions and +10% average price-per-ad (Meta 10-K FY2024 summary — https://www.libertify.com/interactive-library/meta-platforms-10k-2024/). Chosen by platforms that own the audience but not the intent.
- **Programmatic/open-web display & video (via exchanges).** Publishers auction inventory through real-time bidding (RTB). **[Fact]** RTB completes an auction in milliseconds per impression; header bidding lets publishers solicit many demand sources simultaneously and reportedly lifts CPMs 20–50% vs. legacy waterfalls (industry sources, 2024 — https://www.aditude.com/blog/what-is-header-bidding). Auctions historically ran second-price (winner pays $0.01 above runner-up); most exchanges and Google shifted to first-price (~2019) for transparency (Avenga, 2024 — https://www.avenga.com/magazine/first-price-second-price-auction/). Chosen by publishers without owned demand.
- **Subscriptions / freemium (Match Group, YouTube Premium, X Premium, LinkedIn).** Recurring fees; higher-quality revenue, lower scale. **[Fact]** Match Group 2024 revenue $3.48B, overall revenue-per-payer $19.12/mo (+8% YoY); Tinder 9.7M payers, Hinge $550M direct revenue +39% (Match Group 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/891103/000089110325000027/mtch-20241231.htm). Chosen where a discrete outcome (a match, ad-free video) is worth paying for.
- **Data licensing (Reddit).** Selling the UGC corpus for AI training. A new model born of the LLM boom (Reddit 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/1713445/000171344525000018/rddt-20241231.htm).

**Trade-off rule [inference]:** Intent-based monetization beats interest-based when the platform owns the query (higher price, lower volume); interest-based wins when the platform owns attention but not intent (lower price, near-infinite volume). Subscriptions beat advertising when a user's willingness-to-pay for a discrete outcome exceeds their ad-monetization value — true for dating and premium video, false for casual social feeds.

### 3. Asset types and their economics
- **Intangible flywheel assets:** the user graph, behavioral data, ranking/ad models, and brand. Not on the balance sheet, but the true source of value [inference].
- **Physical assets:** data centers, servers, GPUs/TPUs, networking, subsea/terrestrial fiber. Increasingly heavy — the industry is shifting from asset-light to asset-heavier as AI capex rises. **[Fact]** Meta 2024 capex ~$37–39B; Alphabet ~$52B [estimate] (company releases 2025). Depreciation of this fleet is the new large cost line, and useful-life assumptions (typically ~4–6 years for servers) directly swing reported margins [inference].
- **Distribution assets:** search default contracts (a contractual asset for the counterparty, a cost for Google — ~$51B TAC in 2024).

### 4. Testing / qualification / measurement
- **A/B experimentation** is the qualification method for every product and ranking change; large platforms run thousands of concurrent experiments and ship on measured lift in engagement/revenue metrics [inference; standard practice].
- **Ad measurement/attribution** is the "quality control" of the revenue: multi-touch attribution, conversion APIs, incrementality tests, and (post-ATT) modeled conversions. Measurement fidelity determines advertiser trust and thus price [inference].
- **Brand safety / policy review** qualifies inventory for advertisers; failures (ads next to harmful content) trigger advertiser boycotts.

### 5. Unit economics and the cost stack
For a mature ad platform, the cost stack per dollar of revenue [inference from filings]:
- **TAC / revenue share** (search only): ~15–20% of Google advertising revenue.
- **Content-acquisition costs** (YouTube, creators): mid-single-digit to low-double-digit percent.
- **Infrastructure/serving compute + depreciation:** rising, historically single digits, now growing fastest.
- **R&D (engineering/ML):** the largest opex, often 15–25% of revenue at the leaders.
- **Sales & marketing / G&A:** moderate, sublinear due to self-serve.

**[Fact]** Result: Google Services FY2024 operating income $121.3B on $304.9B revenue — a ~40% segment operating margin (Alphabet 10-K FY2024 — https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm). Tencent's marketing-services gross margin rose to 55% in 2024 (Tencent 2024 results — https://www.prnewswire.com/apac/news-releases/tencent-announces-2024-annual-and-fourth-quarter-results-302405688.html). **The marginal cost of one additional impression is essentially the compute + bandwidth to serve it — pennies or less** — which is why incremental gross margins are extraordinarily high and why scale is decisive [inference].

### 6. KPIs practitioners actually track
- **Engagement:** DAU, MAU, DAU/MAU "stickiness," time spent, sessions/user.
- **Monetization:** ARPU (per DAU or MAU), impressions delivered, price-per-ad/CPM, cost-per-click. **[Fact]** Meta family-of-apps ARPU rose to $49.63 in 2024 from $44.60 (Meta 10-K FY2024 summary — same URL); Reddit/Pinterest/Snap ARPU is far lower (~$2–3/user/month in NA) reflecting weaker intent and monetization maturity (Sherwood, 2025 — https://sherwood.news/tech/how-much-money-social-media-facebook-instagram-reddit-snapchat-per-user-meta/).
- **Advertiser health:** ROAS/ROI, number of active advertisers, retention/spend expansion.
- **Subscription businesses:** payers, revenue-per-payer, churn, LTV/CAC. Match tracks payers and RPP explicitly (10-K FY2024).
- **Efficiency:** revenue/employee (very high here), and increasingly capex/revenue and free-cash-flow conversion given the AI build.

### 7. Development timelines and failure points
- **Timelines:** product features ship in weeks; ranking-model iterations are continuous; a new data-center campus takes ~2–4 years to permit, build, and energize, now often gated by power [inference]. This mismatch — fast software, slow physical capacity — is a core operational tension.
- **Characteristic failure points:** (a) **engagement decay** as a platform ages or a rival captures a demographic (the "teens left Facebook" risk); (b) **signal loss** from privacy changes degrading targeting; (c) **advertiser concentration/boycotts**; (d) **regulatory intervention** on defaults, data, or moderation; (e) **capex overreach** — building compute ahead of monetization and stranding depreciation; (f) **platform dependency** (Snap/Meta rely on Apple/Google OS and app stores).

### 8. Valuation across company life-stages

#### (a) Mature cash-generative platforms (Alphabet, Meta, Tencent)
Value as durable, high-margin free-cash-flow compounders. **Primary methods:** DCF on free cash flow, and P/E and EV/EBITDA relative to growth. **[Fact]** Meta has traded roughly 11–19x EV/EBITDA and ~20x P/E across 2024–2026 (stock-analysis-on.net / GuruFocus, 2026 — https://www.gurufocus.com/term/enterprise-value-to-ebitda/META). **Key adjustments [inference]:** (1) strip "other bets"/loss-making segments and value them separately (Alphabet's Cloud, Meta's Reality Labs burn ~$15–20B/yr); (2) treat stock-based compensation as a real cost — add it back to get cash flow but subtract its dilution; (3) watch capex/revenue — rising AI capex lowers near-term FCF, so the market increasingly scrutinizes ROIC on the build. A useful heuristic is "Rule of 40" (revenue growth % + FCF margin %), though it is more a growth-software screen than a mega-cap tool.

#### (b) Cyclical / asset-heavier businesses across the cycle
Digital advertising is **cyclical** — it tracks GDP and corporate marketing budgets, so revenue and especially margin swing with the ad cycle (2022 downturn, 2024 election/Olympics tailwind per IAB). **[Inference]** Value these on **mid-cycle (normalized) earnings**, not peak or trough: apply a through-cycle operating margin to a normalized revenue trend, then a multiple. EV/EBITDA is preferred over P/E because rising depreciation on the GPU fleet distorts net income and D&A varies with the capex cycle. For the asset-heavy AI infrastructure, watch **incremental ROIC** and depreciation-schedule assumptions — extending server useful life flatters earnings and is a known accounting lever [inference]. Smaller ad-cyclicals (Snap, Pinterest) carry higher betas and deserve wider valuation ranges.

#### (c) Pre-revenue / early / platform-optionality companies
Many social/UGC platforms IPO'd with huge users but thin or negative profit (Snap, Reddit, Pinterest early on). **Methods [inference]:**
- **User-based / ARPU-gap valuation:** value = users × achievable ARPU × probability of reaching it, benchmarked to a mature comp. E.g., Reddit's thesis rests on closing the ARPU gap to Meta; the bull case is EV/DAU or EV/user re-rating as monetization matures.
- **EV/Revenue with a path-to-margin overlay:** early platforms are valued on forward revenue multiples with an explicit assumed terminal margin; the multiple is really a probability-weighted bet on that margin being achieved.
- **Optionality on assets:** UGC corpora (Reddit's data-licensing), a defensible niche graph, or unique first-party data can be valued as a call option on future monetization (advertising, AI-training licensing).
- **LTV/CAC for subscription-led early names** (dating, niche apps): sustainable only if lifetime value comfortably exceeds acquisition cost; deteriorating payer counts (Tinder −7% payers in 2024) are the tell that the flywheel is stalling even when revenue holds via price.

**[Inference]** The unifying valuation principle: mature names are valued on *realized* cash flows and the durability of the flywheel; early names are valued on the *probability* of igniting the same flywheel — the metrics differ (DCF/EV-EBITDA vs. EV/user, EV/revenue, LTV/CAC) but all are proxies for "how much durable free cash flow will this attention machine eventually throw off, and how sure are we."

### 9. Complete interaction-to-cash and platform-risk mechanics

The chain is acquire/onboard user and complementor → collect permitted signals/content/catalog → rank/match/recommend → serve interaction or transaction → moderate/fraud-check → monetize → settle/revenue-share → retain and govern ecosystem. Marketplace liquidity is local to category/geography/time; global registered users do not guarantee a usable match.

Revenue includes auctioned/fixed advertising, transaction/take rate, subscription, lead/referral, cloud/API/developer and financial services. Gross bookings/GMV/ad spend differ from net revenue; traffic-acquisition, creator/merchant payouts, payment losses and refunds determine gross profit. Auction price depends on advertiser value, competition, relevance and measurement.

Working capital may include advertiser/merchant receivables, creator/seller payables, user balances, chargebacks, deferred subscription and content/compute commitments. Negative working capital can finance growth but creates safeguarding and liquidity obligations. Capital expenditure and long-term power/data-center contracts turn some “asset-light” platforms into infrastructure businesses.

Track active users and cohort retention, time/queries/content/transactions, creator or merchant supply, matching/conversion, ad load/price/click or outcome, GMV and take rate, subscription ARPU/churn, traffic-acquisition, compute per interaction, moderation/fraud/chargeback, capex and free cash flow. Stress privacy/signal loss, algorithm change, advertiser recession, platform disintermediation, harmful-content event, cyber outage, merchant/creator revolt, AI compute inflation and competition remedy.

### Sources
- IAB/PwC Internet Advertising Revenue Report FY2024 (Apr 2025): https://www.iab.com/wp-content/uploads/2025/04/IAB_PwC-Internet-Ad-Revenue-Report-Full-Year-2024.pdf
- Alphabet Form 10-K FY2024 (SEC): https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm
- Meta Platforms 10-K FY2024 summary (Libertify): https://www.libertify.com/interactive-library/meta-platforms-10k-2024/
- Match Group Form 10-K FY2024 (SEC): https://www.sec.gov/Archives/edgar/data/891103/000089110325000027/mtch-20241231.htm
- Reddit Form 10-K FY2024 (SEC): https://www.sec.gov/Archives/edgar/data/1713445/000171344525000018/rddt-20241231.htm
- Tencent 2024 Annual & Q4 Results (PRNewswire): https://www.prnewswire.com/apac/news-releases/tencent-announces-2024-annual-and-fourth-quarter-results-302405688.html
- Aditude, header bidding / programmatic guide (2024): https://www.aditude.com/blog/what-is-header-bidding
- Avenga, first-price vs second-price auctions (2024): https://www.avenga.com/magazine/first-price-second-price-auction/
- Sherwood News, social ARPU comparison (2025): https://sherwood.news/tech/how-much-money-social-media-facebook-instagram-reddit-snapchat-per-user-meta/
- GuruFocus, Meta EV/EBITDA history (2026): https://www.gurufocus.com/term/enterprise-value-to-ebitda/META

## 5. Economics and Valuation


Benchmark bands are diagnostic starting points; refresh for product, asset, geography, contract, and cycle.

### Core unit-economic identity

Platform contribution = advertising/transaction/subscription/API revenue − TAC − creator/merchant payout − payments/refunds/fraud − compute/content/moderation/support. Cash subtracts data-center/network capex, long-term compute/power and regulatory remediation.

### Ten benchmark measures

| Measure | Diagnostic band or unit | Decision use |
| --- | --- | --- |
| DAU/MAU | often ~20–80% by product habit | Engagement frequency |
| Ad load | impressions/time per active user | Monetization ceiling |
| Ad price | CPM/CPC/CPA and conversion | Demand/measurement |
| TAC | percent of search/traffic revenue | Distribution rent |
| Marketplace take | often ~5–30% by category/services | Monetization |
| Buyer/seller retention | cohort repeat and active supply | Network quality |
| Fraud/chargeback/refund | percent GMV/revenue | Trust cost |
| Compute per interaction | $/query/token/task | AI economics |
| Content/moderation cost | per user/content item and incident | Safety scale |
| Capex intensity | data-center/network capex/revenue | Infrastructure burden |

### Accounting-to-cash bridge

Separate GMV/bookings/ad spend from net revenue; principal/agent; TAC and payouts; customer/merchant funds; deferred subscription; chargebacks/refunds; content/model licenses; stock compensation and data-center leases/capex.

### Highest-value sensitivities

- User/creator/merchant retention, ranking, engagement quality and network liquidity.
- Advertiser demand, conversion/measurement, take rate, pricing and subscription.
- Compute/power, content/moderation, fraud/payments and traffic acquisition.
- Privacy, platform competition, online safety/minors, AI/copyright and geopolitical access.

### Valuation discipline

Use side-specific cohorts and unit contribution after TAC/payout/compute; assess network/distribution and regulatory liabilities. Infrastructure-heavy AI/platforms require capex-adjusted FCF.


## 6. Regulation and Public Funding


Snapshot reviewed through **2026-07-14**. Verify enacted text, implementation dates, litigation, and current guidance.

### Permission chain

User supplies attention/data/content; creator/publisher/merchant/developer supplies complements; platform ranks/distributes; advertiser/merchant/subscriber pays; cloud/chip/payment supports; moderator/regulator controls; end user receives.

### Jurisdiction and regime map

| Jurisdiction or layer | Core regimes and authorities | Economic transmission |
| --- | --- | --- |
| United States | FTC/DOJ competition/consumer, state/federal privacy, Section 230/content, minors, ads, payments and AI | Data, ranking, take, liability and M&A |
| European Union | DMA, DSA, GDPR, AI Act, consumer and copyright | Gatekeeper conduct, safety, data and AI |
| Other national markets | Data localization, censorship/content, foreign ownership, tax and payments | Access and product localization |
| Ecosystem/financial | App rules, merchant protection, KYC/AML, money transmission and gig labor | Take rate, payouts and workforce |

### Public and private funding

Private funding includes advertising/transaction cash, customer balances, venture/growth/public markets, debt and strategic cloud partnerships. Public funding includes basic internet/AI research, broadband and government digital procurement.

### Enforcement and liability

Competition remedies, app/take restrictions, privacy fines, content/child-safety liability, merchant/consumer restitution, payments/license loss, copyright damages, sanctions and service bans are core.

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
| 1990s search portals | Navigation became scarce as the web expanded | Search economics concentrated around intent | Information abundance creates discovery tolls |
| 2000s social network effects | Identity/content graphs drove rapid adoption | Winner scale and moderation burden rose | Growth creates governance cost |
| 2010s mobile app platforms | OS/app stores controlled distribution and payments | Developers paid platform tolls | Default access is an economic moat |
| 2016–2021 privacy and platform backlash | Data/market power drew regulation | Targeting and acquisitions faced constraints | Regulation can change the data-production function |
| 2022–2026 generative AI search/agents | Answer interfaces challenged click/referral models | Compute and publisher rights rose while monetization shifted | New interface can cannibalize the old toll |

### Practitioner extraction

- **Leading signals:** Cohorts, DAU/MAU, time/tasks, creator/merchant supply, ad price/conversion, take, TAC, compute, moderation/fraud and regulation.
- **Evidence that breaks the easy thesis:** Registered users without active cohorts, GMV without contribution, or AI usage without retention/compute margin.
- **Durable lesson:** Platform expertise measures each side's liquidity and value after distribution, trust and infrastructure cost.


## 8. Data Sources and Monitoring Dashboard


Preserve observation period, unit, definition, geography, and revision vintage.

### Primary source map

| Source | Cadence | Best use | Caveat |
| --- | --- | --- | --- |
| [SEC EDGAR filings](https://www.sec.gov/edgar/search/) | quarterly/annual | Users, ads, GMV, capex and risks | Company-defined metrics |
| [FTC cases and policy](https://www.ftc.gov/legal-library/browse/cases-proceedings) | event-driven | Competition and consumer enforcement | US only |
| [European Commission DMA/DSA](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act-package) | rule-driven | EU platform obligations | Implementation evolves |
| [European Commission AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) | rule-driven | AI obligations | Timeline/rules evolve |
| [BEA digital economy](https://www.bea.gov/data/special-topics/digital-economy) | periodic | Economic output | Aggregated |

### Indicator stack

- **Leading:** cohort retention; creator/merchant supply; ad auction; app ranking; compute.
- **Coincident:** DAU/MAU; engagement; GMV; take; conversion; TAC; fraud.
- **Lagging:** network durability; enforcement; capex return; creator economics; disintermediation.

### Minimum dashboard

1. **DAU/MAU** — often ~20–80% by product habit; Engagement frequency.
2. **Ad load** — impressions/time per active user; Monetization ceiling.
3. **Ad price** — CPM/CPC/CPA and conversion; Demand/measurement.
4. **TAC** — percent of search/traffic revenue; Distribution rent.
5. **Marketplace take** — often ~5–30% by category/services; Monetization.
6. **Buyer/seller retention** — cohort repeat and active supply; Network quality.
7. **Fraud/chargeback/refund** — percent GMV/revenue; Trust cost.
8. **Compute per interaction** — $/query/token/task; AI economics.
9. **Content/moderation cost** — per user/content item and incident; Safety scale.
10. **Capex intensity** — data-center/network capex/revenue; Infrastructure burden.

### Normalization rules

- Use active cohorts.
- Bridge GMV/ad spend to net.
- Subtract payouts/TAC/compute.
- Filter bots/fraud.

### Evidence traps

- Registered users.
- GMV as revenue.
- Engagement without welfare or monetization.

## 9. Geographic Operating Models

Geography changes ownership, contracting, cost, funding, regulation and risk; compare like with like.

| Geography / archetype | Operating model | Economic and risk implications |
| --- | --- | --- |
| United States | Global search, social, marketplace, cloud-adjacent and creator platforms with venture-scale ecosystems | Network effects, data and advertising depth support scale under competition scrutiny |
| European Union | Large user/advertiser market governed by stronger platform, privacy and content rules | Compliance and consent affect targeting, app distribution and product design |
| China | Domestic super-app, search, social, commerce and gaming ecosystems behind distinct regulation | Local platforms integrate payments/commerce but have limited global interoperability |
| India/Southeast Asia | Mobile-first, multilingual growth markets using digital payments and low-cost data | High engagement may monetize at lower ARPU; local commerce/logistics matter |
| Latin America/Africa | Rapid social, messaging, fintech and marketplace adoption with infrastructure/payment constraints | Currency, fraud, moderation and merchant formalization shape unit economics |

## 10. Cross-Industry Dependency Map

| Dependency class | Linked markets and institutions | Transmission into this industry |
| --- | --- | --- |
| Compute/data | Clouds, chips, networks, storage, models, identity and licensed/user data | AI and video raise compute and content-delivery cost |
| Content/supply | Users, creators, publishers, merchants, developers and app ecosystems | Platform value depends on healthy counterpart economics |
| Demand/monetization | Advertisers, agencies, consumers, merchants, subscriptions and payments | Auction density and transaction trust determine monetization |
| Distribution | Mobile OS, browsers, app stores, device defaults, search access and telecom networks | Traffic-acquisition and platform rules allocate value |
| Policy/externality | Privacy, competition, child safety, speech, copyright, fraud, tax and election rules | Trust/safety and legal duties are operating inputs, not peripheral costs |

The practical test is to trace a shock through availability, delivered cost, working capital, output, customer economics, financing and eventual substitution—not merely name the adjacent market.

## 11. Decision-Grade Unit Economics

> The numerical example below is illustrative, not a current market forecast or universal benchmark. Replace every assumption with asset-, contract-, product- and geography-specific evidence.

**Representative unit:** One million monthly active users on an ad-and-transaction platform.

**Core equation:** `User-cohort contribution = monetizable events × net yield + transaction/subscription revenue − traffic/creator share − compute/delivery − trust/safety/service − sales − allocated product/G&A` 

| Bridge item | Illustrative assumption and calculation | Result / interpretation |
| --- | --- | --- |
| Ad opportunity | 1m users × 30 sessions × 5 monetizable impressions | 150m impressions/month |
| Net advertising | 150m ÷ 1,000 × $8 eCPM × 70% fill/quality factor | $840k/month |
| Transaction/other | Net take rate, subscription and developer/service revenue | $200k/month |
| Compute/delivery | Hosting, inference, network and storage | $100k/month |
| Traffic/creator/trust | $250k acquisition/revenue share + $80k moderation/fraud/service | $330k/month |
| Illustrative contribution | $1.04m − $100k − $330k − $200k sales − $250k product/G&A | $160k/month before corporate and long-horizon R&D |

**Decision test:** Measure country/product cohorts by retained active use, monetizable intent, net yield, acquisition/revenue share, compute and trust cost; global MAU is not an economic unit.

## 12. Industry Balance and Marginal Economics

| Balance concept | Industry-specific definition | What to measure |
| --- | --- | --- |
| Marginal supply unit | Next platform, creator, merchant or developer able to attract a user interaction | Network liquidity and distribution—not server count—gate supply |
| Marginal customer | User/advertiser/merchant choosing another platform, direct channel or no transaction | Multihoming makes switching different on each side |
| Clearing mechanism | Ad auctions, take rates, app fees, subscriptions and revenue shares | Platform price is a vector across participant sides |
| Cash shutdown point | Feature/market continues while incremental ecosystem value exceeds compute, support, risk and acquisition cost | Cross-subsidy can sustain a standalone loss |
| New-capacity incentive | Expected network and cohort lifetime value covers product, moderation, distribution and infrastructure | Regulation and congestion can reverse scale benefits |
| Adjustment lag | Instant compute allocation, months for product adoption, years for trust/network formation | Technical launch does not create marketplace liquidity |

## 13. Terminology and Comparability Traps

| Reported term | Common but invalid interpretation | Required normalization |
| --- | --- | --- |
| MAU/DAU | Comparable human engagement | Define active action, deduplicate, remove bots, segment country/product and assess intensity |
| Engagement | Economic or healthy use | Measure intent, time, retention, monetization, wellbeing and opportunity cost |
| Ad impressions | Revenue opportunity | Adjust eligibility, fill, viewability, fraud, auction density and net yield |
| GMV | Platform revenue or value added | Apply take rate, returns, incentives, seller services, tax and pass-through payments |
| Network effect | Permanent defensibility | Identify participant side, local density, multihoming, switching, interoperability and governance |


