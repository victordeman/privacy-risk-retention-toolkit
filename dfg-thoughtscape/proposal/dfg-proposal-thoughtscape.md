---
title: "Project Description – Research Grant Proposal"
subtitle: "Are Reasoning-Trajectory Metrics Valid, Fair and Useful? Measurement Validity of Consensus-Tree Process Data in University Technical Courses (ThoughtScape)"
---

**Applicant:** Dr.-Ing. Chukwuka Victor Obionwu · **Host / mentoring applicant (to be confirmed):** Prof. Dr. Andreas Nürnberger, Otto von Guericke University Magdeburg
**Duration:** 36 months · **Funding line:** Research Grants (Sachbeihilfe) with modules *Basic Module* and *Temporary Position for Principal Investigator* (see Section 5)
**Status:** DRAFT v1, 16 Nov 2026. Text in [square brackets] marks facts that only the applicant can supply or confirm. It is a new proposal, not a revision of the rejected proposal OB 607/1-1; Section 4.11 and the response matrix (separate file) explain what changed.

**Summary.** Learning-analytics systems usually record whether a student's answer was right. ThoughtScape, a working web platform used in six university courses, records the *sequence of reasoning steps* a student commits, keeps those steps in a tree, and compares that tree with instructor-defined solution trees. From the comparison it computes trajectory metrics (progress, step distance, alignment distance, per-step deviation, flags such as "off path" or "productive struggle"). These metrics are the platform's central scientific claim: that they show *where understanding diverges*, not only whether it is correct. **Nobody has yet tested that claim.** A first stress test of the shipped code (Section 1.3) shows why this matters: its text-similarity step cannot tell a meaning-preserving rewording from a meaning-breaking one-word error. The project therefore does not build another adaptive system. It asks three questions: **(RQ1)** do trajectory metrics measure defined reasoning constructs, and do they add information beyond answer correctness and standard knowledge-tracing baselines? **(RQ2)** which similarity and alignment method is valid, robust to equivalent solution paths, and fair across language and gender groups? **(RQ3)** can instructors turn the evidence into better teaching decisions? Work is grounded in evidence-centered assessment design and in learning-science accounts of constructive engagement, error and productive failure. It is carried out with named courses at two institutions, a preregistered design and a formal data management plan. A doctoral researcher's thesis is built from the work packages.

# 1 Starting point

## 1.1 State of the art and research gap

**Outcome-centred analytics.** Educational data mining and learning analytics have been dominated for two decades by prediction of outcomes. Knowledge tracing (KT) is the best-developed line: from Bayesian KT [Corbett & Anderson 1995] to deep sequence models [Piech et al. 2015], surveyed by Abdelrahman et al. [2023]. KT estimates the probability that a student will answer the next item correctly. It does not represent *how* a student reasoned, so it cannot tell an instructor whether a wrong answer came from a mis-chosen strategy, an arithmetic slip or an abandoned correct idea. Gašević et al. [2015] argued that analytics must be integrated with educational research and theory; much of the field has not followed. This project does not propose a new KT model. KT is used only as a baseline.

**Process measures in computing education.** Process data are not new in programming education. The Error Quotient [Jadud 2006] quantifies repeated compile errors and is a well-known predictor of difficulty. Such measures are bound to one event type (syntax errors), do not represent the *structure* of the student's plan, and are not defined for SQL, mathematical derivation or free-text reasoning.

**Intelligent tutoring systems (ITS) and their adoption.** Step-based ITS reach effect sizes close to human tutoring, d = 0.76 vs. 0.79 in VanLehn's [2011] review. The meta-analysis of Kulik and Fletcher [2016] also reports positive effects on average. They are expensive to author and have not become routine in university teaching. Work on teacher-facing tools shows that usefulness depends on co-design with teachers and on supporting *human* decisions, not on better prediction [Holstein, McLaren & Aleven 2019]. Example-tracing tutors [Aleven et al. 2009] lowered authoring cost by recording demonstrated solution graphs. ThoughtScape is closest to that idea, with three differences: the learner's own structure persists and is *revised* (repair, revision, abandonment edges), there is deliberately no tutoring feedback, so that the instrument can be validated before it is used to intervene, and the target tasks are open-ended code, SQL and derivations.

**Concept-map assessment.** Eliciting a student's knowledge structure and scoring it against a criterion map is an established assessment method. Ruiz-Primo and Shavelson [1996] concluded that its validity depends on task, response format and scoring, and that an integrative cognitive theory is needed to limit variation. ThoughtScape's gold tree is a *dynamic* criterion map. The lessons apply directly: scoring choices must be justified by theory and tested, not assumed.

