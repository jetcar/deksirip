# Hacker News — Ask HN draft

> Archived adaptation. Use [10-master-post-v2.en.md](10-master-post-v2.en.md) for a new publication; the old body contains objections later removed.

**Rules checked.** Key: “Most stories about politics… are off-topic unless they're evidence of some interesting new phenomenon”; “Please don't use HN primarily for promotion”; don't ask for a vote; Do not post generated text in comments.
**Risk Mitigation:** This should be a **Text Ask HN** and not a link to the manifest; the frame is mechanism-design and distributed systems, not a political program; no rhetoric about capitalism. Heading without editorializing.
**Realistic Expectation:** Can be flagged as a policy. If so, don’t overpost (this is against the guidelines).

---

## Title

**Ask HN: Can dispersed, non-transferable stakes ever produce adequate monitoring?**

## Body

I've been picking apart an allocation mechanism and I keep hitting the same wall, which I think is a general problem rather than a property of this design. I'd like to know if anyone has seen it solved anywhere.

**The mechanism, stripped of politics:** every participant receives a recurring, equal allocation of a scarce budget. Unspent allocation accumulates in a personal balance. Balances are non-transferable and confer no ownership or resale rights. Any participant can propose a project with a funding threshold; the project executes if enough participants direct their balances into it. Projects with long gestation can receive multi-year pledges, revocable at any time. There is no committee that approves projects and no market where stakes can be resold.

**The wall.** With N participants each holding 1/N of the oversight benefit and 100% of their own oversight cost, nobody audits how a funded project spends. The two known fixes are (a) concentrated stakes — an investor big enough that monitoring pays for itself — or (b) a delegated monitor with a mandate. The mechanism forbids both by construction. What is left is insider control of resources that insiders do not own, which is the pattern this kind of design is usually meant to prevent.

**Related things that seem to break the same way:**

- **Quadratic funding.** Designed exactly for "many small funders beat a few big ones", and in practice every Gitcoin round needed a sybil-detection team and manual disqualifications. Both sybil resistance and collusion resistance seem to require a trusted identity registry, which recreates the central authority.
- **DAO governance.** Participation typically 1–10% of tokens, delegate weight concentrating in a handful of addresses, and treasuries drained via governance capture (Build Finance is the cleanest example). Liquid democracy hits the same superdelegate problem — German Pirate Party LiquidFeedback data is the reference.
- **Crowdfunding as capital allocation.** No shorting, no resale, no way to profit by debunking an overhyped project. Grossman–Stiglitz says information gets into prices because informed traders profit from it; remove the profit and you remove the informed trader. Empirically: ICO outcomes in 2017–18, Kickstarter delivery rates.
- **Revocable long-term pledges.** A 20-year project looks like a failure at year 7 by construction. Making pledges irrevocable fixes it and immediately creates an unaccountable perpetual fund.

**Questions I'd like answers to:**

1. Is there *any* system — technical, financial, organisational — where fully dispersed non-transferable stakes produced adequate monitoring without either concentration or a delegated auditor? I can't think of one and would like to be corrected.
2. Is sybil resistance without a trusted identity registry actually possible for a mechanism where the payoff to a fake identity is a share of real resources? Proof-of-personhood schemes all seem to reintroduce a gatekeeper.
3. Is there a delegation design with a provable bound on delegate concentration that doesn't reduce to banning recommendations?
4. Has anyone formalised the difference between staking a replenishing income stream and staking a non-replenishing endowment, in terms of how selective the staker becomes?

Context, since it will be asked: this comes from evaluating a proposed economic arrangement, but I think (1)–(4) are mechanism-design questions that stand on their own, and I'm more interested in those than in the politics.
