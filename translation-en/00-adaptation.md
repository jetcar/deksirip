# English adaptation: style bible and glossary

This file holds the canonical rules for translating both novels of the «Материальный вопрос» cycle into English for an American reader. Every translated chapter must follow it. When a chapter introduces a name, place, institution or recurring phrase that is not listed here, the translator picks an English form, uses it, and **adds it to the right table below in the same commit**. A name chosen once is never changed later without updating every translated chapter.

Sources:
- Book 1, «Материальный вопрос» → **A Material Question**: `novel-materia/chapters/` (submodule), plan `novel-materia/00-plan.md`.
- Book 2, «Шестой пункт» → **Rule Six**: `novel-shestoy-punkt/chapters/`, plan `novel-shestoy-punkt/00-plan.md`.

Output:
- `translation-en/book1-a-material-question/chapters/NN-english-slug.md`
- `translation-en/book2-rule-six/chapters/NN-english-slug.md`
- Heading: `# Chapter N. Title`.

## Goals

1. A literary translation, not a gloss. It should read as if written in American English: idiomatic dialogue, American rhythm of jokes, no calques ("he said to me that…", "well, so"), no transliterated interjections.
2. Faithful to plot, facts, numbers, costs and magic rules. Nothing is cut or added beyond what an adaptation needs. If a joke depends on Russian wordplay, replace it with an English joke of the same weight and note the change in the progress log.
3. Same narrator voice: book 1 — Tim, first person, conversational, wry, back-of-the-napkin estimates; book 2 — Nikki, first person, precise, medical, sardonic, bodily.
4. Content rules stay exactly as in the originals: adults only, explicit consent in dialogue, the act itself is never described (fade-out), violence without relish and without technical instructions for weapons, lock-picking or causing harm.
5. Book 1 and book 2 share one world: names and terms from book 1 that book 2 mentions (Granton, the manual, the thimble) must match.

## Setting adaptation (America-like, still fictional)

- The country stays unnamed, as in the originals, but everyday texture is American: streets, food, institutions, units, money habits, paperwork.
- Book 1 town **Гранск → Granton**: a small Rust Belt college town with a flea/farmers market and a state polytechnic ("the Poly").
- Book 2 city **Верхнегорск → Highridge**: a regional mountain city with a steel mill, private clinics downtown and housing on the hillsides.
- **Money.** The currency is still never named. Keep the original figures exactly (so continuity and arithmetic hold). Characters' private units are adapted:
  - Book 1: Tim counts in **bags of frozen pierogi** (one bag = 189). "Пачка пельменей" → "a bag of pierogi".
  - Book 2: Nikki counts in **facials** (one facial = what she makes in an hour at the salon). "Чистка (лица)" → "a facial".
  - Calories stay kilocalories → write "calories" (American usage).
- **Units.**
  - Everyday: Fahrenheit for weather and room temperature, feet/inches/miles, pounds for body weight (convert, round sensibly: 59 kg → 130 lb; 57.6 kg → 127 lb), gallons for bathtubs.
  - Medical and lab: keep metric — grams of fat, millimeters, centimeters, milliliters; fever in °F (38.4 °C → 101.1 °F); blood glucose in mg/dL (4.2 mmol/L → 76 mg/dL); blood pressure unchanged.
  - The glass-of-water test stays in °C, as a lab measurement: "minus nine tenths of a degree against the control".
- **Institutions** (by function, American equivalents):
  - налоговая → the tax office / Revenue Department; налоговый инспектор → revenue auditor.
  - управляющая компания → property management company; ЖКХ/коммуналка → utilities.
  - горсовет → city council; депутат горсовета → city councilman.
  - самозанятость → registering as self-employed / a sole proprietor.
  - микрозайм → payday loan; коллектор → debt collector.
  - политех → the Poly (state polytechnic); кафедра химии → the chemistry department; лаборант → lab tech.
  - полиция, следователь → police, detective; группа по перестройке → the Reshaping Unit.
  - мировой суд / административный штраф → municipal court / civil fine.
  - адвокат → attorney; протокол допроса → interview transcript / statement.
  - медицинский колледж → nursing school; операционная медсестра → OR nurse (scrub nurse); патанатом → pathologist; патанатомия → the pathology department; приёмное отделение → the ER; реанимация → the ICU; городская больница → County General (Highridge County General).
  - ломбард → pawn shop; скупка → buy-and-sell shop.
  - подъезд → the building / the stairwell; хрущёвка, панелька → a walk-up apartment building.