**Generative AI.** Chat-based assistants are now common. A field experiment with nearly 1,000 secondary students found that unguarded access raised practice performance but lowered later unaided performance, while a guardrailed tutor largely avoided the harm [Bastani et al. 2025]. This motivates instruments that *elicit* reasoning rather than supply answers, but only if the instrument measures reasoning validly.

**Fairness.** Algorithmic bias in educational models is well documented across gender, race and language [Baker & Hawn 2022], and slicing analysis is the recommended basic audit [Gardner et al. 2019]. Fairness of *process* metrics derived from free text is almost unexamined. Text-similarity measures plausibly disadvantage second-language writers.

**Research gap.** Three gaps follow. **G1:** no evidence exists on the *construct validity* of reasoning-trajectory metrics derived from a student-built tree (what they measure, whether they exceed correctness and KT). **G2:** it is unknown which similarity and alignment method yields valid metrics when valid solutions are many and student wording varies. **G3:** it is unknown whether and how instructors can use such evidence, and for whom it is unfair. These gaps are the scientific core. Platform engineering is not a project goal.

## 1.2 Theoretical framework and definitions

The project uses **evidence-centered design** [Mislevy et al. 2003] as its measurement framework. A *student model* names the claims we want to make about reasoning, a *task model* defines the lab (scenes, gold set) that elicits it, and an *evidence model* states which observable trajectory features bear on each claim. Validity is then an argument that can be tested piece by piece.

We do not treat "knowledge" as one latent number. **We claim nothing about internal mental states. We operationalise *externalised reasoning steps* along five constructs**, each tied to a learning theory (Table 1). "Personalised learning" is not a target; the product of the project is evidence for *instructor-mediated formative feedback*.

**Table 1. Constructs, theory, trajectory evidence and validity threats**

| Construct | Theoretical basis | Trajectory evidence (observable) | Main threat to validity |
|---|---|---|---|
| C1 Constructive engagement | ICAP: constructing outputs beyond the given material produces deeper learning than active or passive engagement [Chi & Wylie 2014]; self-explanation [Chi et al. 1994] | Number and elaboration depth of committed steps (not only runs) | Many steps ≠ good steps; students may pad |
| C2 Conceptual vs. procedural knowledge | Procedural skill and conceptual understanding develop iteratively and are separable [Rittle-Johnson et al. 2001; Anderson & Krathwohl 2001] | Node kind (goal/subgoal = strategy, operator = procedure, evidence) and their balance | Node kinds are assigned by rules; must be checked against expert coding |
| C3 Error handling and repair | Learning from performance errors [Ohlsson 1996]; productive failure [Kapur 2008; 2016] | Error nodes, `repairs` edges, time-to-repair, dead-end ratio | Struggle can be unproductive; productive failure effects depend on task complexity and later consolidation [Sinha & Kapur 2021] |
| C4 Misconception persistence | Misconceptions as systematic, recurrent wrong models | The same gold step diverges, is revised and diverges again across attempts or labs | Needs a misconception inventory per course (WP1) |
| C5 Rationale coverage | Self-explanation quality [Chi et al. 1994] | Coverage of gold rationale in free-text steps | Language proficiency confounds text coverage (fairness, WP2) |

**Why the rewrite of Figure 1.** The earlier proposal presented a catalogue of ML techniques. Here every analytic element exists only because a construct needs evidence. The unit of analysis is a *reasoning step*, defined in the platform as one committed interaction whose normalised text is attached to the student's tree.

## 1.3 Preliminary work

**(a) A working instrument.** ThoughtScape (code: github.com/victordeman/thought-scape; deployed at thought-scape-three.vercel.app) is a Next.js application with a Postgres backend. We inspected the code at commit 793795a (8 Nov 2026). It offers six courses (Distributed Systems, Robotics Perception, Mathematics of Cryptography, Introduction to AI, Database Management Systems, Introduction to Machine Learning) with **61 labs and 375 gold-tree nodes** (mean 10 words per node). A three-pane workspace separates **Run** (explore) from **Commit thought** (add to tree). The engine keeps a binary consensus tree per learner and task with typed edges (`elaborates`, `depends-on`, `revises`, `contradicts`, `repairs`, `abandons`). Rules repair errors, prune contradicted siblings and mark outlier steps as dead ends. A dynamic-programming alignment of the student path to the gold path with a drop cost yields `d_align`, `mean_d_step`, `d_trajectory` (0.7 · alignment + 0.3 · mean step), progress, per-step deviation δπ and flags. Semester freezing, shared classroom trees, QR-badge sign-in with server-side session revocation, an activity-analytics dashboard and a researcher role exist. In our environment the three engine test files (20 tests) pass; the full test suite needs a native SQLite build that was not available, so we did not run it. A separate reference repository for the thought-model engine ("Thought-model-generator") is linked from the README.

