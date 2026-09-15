# Designing Simulation Module to Diagnose Misconceptions in Learning Natural Selection

**Conference:** ISLS 2021

## Abstract & Introduction

### Abstract
This online experiment, involving 28 high school students, investigates frequencies and types of misconceptions while learning natural selection via two types of simulation modules. The experimental group uses an agent-based model which characterizes Pattern, Agents, Interactions, Relations, and Causality (PAIR-C) features while the control group employs a commonly used PhET simulation. Although the pre-posttest does not capture significant differences between the two conditions, a set of non-leading prompt questions embedded in both simulation modules successfully captured the differences. Students from the experimental condition revealed fewer frequencies and categories of misconceptions and scored significantly higher in explaining one type of common misconceptions as well as responding to objective prompts than the control condition. Our finding indicates that the PAIR-C simulation module might have a better effect in reducing misconceptions. This study manifests strong potential in using a well-structured online simulation module to diagnose and address students’ misconceptions in learning natural selection.

Designing Simulation Module to Diagnose Misconceptions in Learning Natural Selection Man Su, J.Yohan Cho, Michelene T. H. Chi, Nicole Boucher mansu@asu.edu, jycho2@asu.edu, michelene.chi@asu.edu, nsbouche@asu.edu, Arizona State University Brandon Vanbibber, University High School, brandon.vanbibber@tuhsd.org Abstract: This online experiment, involving 28 high school students, investigates frequencies and types  of misconceptions while learning natural selection  via two types o f simulation modules. The experimental group uses an  agent-based model which  characterizes Pattern, Agents, Interactions, Relations, and Causality (PAIR-C) features while the control group employs a commonly used PhET simulation.  Although the pre-posttest does not capture significant differences  between the two conditions, a set of non-leading prompt questions embedded in both simulation modules successfully captured the differences. Students from the experimental condition revealed fewer frequencies and categories of misconceptions and scored significantly higher in explaining one type of common misconceptions as well as responding to objective prompts than the control condition. Our finding indicates that the PAIR-C simulation module might hav e a better effect in reducing misconceptions.  T his study  manifests strong potential in using a well-structured online simulation module to diagnose and address students’ misconceptions in learning natural selection.

## Introduction

In our increasingly interconnected world, issues that emerge from local cir cumstances can give rise to complex global challenges (Wilensky & Jacobson, 2014). To prepare future generations to become contributing members of society as we move into the post-pandemic era, educators are at the forefront to create order out of the complexities. Helping students understand how a complex phenomenon is formed and why it is happening is critically important for formulating scientific predictions and reasonable decisions. Many natural and social phenomena can be conceptualized as emergent complex  systems. A complex system is a system composed of many elements that interact with each other and their  environment. Researchers use the term “emergent process” to describe how macro-level observable patterns emerge from micro-level interactions between numerous independent entities  and the resultant patterns are called "emergent phenomena" (Wilensky & Jacobson, 2014). Numerous researchers indicated challenges in introducing the concept of emergent complexity in traditional science curriculum (Yoon et al., 2018; Basu et al., 2015; Hmelo-Silver et al., 2015), and reported that high school students often have difficulty in learning the interactive components of complex systems, holding persistent  misconceptions in interpreting  emergent processes from a sequential mindset in science classrooms (Chi, 2013; Dickes et al., 2016).

Therefore, the advancement of teaching emergent complexity requir es more innovative instructional methods rather than the current traditional approaches. Our objective in this study was two-fold. The first objective is to  draw upon the PAIR-C framework  (Chi, under review) and agent-based modeling (ABM) literature to develop a simulation module that will constructively engage youth in observing and explaining complex systems. The second objective is to examine the effectiveness of using this simulation module to diagnose and address students’ misconceptions in learning the emergent process of natural selection. To this end, the simulation module designed in this study will be used to provide an alternative instructional approach and help tr ansform complex system teaching into flexible and efficient online modules.

## Theoretical perspectives

