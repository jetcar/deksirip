# Graph Report - novel-shestoy-punkt  (2026-10-27)

## Corpus Check
- 74 files · ~113,686 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 553 nodes · 1742 edges · 17 communities (16 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 104 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Премиса и шестой пункт
- Начало: салон и тело Ники
- Эстетика Плюс изнутри
- Вольский и предложение
- Оля и память ткани
- Колечки и мастерская Ганца
- Вольский: признание и арест
- Долг Гвоздю и краденые колечки
- Протоколы и суд
- Драка умеющих
- Белый лотос и Лариса
- Как держать узел
- Подвал клиники
- Убийство Ремизова
- Мышцы Гены и белье
- Тело Вольского
- Настя и Вадик

## God Nodes (most connected - your core abstractions)
1. `World — указатель мира` - 45 edges
2. `Глава 15. Марат` - 39 edges
3. `Вероника Павловна Зорина (Ника)` - 39 edges
4. `Глава 7. Сарафанное радио` - 37 edges
5. `Ника (Вероника Зорина) — косметолог, бывшая операционная сестра` - 36 edges
6. `Глава 19. Шестой пункт` - 36 edges
7. `Аркадий Львович Вольский` - 36 edges
8. `Вероника «Ника» Зорина` - 36 edges
9. `Глава 5. Возвращение` - 34 edges
10. `Глава 21. Как держат узел` - 34 edges

## Surprising Connections (you probably didn't know these)
- `Верхнегорск` --semantically_similar_to--> `Верхнегорск`  [INFERRED] [semantically similar]
  chapters/08-kolechko.md → bible/world/verkhnegorsk.md
- `Салон «Белый лотос»` --semantically_similar_to--> `Салон «Белый лотос»`  [INFERRED] [semantically similar]
  chapters/01-stakan-vody.md → bible/world/belyy-lotos.md
- `Шестой пункт: «Живое не трогать»` --semantically_similar_to--> `Шестой пункт — «Живое не трогать»`  [INFERRED] [semantically similar]
  chapters/01-stakan-vody.md → bible/world/shestoy-punkt.md
- `Магазин белья «Шёпот»` --semantically_similar_to--> `Магазин белья «Шёпот»`  [INFERRED] [semantically similar]
  chapters/04-lipofiling-bez-kanyuli.md → bible/world/shyopot.md
- `Марат Ильдарович Гараев — патологоанатом` --semantically_similar_to--> `Марат Ильдарович Гараев (патологоанатом)`  [INFERRED] [semantically similar]
  chapters/04-lipofiling-bez-kanyuli.md → bible/world/doklad-garaeva.md

## Hyperedges (group relationships)
- **Собственные правила безопасности Ники** — chapters_02_myortvoe_na_zhivom_vannochku_vsegda_stav, chapters_03_zhir_eto_toplivo_mozg_platit_sakharom, chapters_03_zhir_eto_toplivo_kletki_slyshat_drug_druga, chapters_04_lipofiling_bez_kanyuli_tochnost_ravna_ponimaniyu, chapters_04_lipofiling_bez_kanyuli_klast_nityami, chapters_07_sarafannoe_radio_informirovannoe_soglasie [INFERRED 0.85]
- **Цепь поколений колечек от Гранска** — chapters_01_stakan_vody_gransk, chapters_01_stakan_vody_kolechko, chapters_02_myortvoe_na_zhivom_kolechko_5_pokoleniya, chapters_02_myortvoe_na_zhivom_kolechko_6_pokoleniya, chapters_02_myortvoe_na_zhivom_vadik, chapters_02_myortvoe_na_zhivom_lev_borisovich_gants [EXTRACTED 1.00]
- **Осложнения перестройки живого** — chapters_03_zhir_eto_toplivo_goroshina, chapters_04_lipofiling_bez_kanyuli_maslyanaya_kista, chapters_04_lipofiling_bez_kanyuli_ekstrasistola, chapters_03_zhir_eto_toplivo_gipoglikemiya, chapters_06_olya_pereokhlazhdenie_nog_oli, chapters_07_sarafannoe_radio_asimmetriya_guby, chapters_05_vozvrashchenie_ukreplennyi_sustav [INFERRED 0.85]
- **Долговой конвейер: ломбарды → подвал клиники** — chapters_08_kolechko_lombard_24, chapters_08_kolechko_vadik, chapters_11_dobrovolets_liza_kovaleva, chapters_12_myshtsy_gena, chapters_12_myshtsy_stepa, chapters_09_predlozhenie_seraya_dver, chapters_08_kolechko_volskiy [EXTRACTED 1.00]
- **Расследование смерти Ремизова** — chapters_08_kolechko_vetrov, chapters_08_kolechko_garaev, chapters_08_kolechko_veronika_zorina, chapters_14_protokol_zapis_stimulyatora, chapters_14_protokol_ubiystvo_rukami, chapters_14_protokol_letniy_skupshchik [EXTRACTED 1.00]
- **Поколения колечек (6→5→4→3→2)** — chapters_08_kolechko_kolechko, chapters_08_kolechko_pyatoe_kolechko, chapters_09_predlozhenie_vtoroe_kolechko, chapters_13_skupka_tretye_kolechko, chapters_09_predlozhenie_kolechko_pod_kozhey, chapters_08_kolechko_reestr_kolechek [INFERRED 0.85]
- **Цепочка поколений колечек (2→3→4)** — chapters_15_marat_kolechko_vtoroe, chapters_15_marat_eduard_krylov, chapters_20_boytsy_kolechko_vshitoe, chapters_20_boytsy_novye_boytsy, chapters_15_marat_volsky [EXTRACTED 1.00]
- **Узел держащих в читальном зале** — chapters_15_marat_olya, chapters_21_kak_derzhat_uzel_galina_stepanovna, chapters_21_kak_derzhat_uzel_pensionerki, chapters_19_shestoy_punkt_petr_sanych, chapters_19_shestoy_punkt_kira, chapters_18_pervaya_draka_svetka_kononova, chapters_15_marat_marat_garaev, chapters_19_shestoy_punkt_lev_borisovich, chapters_21_kak_derzhat_uzel_eksperiment_olya [EXTRACTED 1.00]
- **Жертвы пробуждённого деления** — chapters_15_marat_nadya_kuznetsova, chapters_15_marat_stepa, chapters_15_marat_liza, chapters_15_marat_delenie_vklyuchennoe_snaruzhi [INFERRED 0.85]
- **Цепочка держания в подвале** — chapters_22_telo_volskogo_veronika_zorina, chapters_23_klinika_nochyu_tolya, chapters_22_telo_volskogo_lapin, chapters_22_telo_volskogo_alla_vitalevna, chapters_23_klinika_nochyu_savelyev, chapters_23_klinika_nochyu_zinaida_petrovna, chapters_23_klinika_nochyu_danya_vetrov [EXTRACTED 1.00]
- **Мастерская держит батареи наверху** — chapters_23_klinika_nochyu_lev_borisovich, chapters_22_telo_volskogo_olya, chapters_22_telo_volskogo_gena, chapters_23_klinika_nochyu_pyotr_sanych, chapters_23_klinika_nochyu_galina_stepanovna, chapters_24_draka_umeyushchikh_nina_mikhaylovna, chapters_24_draka_umeyushchikh_rimma_fyodorovna, chapters_24_draka_umeyushchikh_tyotya_masha, chapters_24_draka_umeyushchikh_svetka [EXTRACTED 1.00]
- **Авторы раздела «Живое»** — chapters_22_telo_volskogo_veronika_zorina, chapters_22_telo_volskogo_garaev, chapters_23_klinika_nochyu_danya_vetrov, chapters_27_razdel_zhivoe_razdel_zhivoe [EXTRACTED 1.00]
- **Цена перестройки: тепло, сахар, жир, налог** — bible_world_raskhod_raskhod, bible_world_zhir_toplivo_zhir_toplivo, bible_world_perekladyvanie_zhira_nalog, bible_world_posobie_razdel_energiya, bible_world_perekladyvanie_zhira_perekladyvanie_zhira [INFERRED 0.85]
- **Договариваться с тканью вместо ломать** — bible_world_vozvrashchenie_zhivogo_vozvrashchenie_zhivogo, bible_world_zov_krovi_zov_krovi, bible_world_kak_derzhat_uzel_kak_derzhat_uzel, bible_world_vozvrashchenie_zhivogo_tkan_pomnit_prichinu, bible_world_shestoy_punkt_niki_shestoy_punkt_niki [INFERRED 0.85]
- **Оборот колечек: реестр, чёрный рынок, скупки** — bible_world_kolechko_kolechko, bible_world_reestr_kolechek_reestr_kolechek, bible_world_chernyy_rynok_kolechek_chernyy_rynok_kolechek, bible_world_lombard_24_lombard_24, bible_world_skupka_remizova_skupka_remizova, bible_world_masterskaya_biblioteka_masterskaya_biblioteka [EXTRACTED 1.00]

## Communities (17 total, 1 thin omitted)

### Community 0 - "Премиса и шестой пункт"
Cohesion: 0.06
Nodes (83): Дар к мягкому (кожа, жир, вода), Гранск, Гвоздь — Станислав Гордеев, Цикл «Материальный вопрос», Вероника «Ника» Зорина, Шестой пункт — премиса романа, Аркадий Львович Вольский (хирург), World — указатель мира (+75 more)

### Community 1 - "Начало: салон и тело Ники"
Cohesion: 0.06
Nodes (88): Глава 1. Стакан воды, Салон «Белый лотос», Бежевый лифчик с поролоном («бельё, которое врёт»), Запись о дрожжевом тесте, переставшем подниматься, Городская больница (хирургия), Гранск — город-источник перестройки и колечек, Ипполит — золотая рыбка Ники, «свидетель», Кирилл — бывший муж Ники (+80 more)

### Community 2 - "Эстетика Плюс изнутри"
Cohesion: 0.07
Nodes (104): Глава 15. Марат, Алла Витальевна, старшая сестра «Эстетики Плюс», Анжелика Сергеевна, клиентка (грудь), Даня Ветров, капитан, группа по перестройке, сапёр, Деление, включённое снаружи (стимуляция клеток-предшественников), Эдуард Геннадьевич Крылов, хирург клиники, Электронный журнал выдачи колечек Аллы Витальевны, Клиника «Эстетика Плюс» (Театральная) (+96 more)

### Community 3 - "Вольский и предложение"
Cohesion: 0.12
Nodes (28): Клиника «Эстетика Плюс», Регина Аркадьевна, Аркадий Львович Вольский, Биопсии Вольского у Гараева, Глава 9. Предложение, Денис (юрист клиники), Эдуард Геннадьевич Крылов, Фотографии осложнений Эдуарда (+20 more)

### Community 4 - "Оля и память ткани"
Cohesion: 0.11
Nodes (16): Людмила (УЗИ), Граница на лице (возврат кожи), Ипполит (рыбка в банке), Оля Синичкина, Вероника Павловна Зорина (Ника), Глюкометр Вероники, Мама Вероники, Синий балконет из «Шёпота» (+8 more)

### Community 5 - "Колечки и мастерская Ганца"
Cohesion: 0.13
Nodes (22): Чувство металла (свищ на трубе), Группа по перестройке (городское управление), Колечко (поколения колец), Лев Борисович Ганц, Опыт со стаканом воды (охлаждение), Колечко пятого поколения со спиленным номером, Реестр колечек (номера, очередь), Вероника Павловна Зорина (Ника) (+14 more)

### Community 6 - "Вольский: признание и арест"
Cohesion: 0.19
Nodes (18): Эдуард Геннадьевич, Сергей Олегович Лапин, Лиза Кузнецова, Надя (Надежда Ивановна Кузнецова), Отказ Вольского от госпитализации, Признание Вольского про Надю («моя ошибка»), Рабдомиолиз Вольского, Аркадий Львович Вольский (+10 more)

### Community 7 - "Долг Гвоздю и краденые колечки"
Cohesion: 0.19
Nodes (17): Долг 150 чисток Вадику, Станислав Игоревич Гордеев (Гвоздь), Спиленные номера (краденые колечки), Вадик (Вадим), Гранск, Колечко второго поколения (аренда), Пособие (второе издание), Стёпа (мальчик с рюкзаком) (+9 more)

### Community 8 - "Протоколы и суд"
Cohesion: 0.18
Nodes (16): Вшитое колечко второго поколения Вольского, Папка Вольского (компромат), Свищ над колечком, Лев Борисович (Ганц), Шестое колечко мастерской, Глава 26. Протоколы, Инна Марковна Шаповалова, адвокат, Колечко №641 пятого поколения (бывшее Вероники) (+8 more)

### Community 9 - "Драка умеющих"
Cohesion: 0.18
Nodes (16): Марат Ильдарович Гараев, Даня (Даниил Сергеевич Ветров), сапёр-полицейский, Металл здания как единый кусок (стояки, батареи), Трое бойцов Вольского (вшитые колечки), Глава 24. Драка умеющих, Держание батарей наверху (сорок минут), Подкрепление полиции, Вольский отпускает всё сразу (+8 more)

### Community 10 - "Белый лотос и Лариса"
Cohesion: 0.17
Nodes (15): Анонимная жалоба на салон, Салон «Белый лотос», Глава 8. Колечко, Сделка с Ларисой: кабинет 60/40, Лариса Викторовна, Сеть «Ломбард 24» (жёлтые с чёрным), Ломбард на Горной, Людмила (УЗИ на Строителей) (+7 more)

### Community 11 - "Как держать узел"
Cohesion: 0.16
Nodes (14): Библиотека (читальный зал), «Девять человек — раз в десять» (держание в библиотеке), Гена, Стёпа, Пётр Саныч, Мастерская Ганца («умеющие чуть-чуть»), Нина Михайловна, Пустая строчка в журнале (не взял трубку) (+6 more)

### Community 12 - "Подвал клиники"
Cohesion: 0.18
Nodes (12): Гараж у Гордеева, Станислав Игоревич Гордеев, Кира, Клиника «Эстетика Плюс» на Театральной, Подвал клиники (четыре палаты), Савельев, Серая стальная дверь в подвал, Сервер с записями камер (+4 more)

### Community 13 - "Убийство Ремизова"
Cohesion: 0.29
Nodes (10): Марат Ильдарович Гараев, Ипполит (рыбка), Медный провод от стояка (ложный след), Смерть Ремизова, Кардиостимулятор Ремизова (память прибора), Глава 14. Протокол, Объяснение Ники о Гордееве, Первая палата — «выписали» (+2 more)

### Community 14 - "Мышцы Гены и белье"
Cohesion: 0.22
Nodes (10): Отец боксёра (Артёма), «Сделай кулак» (заказ на кисти), Магазин белья «Шёпот», Бордовый комплект белья, Глава 12. Мышцы, Гена (грузчик, «учебник»), Конвейер: ломбарды Гвоздя → клиника Вольского, Ника и Даня: первая ночь (+2 more)

### Community 15 - "Тело Вольского"
Cohesion: 0.36
Nodes (10): Алла Витальевна, Глава 22. Тело Вольского, Две кровати, застеленные в подвале, Ночь капельницы на Садовой, Квартира Вольского на Садовой, Долг как средство принуждения, Толя, шиномонтажник, Зинаида Петровна (Зина) (+2 more)

## Ambiguous Edges - Review These
- `Вадик — продавец колечек` → `Отец Артёма — мужчина в дублёнке с золотой цепью`  [AMBIGUOUS]
  chapters/07-sarafannoe-radio.md · relation: conceptually_related_to
- `Отец Артёма — мужчина в дублёнке с золотой цепью` → `Анонимная жалоба на салон`  [AMBIGUOUS]
  chapters/07-sarafannoe-radio.md · relation: references
- `Эдуард Геннадьевич Крылов` → `Убийство руками: дрожь грудной мышцы`  [AMBIGUOUS]
  chapters/14-protokol.md · relation: conceptually_related_to
- `Убийство руками: дрожь грудной мышцы` → `Расписание: Эдуард «перенесено» в среду 13:00`  [AMBIGUOUS]
  chapters/14-protokol.md · relation: conceptually_related_to
- `Шестое колечко мастерской` → `Толстый ответ из Гранска (с круглым предметом внутри)`  [AMBIGUOUS]
  chapters/28-svoyo-telo.md · relation: semantically_similar_to

## Knowledge Gaps
- **32 isolated node(s):** `Людмила (УЗИ на Строителей)`, `Чувство металла (свищ на трубе)`, `Колечко Вольского под кожей запястья`, `Пакеты клиники («Невеста» и др.)`, `Савельев (электрика)` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 38 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Вероника Павловна Зорина (Ника)` connect `Оля и память ткани` to `Колечки и мастерская Ганца`, `Вольский: признание и арест`, `Протоколы и суд`, `Драка умеющих`, `Как держать узел`, `Подвал клиники`, `Тело Вольского`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Вероника Павловна Зорина (Ника)` (e.g. with `Вероника Павловна Зорина (Ника)` and `Станислав Игоревич Гордеев`) actually correct?**
  _`Вероника Павловна Зорина (Ника)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Людмила (УЗИ на Строителей)`, `Чувство металла (свищ на трубе)`, `Колечко Вольского под кожей запястья` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Премиса и шестой пункт` be split into smaller, more focused modules?**
  _Cohesion score 0.06386743886743887 - nodes in this community are weakly interconnected._
- **Why does `Станислав Игоревич Гордеев` connect `Подвал клиники` to `Эстетика Плюс изнутри`, `Как держать узел`, `Оля и память ткани`, `Вольский: признание и арест`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Вадик — продавец колечек` and `Отец Артёма — мужчина в дублёнке с золотой цепью`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Отец Артёма — мужчина в дублёнке с золотой цепью` and `Анонимная жалоба на салон`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._