**(b) What the instrument does *not* yet have.** (i) No validity evidence exists. The instrument has not been evaluated against expert judgement or learning outcomes. [Confirm: no classroom data collected so far.] (ii) Text similarity is computed with a **64-dimension signed hash of word unigrams and bigrams** (`embeddingUtils.ts`), not a semantic model. Thresholds (0.3, 0.6, 0.7), the drop cost 0.5 and the 0.7/0.3 weighting are hand-set. (iii) Labs are authored in TypeScript source files, which instructors cannot edit. (iv) Name-based student sign-in with no credential is on by default, and activity records are deleted after 90 days by default. Both settings must change for research use (Section 2.4).

**(c) A stress test of the shipped similarity step (new, this proposal).** We built a *probe set* of 22 gold steps (stratified over the six courses, selected with a fixed random seed). For each we wrote (L) a light rewording, (H) a heavy rewording with the same meaning, and (N) a minimal edit that makes the step wrong (e.g., "UDP" for "TCP", `S` for `S⁻¹`, "after softmax" for "before softmax"). We ran the engine's own distance function (1 – cosine) on each pair. Probes were written by the AI assistant that prepared this draft and are **not yet validated by any domain expert**; n is small; the set is adversarial *by design* to lexical similarity. It tests the metric, not students.

| Result (n = 22) | Light reword | Heavy reword (same meaning) | Minimal error (wrong) |
|---|---|---|---|
| Mean distance to gold step | 0.086 | **0.643** | 0.087 |
| Closer to gold than the minimal error | 11 of 22 (2 ties) | **0 of 22** | – |
| Distance above 0.6 ("off path" flag level) | 0 | **13 of 22** | 0 |
| Distance above 0.7 (sibling-pruning level) | 0 | **9 of 22** | 0 |
| Gold step ranked first among the lab's steps | 22 | **6 (chance ≈ 3.6)** | 22 |

The metric therefore cannot separate a rewording that keeps the meaning from a one-word error (0.086 vs. 0.087), and it treats a faithful heavy rewording as far from the gold step, even beyond the level at which the engine marks a step off-path. Real student text may behave differently. The probe set, code and raw results are published with this proposal so that the test can be repeated and criticised. The result defines the problem the project addresses: **trajectory metrics are currently unvalidated and probably sensitive to wording**.

**(d) Applicant's prior work.** [Insert 3–5 own publications on instructional feedback, SQL learning environments, recommender and knowledge-graph systems, each with DOI and one line on relevance to WP1–WP3. Reviewer 2 of OB 607/1-1 judged these a direct technical foundation; do not re-argue them, point to them.]

## 1.4 What the project deliberately does not do

To meet the objections of the previous review (focus on well-covered ground; excess scope), the project contains **no** new KT model, no reinforcement-learning component, no knowledge-graph construction, no adaptive tutoring, no chatbot, and no development of a new learning environment. Existing features are used as they are, and changes are limited to instrumentation, metric computation and data export.

# 2 Objectives and work programme

## 2.1 Anticipated total duration

36 months. Data collection windows are fixed to the academic terms of the partner institutions (Section 2.3, risks).

## 2.2 Objectives, research questions and hypotheses

**Objective.** Establish, with evidence, whether and how reasoning-trajectory metrics from consensus trees can be used to understand and support student reasoning in university technical courses.

**RQ1 Construct validity.** To what extent do trajectory features relate to expert-coded reasoning constructs C1–C5, and do they add information beyond final-answer correctness, attempts, time on task and a standard KT baseline (performance factors analysis)?
*H1a (convergent):* correlation between trajectory features and expert codes of at least r = .25 (the smallest value of interest). *H1b (incremental):* adding the trajectory block to the baseline raises explained variance in a delayed concept check by at least f² = 0.05, with cross-validated AUC gain ≥ 0.03 for identifying students who fail it. Thresholds are fixed in the preregistration. *Null result:* if H1b fails for all metric families, this is reported as evidence against process-metric claims, which would be a useful result for the field.