The PAIR-C framework Despite earlier research that proposed frameworks to characterize complex systems (Jacobson et al., 2011; HmeloSilver & Pfeffer, 2004), we employed the PAIR-C framework to create our simulation  module because of three unique reasons. First, PAIR-C provides an ontological framework representing two kinds of processes: sequential processes fea ture linear individualistic causality; emergent processes feature nonlinear collective causality. Second, PAIR-C acknowledges that Patterns, Agents, and Interactions are three dimensions  shared by both processes. Third, the Relations and Causality dimensio ns discriminate between the two kinds of processes from seven aspects. These aspects later become guiding principles for the simulation module design (see Table 1). Within the PAIR-C framework, Pattern describes the overall changes by a process that is often visible and meaningful, Agents (internal) are elements that participate in the process which produces the pattern (external agents interact with internal agents but do not participate in the pattern), the Interactions of the agents refer to how the agents of the process interact, the Relations among the interactions compare agents’ interactions, and the Causal relations between the agents-pattern refer to how the interactions between agents pro duce patterns in emergent processes. The causal relations are also referred to as causal mechanisms with two implications. Table 1: Seven aspects from the PAIR-C framework to discriminate between two kinds of processes Aspects Sequential Processes Emergent Processes Relations among the interactions

1. The set of interactions

available to all agents

2. With whom agents can

interact and when for individual interactions

3. Occur in serial order?

4. Conditional dependency:

Occurrence of interactions dependent on prior outcomes?

1. Distinct set

2. Restricted other

3. Serial ordering

4. Dependent

1. Same set

2. (Not restricted)

Random

3. Simultaneous

4. Independent

Causal relations between the Agents-pattern Causal Mechanism

5. How the pattern transforms:

Qualitative description

6. Agent-pattern causal

mechanism for the perceptual pattern: Quantitative computation Cumulative causal mechanism

5. Additive pattern

6. Cumulative summing of

subsequent interactions between units of time Collective causal mechanism

5. Converging pattern

6. Collective summing of

all the agents’ interactions within each unit of time

## Two implications

7. a. Identifiable causal agents

responsible for the pattern b. Alignment between the agents and the pattern

7. a. Single-agent or a group-Centralized control-Special status-Intentional

b. Align: congruous

7.    a. All agents or a

collection-Decentralized

control-Equivalent status-Unintentional

b. Not align: Incongruous Common misconceptions in learning natural selection Researchers (Chi et al., 2012; Gregory, 2009) have recognized that students demonstrated common misconceptions such as teleological perspectives and centralized deterministic mindset s in their reasoning and explanations about natural selection. To address this problem, we  aimed to design a n agent-based simulation module to help students better observe the mechanisms that drive the emergence of population-level phenomena from smaller scales of agent interactions, understand the random and nonlinear characteristics of the systems, and adopt an unintentional and decentralized perspective in understanding the emergent proce ss of natural selection. Agent-based models and revisions In agent-based modeling (ABM), the term “agent” indicates individual computational actor s that obey simple rules. It is the Interactions between these Agents that give rise to emergent Patterns in complex systems. Because the nature of ABM  aligns well with the PAIR-C framework, we used the NetLogo agent-based modeling environment (Wilensky, 1999) to construct our simulation models. A recent meta-analysis on simulations for STEM learning found that when the simulation was very structured (i. e. students use the simulation with a prescribed path), it resulted in more cognitive gains than when the simulatio n allowed for more flexibility in the student interaction with the simulation (D’Angelo et al., 2014). Therefore, we deci ded to use ABM as a representational tool and design a structured learning trajectory for students to navigate the simulation module. In searching for ABM simulations, we selected the NetLogo wolf-sheep predation model (Wilensky,

1997) and identified six issues within this model based on the PAIR-C framework. These were: a) The Patterns

of current simulations focus on moving entities rather than representing dynamic cha nges across multiple generations; b) The way to introduce external Agents (e.g. wolves-predators) may induce misconceptions that external agents also participate in the pattern; c) Agents’ Interactions (e.g. mating interaction; chasing interaction) are not visible in the simulation. Only the agents’ actions (e.g. sheep randomly move) are shown; d) Relations among the Interactions are not visible from watching the random movement of agents; e) The Causal relation characteristics between the agents-pattern (how the pattern converges) are not displayed;  f) The collective summing Causal mechan isms (how the pattern is produced) are not explained.  We incorporated these identified issues and modified the wolf-sheep predation model  in the PAIR-C simulation module. The resulting PAIR-C simulation module will be introduced in the Findings section.

## Participants and research design

