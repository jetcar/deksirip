# Criticism of the concept of a decentralized public economy
## Part 1. Failure Mechanisms

Format: **X → stimulus Y → consequence Z → destabilization**.
The goal is not “greedy people,” but institutional mechanisms that work even with perfectly conscientious participants.

---

## M1. Lack of prices for means of production (Mises-Hayek problem, version 2.0)

**Mechanism.**
The project received 10 billion conventional units. What does he buy with them? Machine tools, steel, engineer man-hours, site, energy. These are goods for production purposes. Their relative value must be expressed in some way, otherwise it is impossible to compare two ways of making an engine.

- X: means of production cannot be owned, which means there is no market for them, where someone puts their own non-renewable supply against their valuation.
- Y: prices for them can only be set by (a) an administrator, (b) a formula, (c) an internal quasi-market between enterprises that do not have a residual claimant for profit/loss.
- Z: in all three cases, the price ceases to be a carrier of information about rarity. It becomes either an administrative decision (= you returned the State Planning Committee) or noise.
- Destabilization: citizens' investment decisions are made in units that do not reflect physical scarcity. Voting in rubles without informative prices for factors is voting by sympathy.

**Key detail the concept misses.** Customer demand is only half the puzzle. It was the second half that Mises attacked in 1920: the distribution of capital goods among competing production techniques. The social dividend solves the first half and does not affect the second.

**Why is this not adjustable by parameter?** The information content of the price of a capital good arises from the fact that someone bears the residual risk. Removing the residual bidder and maintaining the informative price is logically incompatible, not difficult.

---

## M2. Soft budget constraint (Kornai) reinforced by dividend unconditionality

**Mechanism.**
- X: dividends are received regularly and unconditionally. The citizen risks **flow**, and the capitalist risks **stock**, which no one will replace.
- Y: expected cost of error for a citizen ≈ deferred consumption for N months. The incentive to scrutinize a design is close to zero; the incentive to participate in “interesting” things is high.
- Z: systematic oversupply of applications, lack of an exit mechanism (no one really goes bankrupt), chronic shortage of real resources with an excess of nominal applications for them.
- Destabilization: an economy of deficit in Kornai's terms, but without a planning authority that at least tries to balance the balances.

**Strengthening.** A project that is “interesting to a large number of people” can receive funding again after failure: the composition of investors has been updated, memory has been scattered, the costs of failure have been socialized. This is a ratchet: the share of resources spent on non-refundable projects grows monotonically.

---

## M3. Zero monitoring with dispersed possession (Berl-Means in extreme form)

**Mechanism.**
- X: the share of each citizen in control over any project ≈ 1/N, where N is tens or hundreds of millions.
- Y: monitoring costs are private, benefits from monitoring are public. Rational ignorance. Nobody reads the report on the spending of 10 billion.
- Z: actual control passes to those inside the project: managers, engineers, administrators.
- Destabilization: control without ownership. This is exactly the configuration of the Soviet nomenklatura and the “new class” of Djilas: legally no one owns anything, in fact a narrow group controls it, and it cannot be bought out or fired.

**There are exactly two known ways to solve the monitoring problem:**
1. Concentrated share (major shareholder, monitor bank, venture fund with a seat on the board) is prohibited by the concept.
2. Delegated supervisory body - prohibited by the concept (“there should not be a closed body”).

There is no third one in the literature. Roemer, in A Future for Socialism, proposing an almost identical coupon scheme, was forced to add Japanese-style banks as monitors. Your scheme removes this too.

---

## M4. Delegation → concentration (Michels' iron law through attention deficit)

**Mechanism.**
- X: there are thousands of projects, the citizen’s time is finite.
- Y: it is rational to delegate the assessment to someone who understands. “Curators”, “lists of recommendations”, “trust funds” emerge.
- Z: the return on specialization in attention is positive and cumulative: whoever has already gathered delegates finds it easier to gather more (preferential accession). The distribution of delegated shares becomes exponential.
- Destabilization: 20–50 curators direct the investment flow of society. Formally, they do not own anything; in essence, they are new financial capital.

**Empirics, not hypothesis:**
- German Pirate Party / LiquidFeedback: the problem of “overdelegates”; individual users accumulated double-digit percentages of delegated votes.
- DAO (Uniswap, Compound, MakerDAO): the decisive share of votes for address units; participation is usually 1–10% of tokens.
- Index funds in capitalism: three management companies hold about 20% of the votes of the S&P 500, without “owning” anything in the economic sense - they manage someone else’s.

**Why it’s not configurable.** Prohibiting delegation means requiring everyone to competently evaluate thousands of projects, which is physically impossible. Allow - gain concentration. Intermediate restrictions (ceiling on the number of delegates) are circumvented by the creation of formally independent curators with a common source of recommendations.