**RQ2 Method validity, robustness and fairness.** Among four similarity/alignment families (M0 current hashed lexical; M1 pretrained sentence and code encoders; M2 tree-edit distance with M1 node labels; M3 alignment against a *set* of valid gold paths), which satisfies (a) invariance to meaning-preserving rewording, (b) sensitivity to minimal meaning-changing errors, (c) agreement with experts, (d) parity of flag rates and error rates across language-background and gender groups after conditioning on expert-coded reasoning quality?
*H2:* M1–M3 outperform M0 on (a) and (b) (AUC difference with 95% CI excluding 0 on the expert-validated probe set); disparities in flag rate exceed a preregistered tolerance for M0 and not for the selected method. Failure is reported.

**RQ3 Instructor use.** Does showing instructors the tree and trajectory evidence change the quality, speed and confidence of their diagnoses of student difficulty, what actions do they take, and how do these relate to students' resolution of the diagnosed difficulty? RQ3 is *estimation-focused*: effect sizes with intervals, not claims of proof.

## 2.3 Work programme including research methods

**Table 2. Work packages (36 months)**

| WP | Title | Months | Key outputs |
|---|---|---|---|
| WP1 | Construct specification, codebook and annotated corpus | 1–14 | Codebook; expert-annotated corpus; gold *sets*; preregistration |
| WP2 | Metric validation and fairness audit | 9–28 | Probe benchmark; validated metric suite; fairness report; open library |
| WP3 | Instructor evidence use (co-design, decision study, field study) | 10–33 | Dashboard views; decision study; classroom field study |
| WP4 | Synthesis, data release, thesis | 29–36 | Thesis; data release; practice guide |

**Partner courses and sites [confirm each; letters of support attached to the elan submission].** Two courses with different knowledge profiles are used: *Database Management Systems* (14 existing labs; SQL, declarative and procedural knowledge) and *Introduction to Machine Learning* (15 existing labs; mathematical and conceptual reasoning). Site A: [OVGU Faculty of Computer Science, course and instructor]. Site B: [Miva Open University, School of Computing, course and instructor]. At least two instructors per site co-design and use the system. Because labs are authored in code, up to 6 labs per course are authored or adapted *by the project team with the instructors*; an instructor-facing authoring tool is out of scope and named as a limit.

**WP1: Constructs, codebook, corpus (M1–14).**
*T1.1* Evidence-centred domain analysis with the instructors (two workshops per course): target constructs, misconception inventory drawn from the literature and instructors' own exam-error records.
*T1.2* Codebook for node-level codes (C1–C5 × quality level) and trajectory-level codes (e.g., productive struggle, unresolved misconception, recovery from dead end). Two coders code 40 trajectories, refine the book, then double-code at least 20% of the corpus. Codes with Krippendorff's α below 0.667 are reported but excluded from confirmatory tests; target α ≥ 0.70.
*T1.3* Gold *sets*: for each of up to 12 labs, up to three valid solution paths and the known misconception paths, authored by instructors.
*T1.4* Think-aloud sub-study (24 students, 12 per course) with concurrent protocols [Ericsson & Simon 1993] to check that committed steps correspond to what students report thinking, the central assumption of the instrument.
*T1.5* Preregistration (hypotheses, metrics, thresholds, exclusions, analysis code) before confirmatory data are inspected (M10).
*Corpus size.* Target **N = 300 consenting students**. The confirmatory incremental test (k = 3 added predictors, f² = 0.05, α = .05, power .80, up to four baseline covariates) needs n = 223, which leaves a 25% margin for non-consent, missing data and exclusion. The fallback is N ≥ 124, which is sufficient for H1a (r = .25, power .80).
*Deliverables:* D1.1 codebook (M8), D1.2 preregistration (M10), D1.3 annotated corpus and gold sets (M14).