This online experiment was conducted among 28 participants. These participants were high school students from two science extracurricular programs. Participants were assigned to one of two conditions. Students in the experimental condition  (n = 14) were given three modules: 1) an overarching PAIR-C Process Module containing information about the concept of emergent causality by comparing and contrasting ever y day “emergent” and “sequential” processes; 2) a PAIR-C Natural Selection Lecture; 3) a PAIR-C Simulation Module. Students in the control condition (n = 14) were given three modules as well: 1) a Nature of Science Module, a traditional module introducing the philosophy and methods of scientific exploration; 2) a “Business as Us ual (BAU)” Natural Selection Lecture; 3) a BAU Bunny Simulation Module. The BAU bunny simulation is created based on a n interactive PhET simulation on Natural Selection. The study involves three tests: p re-test, post-test 1 (after the Natural Selection Module), and post-test 2 (after the Simulation Module). Data sources Several different data sources allow researchers to investigate the effectiveness of the PAIR-C simulation module over the BAU simulation module in terms of diagnosing and reducing misconceptions when learning the emergent process of natural selection. A repeated test measure (from pretest to posttest 2, from posttest 1 to posttest 2) was used to examine knowledge gains. Prompt questions embedded in the simulation module also revealed students’ formative performance  and misconceptions. A feedback survey inserted at the end of the module provide d evidence on engagement, module clarity, and learning experience. Each simulation module consisted of seven parts and three scenarios. Both simulation modules used two types of prompts. The first type of prompts consists of questions that expect students to find clues from observing the simulations. These questions include true or false (T/F) questions, yes or no (Y/N) questions, open-ended (OE) questions, and two-tiered questions (the first-tier is a Y/N question while the second-tier is an OE question asking for explanation). All of these questions were coded and scored  based on PAIR-C features shown in Table 1. Overall, students in both groups answered a total of 9 open-ended questions and 21 objective questions which were matched as much as possible to be the same for both conditions.  In addition to assessing how students understood the emergent process of natural selection, the second type of prompts was designed not to measure understanding but to better engage students while working through the simulation module.

## Procedure and data analyses

The PAIR-C simulation module  was operated using Google Form, through which the researcher could conveniently collect students’ responses. To examine students’ misconceptions about natural selection, we coded student responses to prompt questions within the simulation module. We deliberately designed non-leading prompt questions for the PAIR-C simulation module and the BAU Bunny simulation module  to ensure the students’ responses to the 9 open-ended prompt questions and the 21 objective questions were comparable across the two condition s. We used a t wo-step process to score students’ responses to the 9 OE questions and later conducted statistical analyses. First, each open-ended prompt was scored for correctness (a score of  2 was given to accurate and complete answers; 1 for accurate but not complete responses; 0 for inaccurate responses). Second, for responses that scored 1 or 0, the responses were coded using the PAIR-C Framework for misconceptions in student responses. In this second step, we also marked un decided responses and other types of errors that led to that score (usually incomplete responses). The responses with scores of 2 were also screened to make sure they were not showing misconceptions. The coding rubric for each OE prompt question was established and checked by two experienced coders (See Table 2 for a sample rubric established by two coders). Table 2: The coding rubric and sample responses for prompt Q7b Score PAIR-C Simulation Prompt Q7b Bunny Simulation Prompt Q7b Rubric: This question was designed to assess the understanding of the collective summing feature.

• 2 (correct and complete): collective summing within each unit of time (primary feature) +

mentioning one of the secondary features (e.g. misalignment; unrestricted relations)

• 1 (correct but not complete): Only mentioning secondary features or implications

• 0 (incorrect): showing misconceptions

2 The number of white sheep is not always increasing, so this is not just about white sheep increasing via

## mating. Instead, this is a result of white sheep

increasing or decreasing via mating, (collective summing) and brown sheep increasing or decreasing

## via mating. So this does not always result in the

number of white sheep increasing (not just mating between white sheep; both brown and white sheep can mate randomly). OR Considering both the white sheep and the brown sheep, and the mating interactions of all sheep, the white sheep don't have to increase in every generation (collective summing), but the percentage of white sheep has an increasing pattern (not align).

The number of long-toothed bunnies is not always increasing, so this is not just about long-tooths increasing via mating. Instead,

## this is a result of long-tooths increasing or

decreasing via mating, and short-tooths increasing or decreasing via mating.  So

## this does not always result in the number