- **Food and daily life.** Пироги → hand pies or pie as fits; сметана → sour cream; гречка → oatmeal or rice as the role demands (a cheap, filling breakfast); чай с сахаром stays sweet tea; огурцы в банке → jarred pickles; пуховик → puffer jacket; дача → cabin / weekend place.
- **Names of real cities, brands, countries**: none, as in the originals.

## Core terms

| Russian | English |
|---|---|
| перестройка (вещества), перестраивать | reshaping (matter), to reshape |
| пособие «Перестройка вещества руками» | the manual, *Reshaping Matter by Hand* |
| напёрсток | the thimble |
| колечко (поколение N) | ring (Nth generation) |
| ученический напёрсток | student thimble |
| умеющий | a shaper |
| мастерская | the workshop |
| Обменник | the Exchange |
| методичка | the handbook |
| стакан воды (проба) | the glass-of-water test |
| к контролю | against the control (glass) |
| шестой пункт | Rule Six |
| «Живое не трогать» | "Don't touch the living" |
| держать (узел) | to hold (the knot) |
| «Как держать узел» | "How to Hold the Knot" |
| налог (при переносе жира через кровь) | the tax |
| зов крови | calling the blood |
| ванночка | the foot basin |

## Characters — book 1 (*A Material Question*)

| Russian | English | Notes |
|---|---|---|
| Тимофей «Тима» Гвоздев, 32 | Timothy "Tim" Nagel, 32 | narrator; fix-it man at the market |
| Валерия «Лера» Синицына, 29 | Valerie "Val" Finch, 29 | chemistry lab tech at the Poly |
| Белла Марковна Штерн, 78 | Bella Stern, 78 ("Mrs. Stern") | professor's widow |
| профессор Штерн | Professor Stern | materials scientist, deceased |
| Ашот Саркисян, 55 | Ashot Sarkisian, 55 | cobbler, Armenian-American |
| Зоя Ивановна, 71 | Dorothy "Dot" Mazur, 71 ("Mrs. Mazur") | neighbor, retired factory cafeteria cook |
| Миша Кравец, 15 | Mikey Kravitz, 15 | teenage hacker, neighbor |
| Георгий «Жора» Бык, 40 | George "Bull" Bykowski, 40 | debt collector; contact saved as "Don't Answer" |
| Нина Петровна Звягина, 58 | Nina Pratt, 58 ("Ms. Pratt") | revenue auditor |
| Злата Кочетова, 30 | Goldie Cochran, 30 | attorney, developer's daughter |
| Вадим Кочетов, 60 | Vance Cochran, 60 | developer, city councilman |
| Глеб Ржевский, 45 | Glen Rusk, 45 | Stern's former grad student, second thimble |
| Пал Палыч | Pete Palmer ("Old Pete") | conspiracy-theorist neighbor |
| Рикардо | Ricardo | (keep) |
| кот Шуруп | Lugnut the cat | steals shiny things |
| мама Тимы | Tim's mom | calls from the country |
| Семён Аркадьевич | Mr. Abrams (Sy Abrams) | owns Tim's booth (a row of booths) at the market; not to be confused with Arkady Semyonovich of ch. 5 |
| Аркадий Семёнович | Professor Arkin | Tim's old crystallography professor ("Nagel, without structure there are no properties"); first appears ch. 2, recurs ch. 3–5 |
| Лёха Курган, 43 | Lenny Kurgan, 43 | bald, gold tooth; runs the BUY & SELL. SCRAP METAL. BATTERIES. container behind the market; calls Tim "Timmy" (Тимоха); first appears ch. 4, recurs |
| Серый | Sarge | Lenny's muscle (from Сергей); first appears ch. 4 |

## Characters — book 2 (*Rule Six*)