**WP2: Metric validation and fairness (M9–28).**
*T2.1 Probe benchmark.* Extend the stress test of Section 1.3 into a benchmark of at least 500 expert-validated probe pairs across courses: meaning-preserving transformations (paraphrase, identifier renaming, clause reordering, formatting) and minimal meaning-changing edits (operator flip, off-by-one, negation, wrong quantifier). Two instructors validate each pair; unclear pairs are dropped. Every metric family is scored on invariance and sensitivity with intervals.
*T2.2 Metric families.* M0 (baseline: current engine). M1: pretrained sentence encoders [Reimers & Gurevych 2019] and code-aware encoders, run **on infrastructure in the EU; no student text is sent to third-party APIs**. M2: tree-edit distance [Zhang & Shasha 1989] over the learner tree and gold tree with M1 labels. M3: sequence alignment against the gold *set*, taking the best path, with explicit semantics for dropped steps (building on dynamic time warping [Sakoe & Chiba 1978]). All hand-set constants (0.3, 0.6, 0.7, 0.5, 0.7/0.3) become parameters estimated by cross-validation on part of the corpus and frozen before the confirmatory test.
*T2.3 Validity analysis.* Convergent validity against expert codes (weighted κ, Spearman). Incremental validity: nested models, cross-validated, with a baseline containing final correctness, attempts, time on task and a performance-factors KT model. Criterion: a delayed (2–3 weeks) concept check aligned with the lab constructs, plus aligned exam subscores.
*T2.4 Fairness audit.* Slicing analysis [Gardner et al. 2019] by language-of-instruction background, gender (voluntary self-report), prior-grade tier and site. Parity of flag rates, AUC and calibration, *conditional on expert-coded reasoning quality*. If a disparity exceeds the preregistered tolerance, we test the mitigation options (different metric family, group-agnostic thresholds, text normalisation) and report what remains.
*T2.5 Open release.* Measurement library (TypeScript, with a reference Python implementation), probe benchmark and, where consent allows, the pseudonymised corpus.
*Deliverables:* D2.1 benchmark (M18), D2.2 metric validation report (M24), D2.3 fairness report and library (M28).

**WP3: Instructor evidence use (M10–33).**
*T3.1 Participatory co-design.* Three cycles with 6–8 instructors and teaching assistants across both sites, following the co-design approach of Holstein et al. [2019]: needs-finding, storyboards, prototype views (tree, flags, misconception list). Outcome: the dashboard views and the *decisions* they are meant to support (who to contact, which misconception to address in class).
*T3.2 Decision experiment.* Within-subject, N ≥ 16 instructors/assistants, 8 vignettes each, drawn from consented real trajectories. Conditions: (A) scores and submissions only; (B) plus tree and trajectory view; order counterbalanced. Outcomes: agreement of the diagnosis with the expert coding, time, confidence, System Usability Scale, think-aloud notes. Analysis: mixed models (random effects for instructor and vignette); effect sizes with intervals.
*T3.3 Classroom field study.* At least four course sections over two terms. Within each section the view is switched on for alternating labs (counterbalanced across sections), so each instructor serves as their own control. Outcomes: logged instructor actions; time to resolution of a flagged misconception on the next lab (from tree `repairs`); concept check; students' perceived usefulness. **The study is estimation-focused and not powered for small effects**, because cluster dependence (intra-class correlation .05–.10 with about 40 students per section gives a design effect of 3 to 5) cannot be offset at this sample size. Hypothesis tests are therefore secondary.
*T3.4 Student transparency.* Students see their own tree and what is recorded; no ranking or public comparison is shown; flags are never used for grading.
*Deliverables:* D3.1 co-designed views (M18), D3.2 decision study (M26), D3.3 field study (M33).

**WP4: Synthesis (M29–36).** Thesis; data release; a *practice guide* for responsible use of process metrics in teaching; final report.

**Time plan (months).**

| | 1–6 | 7–12 | 13–18 | 19–24 | 25–30 | 31–36 |
|---|---|---|---|---|---|---|
| WP1 | ████ | ████ | ██ | | | |
| WP2 | | ██ | ████ | ████ | ████ | |
| WP3 | | ██ | ████ | ████ | ████ | ██ |
| WP4 | | | | | ██ | ████ |

**Staffing and realism of the plan.** The previous proposal asked one doctoral researcher to build and evaluate five work packages. This proposal has four packages, no platform development, one doctoral researcher, one student assistant and the applicant's own position. Effort (person-months): applicant 36 (WP1 10, WP2 10, WP3 12, WP4 4); doctoral researcher 36 (WP1 9, WP2 12, WP3 11, WP4 4, of which about 20% of working time is reserved for qualification activities); student assistant 36 months at about 9 hours/week (annotation support, study operations, data preparation). **Thesis plan.** Chapter 1 codebook and corpus (WP1); chapter 2 metric validation (WP2); chapter 3 fairness (WP2); chapter 4 instructor decision study (WP3); chapter 5 synthesis. Four first-author papers are planned: P1 corpus and codebook (M14), P2 metric validation (M24), P3 fairness (M28), P4 instructor decision study (M32). Venue families: educational data mining, learning analytics, AI in education and learning-at-scale journals and conferences.

**Risks and contingency.**