of long-tooths increasing (not just mating between long-tooths; both long and shorttoothed bunnies can mate). OR Considering both the long-tooths and the short-tooths, and the mating interactions of all bunnies, long-toothed bunnies don't have to increase in every generation, but the percentage of longtoothed bunnies has an increasing pattern. 1 only explains misalignment but not collective summing. The percentage of white sheep over brown sheep is always increasing but the number of individuals may not always increase. (Only

## mentioning not align implication)

doesn’t say long-toothed bunnies always increase or not; just mentioning long-tooth has an advantage due to environmental factor 0 White sheep are always added to the population between generations to create a pattern of white sheep becoming more common. As white sheep increase, brown sheep will decrease. (Misconception: align, cumulative summing) When time goes on, the long teethed bunny population increases. Therefore, in each generation, long-toothed bunnies are added to the population.

## Findings and discussion

Designing PAIR-C simulation The original wolf-sheep predation model described a set of rules that govern the behaviors (e.g. to move, to reproduce, to eat-sheep, to grow-grass, etc.) of individual computational agents (e.g. sheep, wolves, and grass). As the model runs, all agents con currently act out their rules without explicitly showing the interactions. To let the audience see what is exactly happening, we made the interactions between agents visible by adding rules to represent interacting agents (e.g. sheep-sheep reproduction, wolves-sheep chasing, See Figure 1 for example).

(a)                                                                   (b)

Figure 1. The revised wolf-sheep predation scenario (a) with codes (b).

Upon finishing the revision of models, we had addressed the problems of visualizing interactions (problem c) and introducing external agents separately in  a later scenario (problem b). To solve the remaining problems, we proceeded with creating the online simulation module. The PAIR-C simulation module contains four basic elements to fix the remaining problems: simulation videos, ABM screenshots, animated pictures, and nonleading prompts. There are 6  simulation videos in the module. Some videos were edited with subtitles that convey clarifying information about the generation periods, the number of sheep, or the percentage of sheep. We also captured static screenshots to show relations among sheep interactions (problem d) as well as  generate dynamic patterns across different time periods (problem  a) to demonstrate convergence and collective summing mechanism (problem e and f). Meanwhile, animated pictures were used at two differe nt locations to direct students’ attention to specific simulation features so that they could intuitively draw implications (i.e. decentralized, equivalent status, unintentional  property) to interpret the causal relations between the agents and pattern.

Contrasting PAIR-C simulation with non-PAIR-C simulation It was found that the PAIR-C simulation is different from the non-PAIR-C (BAU bunny) simulation in three major aspects, considering how students interact with the simulation (interactiv ity); what is being represented (visibility), and what is being taught in the simulation (learnability). Interactivity The PAIR-C simulation was used as a multimedia presentation tool which includes simulati on videos, ABS screenshots, and animated pictures. Students interact with it mainly by observati on while they could also adjust the speed, replay the simulation videos as well as responding to the embedded prompts  at their own pace. The prompts require students to generate new inferences beyond observing or manipulating the simulation videos. Noticeably, the non-PAIR-C simulation is often an embodied simulation tool  that allows students to manipulate conditional variables within the simulation. The non-PAIR-C simulation often features an active mode of cognitive engagement when students are only manipulating the simulation (Chi et al.,  2018) without generating new inferences from the presented simulation. Besides, in the context of learning natural selection, allowing the unrealistic agency to manipulate simulation tends to reinforce misconceptions ab out intentionality and special status (see Table 1). In this study, the non-PAIR-C bunny simulation was presented through videos in the same structure as the PAIR-C condition.

Visibility Students often have difficulties seeing the mechanisms that produce the dynamic changing pattern in simulations (Chi, 2005). The PAIR-C simulation solved this problem by using “links” to visualize interactions among agents and showing collective interactions across multiple generations in multiple ABM scr eenshots. In contrast, the non-PAIR-C simulation only shows agents’ actions or movements at each generation. The  bunny simulation directs attention to moving entities rather than how the pattern is produced. For example, in the bunny simulation, students are not able to tell the rand om nature of the interactions among bunnies through the Pedigree chart (see Figure 2).

(a)                                                                   (b)

Figure 2. Comparing simulation interface (a) PAIR-C simulation and (b) Bunny simulation.

Learnability In the PAIR-C simulation module, collective interactions of all agents are counted, nonlinear agents-pattern causal relations that incur misconceptions are explicitly emphasized, and aspects of the Relations among the Interactions are also examined  (see Table 1). Conversely, the non-PAIR-C simulation  showed individualistic actions of a subgroup, represented linear causal relations between conditions and their consequences on the pattern. Features of the Relations are always not mentioned.