| Russian | English | Notes |
|---|---|---|
| Вероника «Ника» Зорина, 29 | Veronica "Nikki" Zorn, 29 | narrator; esthetician, former OR nurse |
| Даниил «Даня» Ветров, 34 | Daniel "Danny" Gale, 34 | Reshaping Unit cop, ex-EOD, ex-welder |
| Аркадий Львович Вольский, 52 | Dr. Arthur Wolfe, 52 | plastic surgeon, owner of Aesthetica Plus |
| Станислав «Стас» Гордеев, «Гвоздь», 40 | Stan Gordon, "Spike", 40 | pawn-shop boss |
| Марат Ильдарович Гараев, 61 | Dr. Martin Garrity, 61 | pathologist, County General |
| Оля (Ольга Андреевна) Синичкина, 24 | Ollie (Olivia) Sinclair, 24 | salon receptionist, best friend |
| Тамара Петровна Зорина, 55 | Tammy Zorn, 55 ("Mom") | retired bookkeeper |
| Лиза (Елизавета Романовна) Ковалёва, 19 | Liz Cole, 19 | Wolfe's "volunteer" |
| Ипполит (золотая рыбка) | Ignatius the goldfish | |
| Лев Борисович Ганц | Leo Gantz ("Mr. Gantz") | runs the library workshop, ex-physics teacher |
| Кирилл (бывший муж) | Kyle (ex-husband) | |
| Лариса Викторовна | Laurie Victor | salon owner |
| Алла Витальевна | Alma Vitale | nurse at the clinic |
| Эдуард Геннадьевич Крылов | Eddie Krill (Edward Krill) | Wolfe's shaper |
| Ирина Петровна | Irene Peterson | anesthesiologist |
| Денис | Dennis | Wolfe's lawyer |
| Вадик | Vic | Spike's man |
| Лапин | Detective Lane | investigator |
| Людмила | Mila | ultrasound tech |
| Регина Аркадьевна | Regina Arcadian ("Mrs. Arcadian") | early client |
| Анжелика Сергеевна | Angelica Sergeant ("Mrs. Sergeant") | clinic client |
| Марина Колесникова | Marina Kessler | lip client |
| Галина Степановна | Galina Stepp ("Mrs. Stepp") | heels client |
| Надежда Ивановна Кузнецова (Надя) | Nadine Kuzma ("Nadia") | died after the "procedure" |
| Гена | Gene | debtor, muscles |
| Стёпа | Stevie | 18, fighter |
| Римма Фёдоровна | Rhoda Fedorov (kept her own surname) | Spike's mother |
| Пётр Саныч | Walt Sanders | workshop driver |
| Светка (Кононова) | Stacy Conner | surgical nurse friend |
| Инна Марковна Шаповалова | Inna Shaw | attorney |
| Валентина Семёновна | Valentina Simmons ("Mrs. Simmons") | landlady |
| Савельев, Кира | Savell, Kira | police officers |
| Ремизов | Ray Remy | murdered rival pawnbroker |