| Risk | Likelihood / impact | Response |
|---|---|---|
| A partner course withdraws or enrolment is low | Medium / high | Two courses at two sites; fallback N ≥ 124 still powers H1a; use of consented data from additional sections |
| Low consent rate | Medium / medium | Consent handled by someone other than the instructor; no grade effect; small voucher; sample margin of 25% |
| Annotation does not reach α ≥ 0.667 for some codes | Medium / medium | Codebook iteration; report such codes as exploratory only |
| No metric family adds incremental validity | Medium / low (still a result) | Publish as evidence on the limits of process metrics; practice guide reflects this |
| Instructors do not use the views | Medium / medium | Co-design with the same instructors; decision study isolates view quality from adoption |
| Platform defects or hosting limits during studies | Low / medium | Instrumentation only; EU-region managed database; pre-term load test |
| Data loss under the platform's 90-day deletion default | High if not handled / high | Research export before the deletion sweep; retention configured for study terms (Section 2.4) |

## 2.4 Handling of research data

*Following the DFG research-data checklist.*

**Characteristics and scope.** (i) Interaction logs: committed text (code, SQL, notes), run/commit events, timestamps, session identifiers. (ii) Learner trees and computed metrics. (iii) Expert annotations. (iv) Think-aloud audio, transcripts. (v) Concept-check and exam subscores. (vi) Questionnaires (SUS, perceived usefulness, self-reported background). (vii) Instructor study data. Expected volume: below 10 GB excluding audio; audio about 20 hours.

**Documentation and quality.** Codebook, data dictionary, preregistration and analysis code are versioned. Software version (commit hash) is stored with each export so that metrics can be recomputed.

**Storage and technical archiving.** Production data stay in a managed Postgres database in an EU region [confirm the current region of the deployed database; migrate if needed]. For the studies, student sign-in uses **QR badges** and name-based sign-in is switched off (`THOUGHTSCAPE_NAME_LOGIN=off`), because the default allows anyone to sign in as any student and would corrupt the data. The platform's default 90-day deletion of activity records is changed for study terms, and a pseudonymised research export is taken *before* any deletion sweep. Login tokens are stored only as hashes. Audio is transcribed within 14 days and deleted. A re-identification key (badge to pseudonym) is held separately at the host institution and destroyed at project end unless participants consent to longer storage.

**Legal obligations and conditions.** GDPR for German processing; the Nigeria Data Protection Act 2023 for processing at Miva Open University; cross-border transfer and joint-controller arrangements are to be reviewed by the data-protection officers of both institutions before data collection [to confirm]. Informed consent covers research use, pseudonymised sharing and the option to withdraw. Free-text submissions may contain personal data; a scrubbing step and manual check precede any release.

**Reuse and long-term access.** Code under an open-source licence [none is currently stated in the repository; choose one]. Probe benchmark and metric library fully public. Pseudonymised corpus offered, where consent permits, via a research data centre for education [e.g., FDZ Bildung at DIPF, to be confirmed] with controlled access; otherwise a metadata record only. Retention of at least 10 years in line with good research practice.

**Responsibilities and resources.** The applicant is responsible for the data management plan; the doctoral researcher for exports and documentation; the host institution's research-data service advises. Costs are in Section 5 (hosting, annotation, repository).

## 2.5 Relevance of sex, gender and/or diversity

The topic is directly concerned with diversity. The fairness audit (T2.4) examines whether flags and metrics differ across language background and gender at equal reasoning quality. Self-report is voluntary and aggregated; **no protected attribute is inferred from text**. Co-design includes instructors of different gender and teaching context. Findings on group differences are reported with the precision allowed by the group sizes, with small cells suppressed.

# 3 Project-related list of publications

[Insert up to 10 items, each with DOI. Suggested structure: (a) 3–5 own peer-reviewed publications relevant to feedback systems, SQL learning, knowledge graphs; (b) the software record for ThoughtScape; (c) optionally the probe set deposit (Zenodo DOI after upload).]

# 4 Supplementary information on the research context

**4.1 Ethical and legal aspects.** Participants are adult students. Risks: privacy of free-text and audio data; pressure to consent where the researcher teaches the course; unfair treatment from flags. Measures: ethics approval at each site *before* data collection [OVGU ethics committee; Miva Open University research ethics board, to be named and dated]; consent collected and held by a person who does not grade the course; participation and opt-out without effect on grades; instructors see flagged data only for consenting students in research mode; flags are advisory and never enter grades; data minimisation; transcription and deletion of audio. No animal experiments. No special-category data are requested.

**4.2 Employment status.** [Applicant: current position and contract end at Miva Open University; confirm that the route for an applicant working outside Germany is the *Research Grants* programme with the module *Temporary Position for Principal Investigator*, which requires a statement of a German host institution that it assumes employer responsibilities. DFG states that applicants must be employed at a research institution in Germany or at a German research institution abroad, so confirm eligibility with the DFG Head Office before submitting.]