The PAIR-C simulation module Pre-posttest A repeated test measure was used in this study, including the pretest, postte st1 (given after the Natural Selection Module), and posttest2 (given after the Simulation Module). This test consists of 20 multiple-choice questions. Among them, 12 questions were hard-level questions, which assessed understandings of different PAIR-C features in the context of natural selection. There were also 5 medium and 3 easy-level factual questions. The majority of these questions were adapted from  multiple conceptual inven tories (e.g. CINS, CANS, AAAS, and past AP Biology Exams from College Board) with two hard-level questions created by a senior researcher. To determine whether students’ scores improve for hard-level questions over time, we conducted a paired samples T-test. The analysis showed that there was no statistically significant improvement  from pretest to posttest2 for the  control condition, while there was a statistically significant improvement from pretest to posttes t2 for the experimental condition, (t(13) = -2.86, p < 0.05). Using pre-test hard questions as a covariate, we conducted ANCOVA and compared students’ scores on post-test2 hard questions to see if we could find a  significant difference between the two groups. There was no statistical significance found between two groups, F (1, 25) =.388, p =.539, partial η2 =.015.

Within module assessment To examine differences in scores for PAIR-C features between conditions, we combined open-ended questions that shared the same features and ran independent t-tests for each feature. Most of the tests were not significant, except for one type: collective summing  (see Figure 3).  This shows that  the PAIR-C simulation group had significantly higher score s than the BAU bunny simulation  group when explaining the collective summing mechanism (t(26) = 2.82, p < 0.01).

Figure 3. Average scores by condition for open-ended prompt questions.

0 1 2 3 4 5 Pattern Agents Collective Summing Not Align Unintentional Score PAIR-C BAU * The number and type of misconceptions that were found in student responses to the  open-ended prompt questions were also counted. Overall, there were 21 misconceptions found for the BAU condition while there were 15 misconceptions found for the i ntervention PAIR-C condition, including the undecided misconceptions. We found that there were 7 instances of restricted relations misconceptions f or BAU while there were none for PAIR-C. Because numerous responses demonstrated at least two categories of misconceptions based on the PAIRC framework, we decided to present the frequency of misconceptions instead of the number of student responses showing misconceptions (See Figure 4).

Figure 4. Frequency of misconception types by condition for open-ended prompt questions.

In addition to the open-ended prompt questions, there were 21 objective prompt questions in each of the simulation modules. The 21-question is composed of 2 items on environmental conditions;12 items on Relations (unrestricted, same set, simultaneous, independent); 1 on the external agent; 2 on no causal agent; 1 on non-alignment; 2 on converging pattern; 1 on collective summing. The average scores of these 21 objective prompts were 19.64 for the PAIR-C condition, and 16.50 for the BAU condition (See Figure 5 for the score distributi on). A two-sample t-test w as conducted which showed a statistically significant difference between the PAIR-C condition and the BAU condition (t(18) = 3.83, p < 0.01). This result indicates that our PAIR-C simulation module might have a better effect in reducing common misconceptions.

(a)                                                                                   (b)

Figure 5. Frequency of score distribution for (a) PAIR-C and (b) BAU conditions on 21 objective prompts.

Feedback survey The post-simulation survey questions asked students to report engagement, module clarity using a 1-5 Likert Scale. Students in the experimental condition reported an average of 4.14 for engagement and 4.21 for clarity. For the control condition, the average scores for engagement and clarity w ere 3.86 and 3.36 respectively. We also asked students to describe their experience in using the simulation videos. Nine students from the PAIR-C condition reported that they only played the simulation once. However, only two students from the  BAU condition expressed that they played the simulation videos once. Other students from the  BAU group  stated that they replayed the majority of the videos multiple times. This further manifests the efficiency and clarity of using PAIRC simulation to represent agent relations among interactions as well as explai n the causal mechanism for the emerging pattern. Several students from both conditions suggested that the simulation module could be improved by including more simulation models as examples, and would be more engaging if a narration was provided. 0 2 4 6 8 10 Restricted Cumulative Summing Align External Agents Intentional Undecided Frequency PAIR-C BAU

## Conclusion