Book 1 places and recurring phrases: рынок Гранска → the Granton market; будка → the booth; «Ремонт всего» (sign) → "We Fix Everything"; мясные ряды → the meat aisle; тётка с семечками → the sunflower-seed lady; пирожок (с капустой/картошкой) → hand pie (cabbage/potato); считать столбиком → thinking "in a column"; квитанция (Tim's notes) → receipt; микрозайм → payday loan; гаечный ключ на двенадцать → half-inch wrench; левая резьба → left-hand thread; ложка «Общепит» → a CAFETERIA spoon (stamped on the handle); тетрадка «Испытания» → the "Trials" notebook; разница (купить vs сделать) → "the difference"; стояк → the riser (heating riser); батарея → radiator; аварийка → the emergency line; котельная → the boiler; седло крана → the (faucet) seat; кладовка-«приют» → the closet, "the shelter"; однокомнатная → one room plus a kitchen; валенки (Zoya) → felt-lined boots; форточка → transom window. Added ch. 3: табличка Пал Палыча «Не звонить. Знаю» → "DON'T RING. I KNOW." (his refrain «Знаю» → "I know"); дерматин (door padding) → leatherette; шпроты → a can of smoked sardines; чебурек → a fried meat pie (from the stand by the gate); термос → thermos; канифоль → rosin; лупа (на лбу) → magnifier visor; тестер → multimeter; авоська → string bag; ставня (будки) → the shutter; мастерская за углом (ordinary repair shop) → the repair shop around the corner (never "workshop", which is reserved for the core term); «Дядя Тим» (Mikey) → "Tim" / "Hey, Tim"; «Ремонт с гарантией» → "Repairs are guaranteed"; моральный ущерб → pain and suffering. Added ch. 4: отцовский ящик для рыбалки → my father's tackle box; грузила → sinkers; поплавки → bobbers; резиновые сапоги (рыбацкие) → knee-high rubber fishing boots; удлинитель → extension cord; фаза → the live wire; пробки (фарфоровые) → the (old porcelain) fuses; жучок → copper wire jammed in place of a fuse; автомат подъезда / щиток → the breaker for the whole stairwell / the panel on the first floor; третий подъезд → stairwell three; горошина (золота) → the pea; пылинка → a speck; банка из-под кофе → coffee can; советские (военные) платы → old military-surplus boards ("the golden ones"); «Покупаем золото дорого» → TOP PRICES PAID FOR GOLD; «Скупка. Приём лома. Аккумуляторы» → BUY & SELL. SCRAP METAL. BATTERIES.; четыре девятки / 99,99 → four nines / ninety-nine point nine nine, bank grade; гаражи за рынком → the garages behind the market (a maze); гараж номер сорок семь → garage number forty-seven; засов-лапша → the bolt went soft as a noodle; фантик «Белый медведь» → a Polar Bear candy wrapper; Шуруп's тайник → his stash; гайка на двенадцать → a half-inch nut; справочники → reference books (never "handbook").

Street names (book 2): Театральная → Theater Street; Садовая → Garden Street; Литейная → Foundry Street; Горная → Ridge Street; Кирова → Kerr Street; Ленина → Lincoln Avenue; Строителей → Builders Avenue.

Businesses: «Белый лотос» → the White Orchid (salon); «Эстетика Плюс» → Aesthetica Plus; «Шёпот» → Whisper (lingerie); «Ломбард двадцать четыре» → Pawn 24.

## Translator checklist (each chapter)

1. Read this file, the source chapter in full, and the previous translated chapter (for voice and continuity).
2. Translate the whole chapter; keep scene breaks (`---`), paragraphing and dialogue structure.
3. Convert units per the rules above; keep money figures unchanged.
4. New names/terms → add to the tables here.
5. Write a 1–2 line entry in the progress log below: chapter, English title, any adapted jokes or notable choices.

## Progress log

- Book 1, ch. 1 «Минус сорок семь тысяч» → "Minus Forty-Seven Thousand" — done. Notes: «Не брать» → "Don't Answer"; «давайте синхронизируемся» → "let's circle back"; "pelmeni in broth is soup" → "Pierogi count as soup if you drink the water they were boiled in"; «сапожник без сапог» → "the cobbler's children go barefoot… I'm the cobbler's children of everything at once" (sets up Ashot the cobbler); набойка на зонт → a new tip on an umbrella; 5 kg → eleven pounds; 12 mm wrench → half-inch wrench; Semyon Arkadyevich → Mr. Abrams. Review: fixed debt wording, Ashot's 'half a bag', reshape wordplay (market/rebuild), calques; ok otherwise.
- Book 1, ch. 2 «Всё, что под рукой» → "Everything at Hand" — done. Notes: «Общепит» stamp → CAFETERIA ("Cafeteria spoons outlive people"); "Chinese" kitchen scale → no-name (no countries); grams kept for the scale and the nutrition label (220 cal/100 g × 800 g = 1,760 calories); Tim's notes numbered "One:/Two:" as in ch. 1; «Девятое: болт» (screw→bolt pun on Шуруп) → "Nine: the nut." (Lugnut/nut); Shurup's name-joke («ввинчивается… вывинтить невозможно») → wedges himself in like a seized lug nut, "can't get him out without a breaker bar and a lot of swearing"; «шаманство» → "a rain dance"; Arkady Semyonovich → Professor Arkin; «Гвоздев» in his line → "Nagel"; the source's early, unexplained «насос без крана» in the frost paragraph smoothed to "Something was pulling heat… like a pump with no shutoff valve" and the radiator-heat paragraph lightly reordered for logic (no content cut); only unit change: «в каждом сантиметре» → "every inch". Review: fixed doubled pump simile, thimble-vs-radiator "It", «от бабушки» → Grandma's, однокомнатная → one room plus a kitchen, "The world stepped" (matches ch. 1), shopping bag vs pierogi bags, bushing, payday lenders, felt-lined boots, assorted calques/rhythm; ok otherwise.
- Book 1, ch. 3 «Ремонт без запчастей» → "Repairs Without Parts" — done. Notes: «Китайская» (technology) → "Imported" (no countries); «Дядя Тим» → plain "Tim" (American teens don't say "uncle" to neighbors; the sincere question keeps weight via "Tim." as its own sentence); «За бесплатно не ценится» → "Nobody values what's free" (matches Mrs. Mazur in ch. 2); «институт» → college; the thermos calorie estimate kept metric as a science aside ("one gram of water, one degree"; a liter cooled to ice ≈ 180 calories, "the big kind on food labels", a tenth of a bag), as with the scale in ch. 2; «целого шкафа пельменей» → "a whole freezer full of pierogi"; «экзаменационный билет, который я не сдал» → "an exam I'd flunked once"; «склеенные клеем макароны» → "macaroni glued in a kid's art project"; the professor's bottle smashed on the lectern (кафедра); «скрутка с термоусадкой» → "twist splice with heat-shrink"; garage padlock repair kept non-technical (spring only); money math unchanged (11 → 10.5 bags, food 2.5, net 8, 24 by Friday, 56 short of 80). Review: fixed source inconsistencies (8 bags × "two more days" → "Counting today and the two days left": 24; "if I didn't eat" → "any more than today", since 8 is already net; thimble already on his finger → "turned the thimble"; "Price for what?" note now written on the back of a receipt, matching the evening scene); Ashot's kettle across the aisle; iron fix held in the fist, not the whole iron; dropped added "cracked" leatherette; shelter parts drawer, glass definition, angle iron, tense agreement, assorted calques/rhythm; ok otherwise.
- Book 1, ch. 4 «Золотой вопрос» → "The Gold Question" — done. Notes: title echoes *A Material Question*; Лёха Курган → Lenny Kurgan, Серый → Sarge, «Тимоха» → "Timmy"; «советские платы» → old military-surplus boards ("the army built its instruments as if it planned to keep fighting for another thousand years"), «со времён развала чего-нибудь большого» → "since the fall of some empire or other" (no countries); «Покупаем золото дорого» → TOP PRICES PAID FOR GOLD (no currency named); «Молодой человек» → "Hon."; «человек без ногтей» → "someone with short nails and long questions"; «как кошки в темноте — на собак» → "the way in the dark a cat can pass for a dog"; «щелбан с паровым молотом» → "a finger flick next to a pile driver"; «"никогда"… как пробка на кране» → "like a washer in a faucet: it holds until somebody turns on the water"; «фазой» → "The live wire"; жучок kept non-technical ("a bit of copper wire jammed in" the fuse); units: полкило/два кг copper → "a pound when there were four and a half"; gold kept in grams (kitchen scale, as in ch. 2) and the forum yield "a quarter of a gram per kilogram" kept metric as a science aside; гайка на двенадцать → half-inch nut. Math unchanged: 1 g ≈ 30 bags, 6 g = 180, 180 − 56 = 124 = half of 248, a third = 60, 15 = twelve times less. Source fixes: «как тянул из батареи прошлой ночью» → "two nights before" (the radiator was Tuesday night, ch. 2; this is the Wed→Thu night); «Жоре — восемь пачек вместо восьмидесяти» → "what was left of yesterday's eight bags" (ch. 3's net 8 was computed before the two evening bags of pierogi and today's eating). Review: pending.