**4.3 First-time proposal data.** [Complete in elan.]

**4.4 Composition of the project group.** Applicant (own position); doctoral researcher (to be recruited); student assistant. [Mentoring applicant and host: Prof. Dr. A. Nürnberger, OVGU, to be confirmed.]

**4.5 Researchers in Germany with whom cooperation is agreed.** [Host: OVGU; partner instructors named in Section 2.3; attach letters.]

**4.6 Researchers abroad with whom cooperation is agreed.** [Miva Open University instructors and ethics contact; attach letters.]

**4.7 Collaborations in the last three years.** [To complete.]

**4.8–4.9 Commercial enterprises.** None. The platform runs on commercial cloud hosting under standard terms; no cooperation or participation exists.

**4.10 Scientific equipment.** The project uses the host's existing computing and the platform's managed hosting. No equipment is requested; the three workstations requested earlier are dropped.

**4.11 Other submissions.** Earlier application OB 607/1-1 ("Lernendenzentriertes Modell zur Vorhersage und Darstellung von Wissen") was rejected. The present proposal has a different question (validity, fairness and use of trajectory metrics), a smaller scope (no model building), named partner courses and a formal data management plan. [Confirm DFG rules on resubmission after rejection with the Head Office.] No other submissions on this topic.

**4.12 Other information – use of generative AI.** In line with DFG requirements, we disclose that the text of this draft was prepared with the assistance of a generative AI model (Claude, Anthropic). The model read the code repository, ran the stress test in Section 1.3 and searched the literature. The applicant is responsible for all content and must verify each claim, citation and number before submission.

# 5 Requested modules and funds

*All amounts are indicative and must be recalculated with the DFG personnel rates for the start year (DFG form 60.12) and the host institution's rates before submission.*

**5.1 Basic Module**

**5.1.1 Staff.**

| Item | Basis | Amount (€) |
|---|---|---|
| Doctoral researcher, 100%, 36 months | indicative €81,600/year ("Doktorandin/Doktorand und Vergleichbare", 2026 level as reprinted in a university guide; verify against form 60.12) | 244,800 |
| Student assistant, 36 months × 40 h/month | €18.20/h indicative host rate | 26,208 |
| **Subtotal staff** | | **271,008** |

*Justification.* The doctoral researcher carries WP1–WP3 together with the applicant and writes the thesis (Section 2.3). The student assistant supports annotation, study operations and data preparation under the applicant's supervision. The previous proposal's two assistants are reduced to one. Note on the earlier draft: the earlier line "two assistants, 40 h/month each at €12.37/h, 36 months = €22,000" does not compute (that gives €35,626), so it should not be reused.

**5.1.2 Direct project costs.**

| Item | Basis | Amount (€) |
|---|---|---|
| Participant compensation | 300 students × €5 voucher; 24 think-aloud × €25; 16 instructors × €50 | 2,900 |
| Expert annotation | 2 external coders × 60 h × €30 | 3,600 |
| EU-region hosting and compute for encoders | €67/month × 36 | 2,412 |
| Travel – conferences | 6 trips × €1,700 | 10,200 |
| Travel – project meetings and fieldwork between the sites | 3 trips × €2,400 | 7,200 |
| Publication costs (open access) | €750/year × 3 | 2,250 |
| **Subtotal direct costs** | | **28,562** |

*Justification.* Costs follow work packages: compensation and annotation (WP1–WP3), hosting for studies and encoder inference without third-party APIs (WP2), conference travel for the four planned papers and site visits needed for classroom studies (WP3). Equipment is not requested. Repository deposit is free of charge.

**5.1.3 Instrumentation.** Not applicable.

**5.2 Module Temporary Position for Principal Investigator.** Requested for the applicant, 36 months, [100%], at the DFG rate for the applicable category [insert from form 60.12], employed by the host institution [OVGU, statement of the host to be attached]. *Justification:* the applicant is not employed by a German institution and leads WP1–WP4. Without the position the project cannot be carried out. [If the host employs the applicant already, this module is not needed; remove.]

**5.3–5.8** Replacement funding, clinician substitution, Mercator fellows, workshops, public relations: not applicable. **Equity and diversity standard allowance:** [check whether the flat rate applies to the host institution and request if eligible].

**Summary of requested funds (without Section 5.2 and the DFG programme flat rate, which DFG adds):**

| | € |
|---|---|
| Staff | 271,008 |
| Direct project costs | 28,562 |
| **Total** | **299,570** |

# References