We believe that our PAIR-C simulation module has scholarly implications for simulation-based online teaching practice. Our results highlight the importance of using a simulation module grounded in the agent-based modeling approach and the PAIR-C theoretica l framework to scaffold student learning in natural selection as emergent processes. From sorely looking at the simulation prompt data, we found that the PAIR-C simulation with non-leading prompts was able to reveal some important misconception features that other traditional simulations could not capture. However, this study could not validate the effectiveness of the PAIR-C simulation without comparing it with standard agent-based simulation. To address this limitation, future works can focus on conducting a standalone study to compare the improved agent-based simulation with PAIR-C features and standard agent-based simulation without PAIR-C features.

## References

Chi, M. T. (2005). Commonsense conceptions of emergent processes: Why some misconceptions are robust. The journal of the learning sciences, 14(2), 161-199. https://doi.org/10.1207/s15327809jls1402_1 Chi, M. T. (2013). Two kinds and four sub-types of misconceived knowledge, ways to change it, and the learning outcomes. In International handbook of research on conceptual change (pp. 49-70). Chi, M. T., Adams, J., Bogusch, E. B., Bruchok, C., Kang, S., Lancaster, M.,... & Yaghmouria n, D. L. (2018). Translating the ICAP theory of cognitive engagement into practice. Cognitive science, 42(6), 1777-1832. https://doi.org/10.1111/cogs.12626 Chi, M. T., Kristensen, A. K., & Roscoe, R. (2012). Misunderstanding emergent ca usal mechanism in natural selection. Evolution challenges: Integrating research and practice in teaching and learning about evolution, 145-173.

Chi, M. T. (under review).  Individualistic versus collective causality: An ontology framework for analyz ing processes, explaining misconceptions, and guiding instruction. Educational Psychologist. Basu, S., Sengupta, P. & Biswas, G. A Scaffolding Framework to Support Learnin g of Emergent Phenomena Using Multi-Agent-Based Simulation Environments.  Res Sci Educ  45, 293–324 (2015). https://doi.org/10.1007/s11165-014-9424-z D’Angelo, C., Rutstein, D., Harris, C., Bernard, R., Borokhovski, E., & Haertel, G. (2014). Simulations for STEM learning: Systematic review and meta-analysis. Menlo Park: SRI International. Dickes, A. C., Sengupta, P., Farris, A. V., & Basu, S. (2016). Developme nt of Mechanistic Reasoning and Multilevel Explanations of Ecology in Third Grade Using Agent-Based Models. Science Education, 100(4), 734–776. https://doi.org/10.1002/sce.21217 Gregory, T. R. (2009). Understanding natural selection: essential concepts and common mis conceptions. Evolution: Education and outreach, 2(2), 156-175.

Hmelo‐Silver, C. E., Liu, L., Gray, S., & Jordan, R. (2015). Using representational tools to learn about comp lex systems: A tale of two classrooms.  Journal of Research in Science Teaching, 52(1), 6-35. https://doi.org/10.1002/tea.21187 Hmelo‐Silver, C. E., & Pfeffer, M. G. (2004). Comparing expert  and novice understanding of a complex system from the perspective of structures, behaviors, and functions.  Cognitive science, 28(1), 127-138. https://doi.org/10.1207/s15516709cog2801_7 Jacobson, M. J., Kapur, M., So, H. J., & Lee, J. (2011). The ontologies of complexity and learning about complex systems. Instructional Science, 39(5), 763-783. https://doi.org/10.1007/s11251-010-9147-0 Wilensky, U., & Jacobson, M. J. (2014). Complex systems and the learning sciences. In The Cambridge handbook of the learning sciences, Second Edition (pp. 319-338). Cambridge University Pr ess. https://doi.org/10.1017/CBO9781139519526.020 Wilensky, U. (1997). NetLogo Wolf Sheep Predation model. http://ccl.northwestern.edu - /netlogo/models/WolfSheepPredation. Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.

Wilensky, U. (1999). NetLogo. http://ccl.northwestern.edu/netlogo/. Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL. Yoon, S. A., Goh, S. E., & Park, M. (2018). Teaching and learni ng about complex systems in K –12 science education: A review of empirical studies 1995 –2015. Review of Educational Research, 88(2), 285-325. https://doi.org/10.3102/0034654317746090

## Acknowledgments

This research was funded by the Institute of Education Sciences (R305A150336).

