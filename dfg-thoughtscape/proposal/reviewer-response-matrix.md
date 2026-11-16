# How the new proposal answers the OB 607/1-1 reviews

Source: "Stellungnahmen zum Antrag" (Gutachten 1, Gutachten 2, Fachkollegium). Section numbers refer to `dfg-proposal-thoughtscape.md`.

| # | Criticism (paraphrased) | Reviewer | What changed | Where |
|---|---|---|---|---|
| 1 | Much of the focus is on well-covered ground (building knowledge tracing and adaptivity) | R1 | No KT model, no adaptive system, no RL, no knowledge graph. KT only as a baseline in the validity test | 1.1, 1.4, 2.3 WP2 |
| 2 | Novelty not clearly articulated; contrast with ITS and adaptive-learning research missing | R1 | Gaps G1–G3 stated; explicit contrast with KT, Error Quotient, ITS/example-tracing, concept-map assessment, LLM tutors | 1.1 |
| 3 | The key adoption question: why are these technologies not used more? Pedagogical integration and usability for teachers barely discussed | R1 | RQ3 and WP3: co-design, decision experiment, classroom field study; estimation-focused | 2.2, 2.3 WP3 |
| 4 | No specification of educational context, data gathering, or partner institutions | R1, Fachkollegium | Two named courses (DBMS, ML) at two sites with instructors; letters of support to be attached; corpus plan with sample-size justification | 2.3 (partner courses, WP1) |
| 5 | Severe risk the models fail in pilots | R1 | Risk table with responses; negative results planned as publishable; fallback sample | 2.3 risks |
| 6 | WP1, 2, 4, 5 are system development in line with prior work; novelty concentrated in WP3 | R1 | Four WPs, none is platform development; every WP produces a research result (codebook/corpus, validated metrics/fairness, decision evidence) | 1.4, 2.3 |
| 7 | WP3 integrates existing XAI/fairness rather than novel approaches | R1 | Replaced by testable contributions: expert-validated probe benchmark, comparison of four metric families, fairness audit of *process* metrics (almost unstudied) | 2.2 RQ2, 2.3 WP2 |
| 8 | User studies under-specified (recruitment, N, usability, protocol) | R1 | Study designs, N, conditions, outcomes, analysis, and power/estimation logic given for each study | 2.3 WP1 T1.4, WP3 T3.2–T3.3 |
| 9 | Research environment lists only compute; partnerships and data infrastructure missing | R1 | Partners and data-management plan; EU hosting; research data centre option | 2.3, 2.4 |
| 10 | Three workstations are basic equipment | R1 | Removed; no equipment requested | 4.10, 5.1 |
| 11 | Educators insufficiently involved in system and study design | R1 | Instructors co-design views and decisions (three cycles) and gold sets | 2.3 WP1 T1.3, WP3 T3.1 |
| 12 | Lacks theoretical grounding from the learning sciences; constructs ("knowledge", "personalised learning") undefined | R2, Fachkollegium | Evidence-centred design framework; five constructs tied to theory (ICAP, self-explanation, conceptual vs procedural knowledge, learning from errors, productive failure); explicit statement of what is and is not claimed | 1.2 (Table 1) |
| 13 | Knowledge treated as one entity; procedural/declarative/conceptual not distinguished | R2 | Construct C2 maps node kinds to knowledge types; checked against expert coding | 1.2, 2.3 WP1 |
| 14 | "Figure 1" reads as a catalogue of ML techniques; EDM/LA introduction superficial | R2 | Catalogue dropped; construct-to-evidence map replaces it; state of the art rewritten | 1.1, 1.2 |
| 15 | Knowledge-representation objective lacks novelty | R2 | Dropped | 1.4 |
| 16 | "Universally scalable system" questionable | R2 | Claims restricted to technical university labs; no scalability objective | 1.4, 2.2 |
| 17 | Work programme gives only a rough idea of the doctoral student's tasks; time for own qualification? | R2 | Person-months per WP, thesis chapter plan, about 20% time for qualification, four planned papers | 2.3 staffing |
| 18 | Scope too broad for one PI, one PhD and two assistants | R2, Fachkollegium | Four WPs, no development, one PhD, one assistant, PI own position | 1.4, 2.3 |
| 19 | No formal data management plan | R2 | DMP following the DFG checklist headings, with platform-specific points (sign-in mode, retention) | 2.4 |
| 20 | Fairness and XAI by design are strengths | R2 | Kept but narrowed to what can be measured: fairness of process metrics; interpretability through the visible tree | 2.2 RQ2, 2.3 T2.4 |

**Added because the review did not ask but the code review showed it:** the shipped similarity step is a 64-dimension hashed n-gram vector, and a stress test (n = 22) shows it does not separate a faithful rewording from a one-word error (Section 1.3). The project turns this into its central research problem rather than hiding it.

**Still open and only the applicant can settle:** partner courses and letters; eligibility route and host statement (Section 4.2); own publications (Sections 1.3d, 3); ethics committees; hosting region of the production database; budget rates; DFG rules on resubmission after rejection.