---

## M5. Beauty contest and information cascades

**Mechanism.**
- X: the project needs a funding threshold. My units will only be useful if others collect the threshold.
- Y: the rational question of a citizen is not “whether the project is good”, but “whether others will finance it.” This is a game of coordination (Keynes, Chapter 12).
- Z: herding, cascades (Bikhchandani-Hirshleifer-Welch), overreaction to early signals, distribution of results with heavy tails, modes.
- Destabilization: society's capital investment correlates with the prominence of the initiator and the quality of the presentation, and not with the expected return.

**Empirics:** ICO boom 2017 (according to Satis Group, about 78% of projects that raised money turned out to be scams or dead), Kickstarter (a significant proportion of funded projects do not deliver the product), Gitcoin Grants (see M6).

**Grossman-Stiglitz as an amplifier.** Information gets into the price because an informed trader makes money on it. In your system, you cannot make money by researching a project: you cannot take a large position, you cannot short an overvalued project, you cannot resell a share. So there is no professional skeptic. All that remains is marketing.

---

## M6. Quadratic financing does not save: sybil and collusion

If you try to fix the M5 through quadratic funding (Buterin-Hitzig-Weyl) - a formula specifically designed so that the breadth of support beats the size of the contribution - you will receive two known failures:

- **Sybil**: it is beneficial to split into many individuals. Protection requires a stable identity system → a centralized register of identities → whoever maintains it has the power to exclude people from the economy.
- **Collusion**: a group of K people, having agreed to cross-fund each other's projects, gets more out of the match than they contribute. The formula is optimal only in the absence of collusion.

Gitcoin had to maintain a fraud detection team in each round and manually disqualify participants. **This is the bureaucracy that the concept prohibits** - it’s simply called “anti-fraud”.

---

## M7. Nobody manages existing factories

The concept describes in detail how **new** projects are financed, and does not describe who makes decisions in an **existing** enterprise: equipment replacement, hiring and firing, supplier selection, payment differentiation, product changes.

Exactly three options are possible, and all three have already been tested:

1. **The workforce of the enterprise.** This is Yugoslav self-government. Known pathologies: the Ward-Domar-Vanek effect (a firm that maximizes income *per employee* can reduce employment when prices rise - supply with a reverse slope); Furubotna-Pejovic horizon problem (non-transferable share → underinvestment in long-lived assets); in practice - unemployment, inflation, regional divergence, collapse of the system.
2. **Designated Manager.** Who appoints? Any answer is a prohibited organ.
3. **Nobody, "people's preference" bootstrapping.** People's preferences do not contain information about whether to change the sander this year.

This is not a parameter, but a **hole in the design**.

---

## M8. The aggregate saving rate has not been agreed upon by anyone

**Mechanism.**
- X: dividend issued in units. The citizen himself decides how much to spend on consumption and how much to save/invest.
- Y: the total decision of millions of people sets the rate of accumulation of the economy. But the physical economy has the capacity to produce consumer goods and the capacity to produce investment goods, and they are not instantly interchangeable.
- Z: if everyone decided to save - excess demand for investment goods while the food and light industries are idle; if everyone decides to spend, the opposite is true.
- Destabilization: the classic problem of matching the structure of output with the structure of demand (Kalecki, Domar). In capitalism it is partly decided by interest rates and profits; in plan - plan. Nothing matters here.

**Additional information about inflation (question 14).** If the dividend is a nominal requirement and prices are free, the real value of the dividend is endogenous. Voting to raise dividends is always locally popular → common pool effect in the budget → ratchet → indexing → spiral. The Alaskan PFD only works because it is (a) small, (b) backed by external rent, (c) calculated using a statutory formula; once the formula was politicized after 2016, it became a budget warground.

---

## M9. Convertibility leaks restore the capital market

Accumulated units “cannot be invested in property,” but they “can be disposed of.” Every control channel is a potential leak:

- **Gift.** I give you 1 million units → actual transfer of purchasing power. Donation can be prohibited, but then transaction control is needed.
- **Hiring services.** I pay for your work → team over labor = core of capital.
- **Reciprocity.** “I finance your project, you finance mine” - a cartel of investment preferences; legally indistinguishable from independent decisions.
- **Secondary market.** Units for real things, for foreign currency, for services. Historically, it always arises: Soviet “Beryozka” checks, Cuban CUC, wartime card systems of Britain and the USA - everywhere the secondary market appeared within months.
- **Inheritance.** Inherited → dynastic accumulation returns immediately. Not inherited → powerful incentive for lifetime distribution and bypass schemes (exactly like optimization of inheritance tax).