Aleven, V., McLaren, B. M., Sewall, J., & Koedinger, K. R. (2009). A new paradigm for intelligent tutoring systems: Example-tracing tutors. *International Journal of Artificial Intelligence in Education, 19*(2), 105–154.
Abdelrahman, G., Wang, Q., & Nunes, B. P. (2023). Knowledge tracing: A survey. *ACM Computing Surveys, 55*(11), 224:1–37. https://doi.org/10.1145/3569576
Anderson, L. W., & Krathwohl, D. R. (Eds.) (2001). *A taxonomy for learning, teaching, and assessing.* Longman.
Baker, R. S., & Hawn, A. (2022). Algorithmic bias in education. *International Journal of Artificial Intelligence in Education, 32*(4), 1052–1092. https://doi.org/10.1007/s40593-021-00285-9
Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö., & Mariman, R. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. *PNAS, 122*(26), e2422633122. https://doi.org/10.1073/pnas.2422633122
Chi, M. T. H., de Leeuw, N., Chiu, M.-H., & LaVancher, C. (1994). Eliciting self-explanations improves understanding. *Cognitive Science, 18*(3), 439–477.
Chi, M. T. H., & Wylie, R. (2014). The ICAP framework: Linking cognitive engagement to active learning outcomes. *Educational Psychologist, 49*(4), 219–243. https://doi.org/10.1080/00461520.2014.965823
Corbett, A. T., & Anderson, J. R. (1995). Knowledge tracing: Modeling the acquisition of procedural knowledge. *User Modeling and User-Adapted Interaction, 4*(4), 253–278.
Ericsson, K. A., & Simon, H. A. (1993). *Protocol analysis: Verbal reports as data* (rev. ed.). MIT Press.
Gardner, J., Brooks, C., & Baker, R. (2019). Evaluating the fairness of predictive student models through slicing analysis. *Proc. LAK '19*, 225–234.
Gašević, D., Dawson, S., & Siemens, G. (2015). Let's not forget: Learning analytics are about learning. *TechTrends, 59*(1), 64–71. https://doi.org/10.1007/s11528-014-0822-x
Holstein, K., McLaren, B. M., & Aleven, V. (2019). Co-designing a real-time classroom orchestration tool to support teacher–AI complementarity. *Journal of Learning Analytics, 6*(2).
Jadud, M. C. (2006). Methods and tools for exploring novice compilation behaviour. *Proc. ICER '06*, 73–84.
Kapur, M. (2008). Productive failure. *Cognition and Instruction, 26*(3), 379–424.
Kapur, M. (2016). Examining productive failure, productive success, unproductive failure, and unproductive success in learning. *Educational Psychologist, 51*(2), 289–299.
Kulik, J. A., & Fletcher, J. D. (2016). Effectiveness of intelligent tutoring systems: A meta-analytic review. *Review of Educational Research, 86*(1), 42–78.
Mislevy, R. J., Almond, R. G., & Lukas, J. F. (2003). *A brief introduction to evidence-centered design* (ETS Research Report RR-03-16). https://doi.org/10.1002/j.2333-8504.2003.tb01908.x
Ohlsson, S. (1996). Learning from performance errors. *Psychological Review, 103*(2), 241–262.
Piech, C., Bassen, J., Huang, J., Ganguli, S., Sahami, M., Guibas, L., & Sohl-Dickstein, J. (2015). Deep knowledge tracing. *Advances in Neural Information Processing Systems 28.*
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proc. EMNLP-IJCNLP 2019*, 3982–3992. https://doi.org/10.18653/v1/D19-1410
Rittle-Johnson, B., Siegler, R. S., & Alibali, M. W. (2001). Developing conceptual understanding and procedural skill in mathematics: An iterative process. *Journal of Educational Psychology, 93*(2), 346–362.
Ruiz-Primo, M. A., & Shavelson, R. J. (1996). Problems and issues in the use of concept maps in science assessment. *Journal of Research in Science Teaching, 33*(6), 569–600.
Sakoe, H., & Chiba, S. (1978). Dynamic programming algorithm optimization for spoken word recognition. *IEEE Trans. Acoustics, Speech, and Signal Processing, 26*(1), 43–49.
Sinha, T., & Kapur, M. (2021). When problem solving followed by instruction works: Evidence for productive failure. *Review of Educational Research, 91*(5), 761–798.
VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist, 46*(4), 197–221. https://doi.org/10.1080/00461520.2011.611369
Zhang, K., & Shasha, D. (1989). Simple fast algorithms for the editing distance between trees and related problems. *SIAM Journal on Computing, 18*(6), 1245–1262.
