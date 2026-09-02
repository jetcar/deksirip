# Ethereum Research / RadicalxChange / Gitcoin–Optimism governance forums — draft

> Archived adaptation. Use [10-master-post-v2.en.md](10-master-post-v2.en.md) for a new publication; the old body contains objections later removed.

**Why:** this is the only audience that has **carried out real experiments** on the distribution of public funds by voting and knows the specific ways in which it breaks: sybil, collusion, vote buying, delegate apathy, degradation of retro funding rounds. The most practical criticism available.
**How ​​not to go off-topic:** tie to quadratic funding and RetroPGF, speak in the language of mechanisms and attacks, not in the language of political philosophy.
⚠️ Check the rules of a particular forum before posting; select the Mechanism Design/Economics category.

---

## Title

**QF at societal scale: what breaks when the matching pool is the entire social product?**

## Body

This is a thought experiment about the limit case of plural funding, and I'd like people who have actually run rounds to tell me where it fails.

**The setup.** Instead of a matching pool topped up by donors, imagine the *entire* capital allocation of an economy runs through citizen-directed funding. Every person receives a recurring equal allocation of social product. Unspent allocation accumulates as a non-transferable personal balance with no ownership or resale rights attached. Any person or group proposes a project with a funding threshold; it executes if enough people direct balances into it. Long-gestation projects receive multi-year pledges that stay revocable. There is deliberately no committee that approves projects, and no secondary market in claims.

Concretely: this is Roemer's 1994 coupon socialism with the monitoring banks removed, or QF with the matching pool set to 100% and the donor pool set to everyone.

**Attacks I already expect, based on what's happened in practice:**

1. **Sybil.** The payoff to a fake identity is now a share of real resources, not a slice of a bounded matching pool, so the attack budget scales with the economy. Every proof-of-personhood scheme I know reintroduces a gatekeeper who can exclude people from the economy entirely. Is there a sybil-resistance result that doesn't reduce to a trusted registry when the stakes are unbounded?

2. **Collusion.** Pairwise-bounded QF and cluster-matching help against naive collusion; they don't help when the colluding group is a genuine community with genuinely correlated preferences, which is indistinguishable from a cartel by construction. Gitcoin rounds needed a permanent fraud team and manual disqualifications. At societal scale that team is a state agency with discretion — which is exactly the institution the design was trying to avoid. Is there a version of this that doesn't require a human referee?

3. **Delegate concentration.** With thousands of projects and finite attention, delegation is inevitable and delegate weight goes power-law. Observed everywhere: DAO delegate distributions, LiquidFeedback superdelegates in the German Pirate Party, index-fund voting concentration in equities. Does anyone have a delegation design with a *provable* bound on concentration that doesn't amount to prohibiting recommendation lists?

4. **No informed sceptic.** Balances are non-transferable, so you cannot take a position against an overhyped project. Grossman–Stiglitz: information enters prices because informed traders profit from it. Remove the profit and you remove the analysis, leaving marketing as the highest-return activity in the system. Prediction markets are the obvious patch — but a prediction market on project outcomes is a tradable financial claim, i.e. the thing that was banned. Is there a non-tradable mechanism with comparable information aggregation?

5. **Retroactive funding doesn't fix long horizons.** RetroPGF works because the impact is already visible. For a 20-year project, revocable pledges get pulled around year 7 when spend is high and results are nil — time inconsistency in the Kydland–Prescott sense. Irrevocable endowments solve it and create a perpetual unaccountable fund. I don't see a third option; is there one?

6. **Low participation is the base case.** DAO turnout runs 1–10% of tokens. At those rates "citizens decide" means "the most motivated 5% decide", which is an unelected self-selected elite with no recall mechanism — strictly worse for accountability than an elected body. Is there any observed intervention that moved participation durably, as opposed to for one round?

7. **Nothing reconciles aggregate composition.** The economy-wide split between consumption and investment becomes an emergent sum of independent choices, with nothing making it consistent with physical capacity to produce investment goods. This is the part I understand least in mechanism terms and would like sharpened.

**What I'm asking for:** concrete attack paths in the form "X → agents' best response is Y → Z → mechanism degenerates", especially ones grounded in what you saw in real rounds. Also: any published post-mortems on QF/RetroPGF rounds with quantified sybil or collusion rates, which I've had trouble finding.