**Conclusion:** In order for the property ban to hold, total monitoring of transactions and individuals is needed. This is the most centralized institution possible.

---

## M10. Responsibility kills long horizons (temporal inconsistency, Kydland-Prescott)

**Mechanism.**
- X: “funding may be revised as new information becomes available” and “if the project is unsuccessful, people may stop funding.”
- Y: a project with a horizon of 20 years in the 7th year **by construction** looks like a failure: a lot of money was spent, there is no result. A rational citizen with limited attention stops funding.
- Z: only projects with quick demonstrable impact and a good narrative survive.
- Destabilization: systematic erosion of precisely the class of projects for which the long-term financing mechanism was introduced.

**Counterexamples from reality:** Katalin Kariko and mRNA - more than ten years of grant refusals and demotion; ITER; LHC (approved 1994, physics 2012); Human Genome Project; decades of “winter” of neural networks.

**Dilemma with no way out.** For long-term projects to survive, **irrevocable** commitments are needed. An irrevocable pool of funds with a multi-year mandate is a fund that citizens do not control, that is, **exactly the body that the concept prohibits**. Either recall and the absence of long projects, or long projects and an uncontrolled fund. There are no intermediate options: any “partially revocable” obligation is revoked exactly at the moment of crisis of confidence.

---

## M11. Direct democracy over a multidimensional distribution space does not have a sustainable solution (Arrow, McKelvey, Schofield)

**Mechanism.**
- X: “citizens themselves set priorities and the size of strategic reserves.” The decision space is multidimensional (which drugs, how much, where, for how long, at what cost).
- Y: McKelvey's chaos theorem: in a multidimensional space and a majority rule, the core is usually empty, and **whoever controls the agenda can bring the outcome to almost any point in space** by a sequence of pairwise votes.
- Z: power = the right to formulate a question. Someone must write the wording, determine “sufficient volume,” select a supplier, maintain a warehouse, rotate overdue items, and decide when to release the reserve.
- Destabilization: the stated principle of “no body that independently determines priorities” is **logically incompatible** with “citizens establish reserves.” The agenda organ always exists; failure to acknowledge it means he is not accountable.

This is the strongest argument in the set: it is not about people or incentives, but about the mathematics of collective choice.

---

## M12. Olson: an organized minority always defeats a scattered majority

**Mechanism.**
- X: the benefit from capturing the resource is concentrated, the costs of resistance are dispersed.
- Y: a block of 2% of citizens with coordinated distribution of dividends systematically outperforms 60% of those who are not coordinated.
- Z: sector after sector is captured by disciplined groups (industry communities, religious and ideological associations, regional blocs, professional “trend” lobbyists).
- Destabilization: a system designed to maximize participation, in practice distributes organized groups across maps.

**Empirics:** Participatory budget of Porto Alegre - participation of about 1-2% of the adult population, dominance of organized residents' associations, coverage of only part of the capital budget, curtailment of the program in 2017.

---

## M13. Passivity does not smoothly degrade the system, but turns it into an oligarchy without elections

**Mechanism.**
- X: the probability that my vote/dividend is decisive is ≈ 0.
- Y: rational non-participation. Basic participation rates: DAO 1–10%; Swiss referendums about 45%; local elections in the USA 15–20%; meetings of residents - a few percent.
- Z: decided by 3–7% of the most motivated, that is, a self-selected group with the strongest ideological or material interest.
- Destabilization: it turns out to be an elite **without a recall mechanism**. The elected politician may not be re-elected; a self-selected activist investor is not possible. In terms of accountability, it is **worse** than representative democracy, not better.

---

## M14. AI advisor destroys the epistemic rationale for a mass decision

**Mechanism.**
- X: Condorcet’s theorem (and the “wisdom of the crowd” in general) requires **independence of errors** of voters.
- Y: If millions delegate analysis to one or two models, errors become highly correlated.
- Z: at high correlation, the accuracy of the collective decision stops increasing with the number of participants and may decrease (Ladha and subsequent literature on dependent votes).
- Destabilization: “AI helps citizen analyze” is not a neutral infrastructure, but a common source of systematic error. Plus: the one who determines learning, failures and model formulations sets the agenda (see M11), that is, is the hidden sovereign. “AI is not an arbiter of truth” is a wish, not a mechanism.

---

##M15. Army: “only force is centralized” - historically the least stable configuration

