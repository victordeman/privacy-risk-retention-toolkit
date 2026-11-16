---
title: "ThoughtScape: Eliciting Student Reasoning as Consensus Trees, and a Stress Test of the Trajectory Metrics Computed from Them"
author: "Chukwuka Victor Obionwu [co-authors and affiliations to be added]"
date: "Draft v1, 16 November 2026"
---

**Status of this draft.** System description and measurement-validity paper. It reports *no* data from students. Its empirical content is a stress test of the shipped metric code on a small probe set written by the author (Section 5). Square brackets mark information only the authors can supply. Suitable venues after revision: learning-at-scale, learning-analytics or computing-education conferences, or a learning-analytics journal. Whether the paper is worth submitting before a classroom study exists is the authors' decision (see Section 7).

# Abstract

Learning platforms usually record what a student submitted. ThoughtScape records the steps a student *commits* while working through a lab, keeps them as a binary consensus tree with typed relations (elaboration, dependency, revision, contradiction, repair, abandonment), and compares the tree with an instructor-defined gold tree. From the comparison it computes trajectory metrics: progress, step distance, alignment distance, per-step deviation and flags such as "off path". The platform runs six university courses (61 labs, 375 gold-tree steps) and deliberately has no conversational assistant. The central design claim is that these metrics show *where* a student's reasoning diverges from the intended reasoning, not only whether the final answer is right. We argue that this claim is a measurement-validity claim, give the evidence argument it would need in the framework of evidence-centred design, and test the weakest link of the shipped implementation: text similarity is computed with a 64-dimension signed hash of word unigrams and bigrams. On 22 gold steps with three variants each (a light rewording, a heavy rewording with the same meaning, a minimal error), the metric assigns practically the same distance to a light rewording and a one-word error (mean 0.086 vs. 0.087), places a faithful heavy rewording on average 7.4 times farther from the gold step than the one-word error (0.643), and would flag 13 of 22 faithful heavy rewordings as off-path. The probes were written by a generative AI model, have not been validated by any domain expert and are adversarial to lexical similarity by design; the result is therefore a reason to validate, not an estimate of performance on students. We release the code and data of the test and set out a validation programme.

**Keywords:** formative assessment, process data, reasoning trajectories, construct validity, learning analytics, computing education

# 1 Introduction

Most course platforms see the *product* of student work: a final answer, a grade, a quiz score. Instructors, however, diagnose understanding from the *process*: which approach the student took, which step went wrong, whether the student noticed and repaired the mistake. Process data are available in principle, because platforms log interactions, but turning logs into statements about reasoning is difficult. A log of keystrokes is not a model of thought.

ThoughtScape takes a deliberately narrow route. Instead of inferring reasoning from raw logs, it asks students to *externalise* reasoning in small committed steps, separates exploring (running code) from committing (adding a step to one's tree), and gives the instructor a tree and a few trajectory metrics. It contains no chatbot. The reasoning is that conversational assistants can supply answers on the student's behalf, which can harm later unaided performance when not designed with guardrails [Bastani et al. 2025], whereas an elicitation instrument leaves the thinking with the student.

The platform exists and is deployed, and that is exactly why a measurement question is now urgent: dashboards that show a number invite interpretation. This paper makes three contributions.

1. **Design.** A description of the instrument: the consensus-tree model, the commit/run separation, the metrics, and the course, classroom and semester machinery around them, based on code inspection at a fixed commit (Section 3).
2. **Validity argument.** A statement of what the metrics claim to measure, mapped to learning theory and to observable trajectory features, and of the evidence needed to support each claim (Section 4).
3. **Stress test.** A reproducible test of the similarity step on which all metrics rest, with an unfavourable result that motivates validation before any classroom conclusions are drawn (Section 5).

# 2 Related work

**Outcome-centred analytics and knowledge tracing.** Knowledge tracing estimates the probability of correct future responses from response histories, from Bayesian models [Corbett & Anderson 1995] to deep sequence models [Piech et al. 2015]; Abdelrahman et al. [2023] survey the field. These models are about *outcomes per skill*, not about the structure of a student's reasoning. Gašević et al. [2015] argued that analytics should be tied to learning research. We use knowledge tracing only as a baseline in our validation plan.

**Process measures in programming education.** The Error Quotient measures how a novice handles repeated compile errors [Jadud 2006]. It shows that process features predict difficulty, but it is tied to one event type. ThoughtScape generalises to committed steps in code, SQL, derivations and notes, at the price of a harder validity question.

**Tutoring systems.** Step-based tutoring systems approach the effect of human tutoring (d = 0.76 vs. 0.79 in VanLehn's [2011] review) and meta-analytic evidence is positive on average [Kulik & Fletcher 2016]. Example-tracing tutors reduce authoring effort by recording demonstrated solution graphs [Aleven et al. 2009]. ThoughtScape borrows the idea of a reference solution graph but differs by keeping and *revising* the learner's own graph, by withholding tutoring feedback so that the instrument can be validated first, and by targeting open-ended tasks. Evidence on teacher-facing tools stresses co-design and support for teacher decisions [Holstein et al. 2019]; that is the stance of our planned instructor studies.

**Concept-map assessment.** Eliciting a knowledge structure and scoring it against a criterion map is established, and its validity depends on task, response format and scoring [Ruiz-Primo & Shavelson 1996]. A ThoughtScape gold tree is a dynamic criterion map, so the same cautions apply.

**Learning theory.** The commit step is a *constructive* activity in the sense of ICAP [Chi & Wylie 2014] and resembles self-explanation [Chi et al. 1994]. Repair and dead-end structure relate to learning from performance errors [Ohlsson 1996] and to productive failure [Kapur 2008; 2016], whose benefits depend on task design and consolidation [Sinha & Kapur 2021].

**Fairness.** Algorithmic bias in education is documented for gender, race and language [Baker & Hawn 2022]; slicing analysis is a standard audit [Gardner et al. 2019]. Text-similarity-based process metrics have, to our knowledge, not been audited.

# 3 The ThoughtScape instrument

All statements in this section are from inspection of the repository `victordeman/thought-scape` at commit `793795a` (8 November 2026). Names in code font are the repository's.

## 3.1 Tasks, scenes and gold trees

A *lab* (`Task`) has a brief, an ordered list of *scenes* (each with a goal and an elicitation mode: SQL editor, code cell, derivation, free text or choice), starter material and a **gold tree**: a small graph of instructor-written steps with kinds (`goal`, `subgoal`, `operator`, `evidence`) and typed edges. The six seeded courses contain 61 labs and 375 gold steps; steps are short natural-language descriptions (mean 10 words, e.g., "population covariance over sqrt(var_x * var_y); zero variance -> 0"). Labs are written in TypeScript source files, so authoring a lab requires a code change.

## 3.2 Run vs. commit, and the consensus tree

The workspace has three panes: scene text, an editor with separate **Run** and **Commit thought** actions, and a live tree view with a metric scoreboard. Running executes code to explore; committing turns the editor text into a normalised *derived thought* (`normalizeThought`) and adds it to the learner's tree. Each commit is classified by channel (query, submit, error, hint, choice, …) into a node kind (`operator`, `error`, `hypothesis`, `subgoal`, `evidence`).

The tree is a *binary* consensus tree: every node has at most two structural children (`elaborates`, `depends-on`); the invariant is asserted in development. A new node attaches to the confirmed or active, non-full node whose content is most similar to the new text, with ancestor and breadth-first fallbacks when nodes are full. Further rules: a later non-error commit marks open error nodes *dormant* and adds a `repairs` edge; a new subgoal or operator prunes a sibling when the text similarity of the two is below 0.3 (or when two different schema declarations are committed), adding a `revises` edge; steps that the alignment drops as outliers become `dead-end`. The *active path* is the set of candidate, active and confirmed nodes.

## 3.3 Metrics

Let $\varphi(t)\in\mathbb{R}^{64}$ be the signed feature-hashing vector of the lower-cased word and punctuation unigrams and adjacent bigrams of a text $t$, scaled to unit length (`embedUtils`), and $d(a,b)=1-\cos(\varphi(a),\varphi(b))$. After each commit the student trajectory $S=(s_1,\dots,s_n)$ is the content of the learner's confirmed and active nodes; the reference trajectory $R=(r_1,\dots,r_m)$ is the content of the confirmed gold nodes. The engine computes:

- *step distance* $d_i=d(s_i,s_{i+1})$ and its mean $\bar d$;
- an alignment of $S$ to $R$ by dynamic programming over match costs $d(s_i,r_j)$, with a *drop* operation of fixed cost 0.5 for student steps that match nothing; $D_{\text{align}}$ is the optimal cost divided by $\max(n,m)$;
- $D(S,R)=0.7\,D_{\text{align}}+0.3\,\bar d$;
- progress $p_j$, the share of the reference covered up to the last matched step, and the expected next reference step;
- per-step deviation $\delta\pi_i$ (the distance to the matched reference step, or 1 for a dropped step);
- flags: `off_path` if some $\delta\pi_i>0.6$; `large_jump` if some $d_i>0.7$; `dropped_outlier` for dropped steps.

The weights (0.7/0.3), the drop cost (0.5) and the thresholds (0.3, 0.6, 0.7) are constants set by hand; we found no estimation or calibration step in the engine code.

## 3.4 Courses, classrooms, semesters, roles and access

Six courses are served, each with a hub (a labs grid, plus syllabus, projects, resources and assessment tabs where the course defines them). A *semester* provisions a course's labs as frozen task specifications for a cohort (lifecycle draft, active, archived). A *classroom* is a join-code room whose shared tree lives under a classroom principal. Roles are student, instructor, researcher and admin; researchers see cross-cohort activity analytics. Sign-in is by QR badge (opaque token, stored as SHA-256 hash, HMAC-signed session cookie, server-side session rows that can be revoked). Name-based student sign-in without any credential exists and is **on by default**; it is documented as a choice for trusted classrooms. Activity records and guest identities are deleted after 90 days by default. The production deployment is on a commercial serverless platform with a managed Postgres database. Both the default sign-in mode and the deletion default matter for research use (Section 6).

## 3.5 Testing

The engine's unit tests (three files, 20 tests) pass in our environment. The full suite (17 files) requires a native SQLite build that was not available there, and we did not run it.

# 4 What the metrics claim: a validity argument

A metric becomes evidence only inside an argument. We use evidence-centred design [Mislevy et al. 2003]: a *student model* (the claims), a *task model* (what the lab elicits) and an *evidence model* (which observable features bear on which claim). The unit of evidence is a committed step. We make **no claim about internal mental states**; the claims are about externalised reasoning along five constructs.

| Construct | Basis | Observable evidence | Main threat |
|---|---|---|---|
| C1 Constructive engagement | ICAP [Chi & Wylie 2014] | number and elaboration depth of committed steps | padding |
| C2 Conceptual vs. procedural knowledge | [Rittle-Johnson et al. 2001] | node kind balance | kinds assigned by rules |
| C3 Error handling and repair | [Ohlsson 1996; Kapur 2008] | error nodes, `repairs` edges, dead-end ratio | unproductive struggle |
| C4 Misconception persistence | systematic wrong models | the same gold step diverges again across attempts | needs an inventory |
| C5 Rationale coverage | self-explanation [Chi et al. 1994] | coverage of gold rationale in free text | language proficiency |

The argument has five links, and each can fail separately. (L1) Committed steps reflect reasoning (testable with think-aloud protocols). (L2) The similarity measure tracks *meaning* of steps. (L3) Alignment to a gold tree is a fair standard when several solutions are valid. (L4) The resulting features relate to expert judgements of the constructs and add information beyond correctness and standard knowledge-tracing baselines. (L5) The features are equally valid across learner groups, including second-language writers. This paper tests only L2, because every other link inherits its error.

# 5 Stress test of the similarity step

**Question.** Does the shipped distance $d$ separate meaning-preserving variation of a reference step from meaning-changing variation?

**Probe set.** From the 375 gold steps we selected, with a fixed random seed (7), up to four steps per course with 7–16 words and kind `operator` or `goal`, one per lab (22 steps: two from the two cryptography labs, four from each other course). For each step we wrote three variants: **L** a light rewording that keeps the meaning (a synonym or small restructuring), **H** a heavy rewording that keeps the meaning but changes most words, and **N** a minimal edit that makes the step wrong (e.g., "UDP" for "TCP"; `S` for `S⁻¹`; "after softmax" for "before softmax"; "inside" for "outside"). All probes are in `experiments/probes.json`.

**Measures.** For each variant, $d$ to its gold step (the engine's own function); whether L or H is closer to gold than N; the share above the engine's off-path level (0.6) and sibling-pruning level (0.7); and whether the gold step is ranked first among the lab's gold steps when each variant is compared with all of them (the situation the alignment faces). Intervals are 95% Wilson intervals; ties are differences of at most $10^{-9}$.

**Results (n = 22).**

| | L (light, same meaning) | H (heavy, same meaning) | N (minimal error) |
|---|---|---|---|
| Mean distance to gold step | 0.086 | 0.643 | 0.087 |
| Median distance | 0.074 | 0.623 | 0.064 |
| Closer to gold than N | 11 (2 ties; N closer in 9) | 0 of 22 | – |
| Distance > 0.6 (off-path level) | 0 of 22 | 13 of 22 [95% CI 0.39–0.77] | 0 of 22 |
| Distance > 0.7 (pruning level) | 0 of 22 | 9 of 22 [0.23–0.61] | 0 of 22 |
| Gold step ranked first in the lab | 22 of 22 | 6 of 22 [0.13–0.48]; chance ≈ 3.6 | 22 of 22 |

Mean rank of the gold step for H variants was 3.32 among on average 6.09 candidates.

**Reading.** (i) L and N are not separable: their mean distances differ by 0.001 and a sign test on the 20 non-tied items is far from significant (two-sided p = 0.82). (ii) H is farther from gold than N in all 22 cases, and in 13 of 22 cases is beyond the level at which the engine would mark a step off-path. (iii) Matching a heavy rewording to its own gold step succeeds in 6 of 22 cases against about 3.6 expected by chance. The metric therefore measures *surface overlap*, as its construction predicts: a one-token change barely moves a hashed n-gram vector, while rewording moves it a lot.

**Threats to validity.** (a) The probes were written by a generative AI model and have not been checked by any domain expert or instructor, so it is unverified that every N variant is really wrong and every L/H variant really equivalent. (b) n = 22 and one data point per item. (c) The set is adversarial by construction: it asks the metric to do what lexical similarity cannot. Students' committed text might be closer to gold wording than our H variants, in which case the gap would shrink, or might be code where the gold step is a prose description, in which case it would widen; the platform compares the *editor text* (`derivedThought`) with the gold description, and we have not tested that mismatch. (d) The test says nothing about the alignment procedure, the tree rules or their thresholds beyond the similarity step. (e) Sampling: 22 steps from 61 labs is a convenience-sized sample, selected with a fixed seed but not designed to represent the catalogue.

# 6 Validation programme

**Probe benchmark.** Extend to at least 500 expert-validated pairs across courses with meaning-preserving transformations (paraphrase, identifier renaming, clause reordering, formatting) and minimal errors (operator flip, off-by-one, negation); report invariance and sensitivity with intervals for each candidate metric.

**Candidate metrics.** M0 the current hashed lexical metric; M1 pretrained sentence and code encoders [Reimers & Gurevych 2019], computed locally; M2 tree-edit distance [Zhang & Shasha 1989] over learner and gold trees with M1 node labels; M3 alignment against a *set* of valid gold paths. Constants become parameters estimated by cross-validation and frozen before confirmatory tests.

**Validity and fairness studies.** Convergent validity against double-coded expert annotations (target Krippendorff's α ≥ 0.70); incremental validity over final correctness, attempts, time and a knowledge-tracing baseline, against a delayed concept check; slicing analysis by language background and gender, conditional on expert-coded reasoning quality [Gardner et al. 2019]; a think-aloud study of link L1 [Ericsson & Simon 1993]; and instructor studies (co-design, decision experiment, classroom field study) in the spirit of Holstein et al. [2019].

**Operational requirements for any study.** Switch off credential-free name sign-in and use QR badges; export pseudonymised data before the default 90-day deletion; host in the EU and run encoders on own infrastructure so that no student text reaches third-party APIs; obtain ethics approval and informed consent that is collected by a person who does not grade the course.

# 7 Discussion and limitations

The instrument's design choices (commit versus run, no chatbot, tree with repair semantics) are defensible on theoretical grounds, but a defensible design is not a validated measure. The stress test shows one concrete failure mode of the shipped metric. It does not show that the metrics are useless, that a better embedding would fix them (rewording invariance and error sensitivity may trade off, and equivalent solution paths are a separate problem), or that students' real text behaves like our probes.

Limitations of this paper: no student data; a small author-written probe set; no inspection of the production database or of deployment settings; authors' own system. The paper is best read as a measurement-validity agenda with a first, reproducible piece of evidence. Whether to submit now or after the benchmark and the first corpus exist is a decision for the authors; reviewers in learning analytics will likely ask for the latter.

# 8 Reproducibility

Code, probe set, selection script and raw results are in `experiments/`. With a ThoughtScape checkout at commit `793795a` and `npm ci --ignore-scripts`: `THOUGHTSCAPE_DIR=$PWD npx tsx <path>/list_nodes.ts > nodes.json`; `python3 select_nodes.py nodes.json > selected.json`; `THOUGHTSCAPE_DIR=$PWD npx tsx <path>/run_probe.ts` (run from the checkout); `python3 summarize.py results.json`. Re-running from the stored selection reproduced `results.json` exactly.

# Declarations

**Use of generative AI.** The text, probe variants and analysis scripts of this draft were produced with the assistance of a generative AI model (Claude, Anthropic), which also read the repository and searched the literature. The authors are responsible for the content and must verify all claims, references and numbers before submission.

**Ethics and data.** No human-subject data are reported. Future studies need ethics approval and consent as described in Section 6.

**Competing interests.** The first author developed and owns the platform. [Add funding and other declarations.]

# References

Aleven, V., McLaren, B. M., Sewall, J., & Koedinger, K. R. (2009). A new paradigm for intelligent tutoring systems: Example-tracing tutors. *International Journal of Artificial Intelligence in Education, 19*(2), 105–154.
Abdelrahman, G., Wang, Q., & Nunes, B. P. (2023). Knowledge tracing: A survey. *ACM Computing Surveys, 55*(11), 224:1–37. https://doi.org/10.1145/3569576
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
Sinha, T., & Kapur, M. (2021). When problem solving followed by instruction works: Evidence for productive failure. *Review of Educational Research, 91*(5), 761–798.
VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist, 46*(4), 197–221. https://doi.org/10.1080/00461520.2011.611369
Zhang, K., & Shasha, D. (1989). Simple fast algorithms for the editing distance between trees and related problems. *SIAM Journal on Computing, 18*(6), 1245–1262.