**Mechanism.**
- X: the civilian political class is absent by design; The professional army is the only permanent, hierarchical, disciplined organization in society.
- Y: praetorian logic (Feiner, “The Man on Horseback”; Huntington; Nordlinger): the likelihood of military intervention increases with weak and fragmented civil institutions and contested legitimacy.
- Z: in a crisis, the army is the only capable entity. She doesn’t need to “seize power”, just stop asking.
- Destabilization: civilian control is carried out by **specific positions with powers** - the ministry, parliament with budgetary authority, the prosecutor's office. This is exactly the professional device that the concept cancels. “Citizen control” without a control body is not control.

**Separately, the emergency clause.** “When attacked, the army acts without voting” is Schmitt’s exception. The sovereign is the one who decides that a state of emergency has occurred. If the command decides, it is sovereign. Roman dictatorship, art. 48 of the Weimar Constitution, the spread of the AUMF in the USA - all began as a narrow, reasonable mandate.

**About the “lack of an independent economic base.”** In a protracted war, the army inevitably receives priority control over resources; After the war, powers are not fully restored (Higgs, "Crisis and Leviathan"). Egypt and Pakistan are modern examples of the army as a major economic entity.

---

## M16. War/catastrophe: the escape hatch is the mechanism of transformation into a centralized state

- X: total war requires the redistribution of tens of percent of output over months (War Production Board 1942, British Emergency Powers Act).
- Y: voluntary distribution of dividends physically cannot ensure this - directive reallocation and priorities are needed.
- Z: an emergency body with planning powers is introduced.
- Destabilization: Tilly - “wars create a state”; Higgs is a ratchet of authority. The presence of a mandatory emergency mode in the design means that the system has a built-in path of conversion to a centralized state, and there is no return path in the design.

---

## M17. Unpleasant work: the channel of compensating differences is closed

- X: basic needs are provided unconditionally; The system does not imply large differences in payment (otherwise inequality returns).
- Y: a sanitation worker, a night nurse, a shift worker in the north have neither a material premium nor a status one (projects give status, routine does not).
- Z: either a large differential is introduced (inequality returns, albeit in the flow and not in the stock), or a shortage arises precisely in non-prestigious critical professions.
- Destabilization: **adverse selection with equal division and free exit**. Abramitsky's work on kibbutzim: with an equal division, the most productive ones leave first, which worsens the balance and increases the pressure to move away from equality. Kibbutzim remained for decades based on ideology and mutual control in a small group and were privatized in the 1990s and 2000s, as generations changed and external opportunities grew. This is a general result, not an Israeli peculiarity.

---

## M18. “Rules can only be changed by the decision of citizens” - refusal of the constitutional level

- X: any rule (including the size of the dividend, property prohibition, financing conditions) is changed by the current decision.
- Y: the planning horizon of any project is limited by the stability horizon of the rules.
- Z: no one takes on 20-year commitments, because in a year the rules may change; plus there is a constant struggle to change the rules as a cheap way of redistribution.
- Destabilization: Buchanan-Tullock: the constitutional level must change **more difficult** than the operational level, otherwise operational conflicts are transferred to the constitutional level. The concept explicitly abandons this distinction.

---

## M19. The system is not decentralized in an institutional sense

The work requires **single** and **single**:
- unit of account and register of balances of all citizens;
- citizenship register (who receives the dividend);
- Sibyl-resistant personality registry;
- definition and enforcement of the ban on private ownership of the means of production;
- audit infrastructure “decision → rule → data → calculation → output.”

This is the most centralized **institutional core** with decentralized decision-making from above. The state has not been eliminated—it has been made invisible and therefore unaccountable. An analogy from the crypto world: “decentralized” networks in practice depend on a few clients, a few development teams, exchanges and bridges - and this is where takeovers occur.

---

##M20. There is no theory of boundaries: entry, exit, children, migrants, the outside world

- Inheritance of savings - see M9.
- Migrants: from what day is the dividend? Any answer creates either an incentive for mass entry or a second class of residents without a share (which reproduces the class division).
- The outside world: if the rest of the world is capitalist - (a) leakage of the most productive (Abramitsky’s logic plus brain drain), (b) an inconvertible internal unit does not buy imports, then a state monopolist of foreign trade is needed (another prohibited body).
- If worldwide acceptance is assumed, this is an assumption greater than the rest of the structure.

---

## M21. Second round: inequality of influence is restored without inequality of stock

Even with a perfectly equal monthly dividend:
- a successful project manager accumulates reputation, network, information and access to expertise;
- Matthew effect (Merton; DiPrete & Eirich): success increases the likelihood of the next success, regardless of quality;
- his next project raises funding faster and cheaper.

**Bottom line:** equality of stock does not imply equality of influence. And influence is converted into the disposal of resources - that is, the very thing for the sake of eliminating which property was prohibited. The answer to questions 2 and 3 is: **yes**, only through the reputation and delegation channel, not through legal title. And this channel cannot be closed without banning the reputation.