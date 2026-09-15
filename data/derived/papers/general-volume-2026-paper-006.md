# Designing an AI-Powered Reflective Partner: Translating Self-Regulated Learning Theory into Generative Chatbot Scaffolds

**Conference:** ISLS 2026

## Abstract

This interactive tool paper presents the design and development of an AI-powered chatbot that scaffolds college students’ self-regulated learning (SRL). Grounded in Pintrich’s SRL framework and informed by meta-analytic evidence on effective SRL interventions, the chatbot is designed as a reflective learning partner that supports metacognitive monitoring, strategic deployment, and affective regulation. Using a design-based research (DBR) approach, this study explores how SRL theory can guide the development of generative AI–mediated interactions. We describe the theoretical rationale underlying the tool, articulate key design principles, present the prototype’s architecture, and discuss implications for improving evidence-based, equitable AI scaffolds to enhance undergraduate learning outcomes. This interactive tool paper presents the design and development of an AI-powered chatbot that scaffolds college students’ self-regulated learning (SRL). Grounded in Pintrich’s SRL framework and informed by meta-analytic evidence on effective SRL interventions, the chatbot is designed as a reflective learning partner that supports metacognitive monitoring, strategic deployment, and affective regulation. Using a design-based research (DBR) approach, this study explores how SRL theory can guide the development of generative AI–mediated interactions. We describe the theoretical rationale underlying the tool, articulate key design principles, present the prototype’s architecture, and discuss implications for improving evidence-based, equitable AI scaffolds to enhance undergraduate learning outcomes. Designing an AI-Powered Reflective Partner: Translating SelfRegulated Learning Theory into Generative Chatbot Scaffolds Na Liu, John Nietfeld nliu22@ncsu.edu, jlnietfe@ncsu.edu North Carolina State University Abstract: This interactive tool paper presents the design and development of an AI-powered chatbot that scaffolds college students’ self-regulated learning (SRL). Grounded in Pintrich’s SRL framework and informed by meta-analytic evidence on effective SRL interventions, the chatbot is designed as a reflective learning partner that supports metacognitive monitoring, strategic deployment, and affective regulation. Using a design-based research (DBR) approach, this study explores how SRL theory can guide the development of generative AI–mediated interactions. We describe the theoretical rationale underlying the tool, articulate key design principles, present the prototype’s architecture, and discuss implications for improving evidence-based, equitable AI scaffolds to enhance undergraduate learning outcomes. Self-regulated learning (SRL) is the process by which learners actively manage their cognition, motivation, and behavior to achieve academic goals (Zimmerman, 1986; Pintrich, 2000). While SRL is a strong predictor of academic success in higher education (Broadbent & Poon, 2015), many students continue to underuse metacognitive and motivational strategies despite explicit instruction (Cao & Nietfeld, 2007). Existing SRL interventions, such as semester-long SRL courses (Bail et al., 2008), reflective diaries (Dörrenbächer & Perels, 2016), and LMS-integrated training modules (Bernacki et al., 2020), have demonstrated small to moderate effects (Theobald, 2021). These efforts consistently face limitations related to scalability, personalization, and sustained learner engagement. Generative artificial intelligence (AI) introduces new opportunities to address these pedagogical constraints by delivering adaptive, context-sensitive scaffolding at scale. Chatbots powered by large language models (LLMs) can engage students in human-like, reflective dialogue and provide timely, personalized feedback. Early studies suggest such systems can enhance motivation, self-efficacy, and strategic learning behaviors (Ng et al., 2024; Pan et al., 2024). This project therefore bridges AI’s technological affordances with the pedagogical rigor of learning sciences theory by designing and testing a SRL chatbot grounded in empirical evidence and models of self-regulation to foster reflection, strategy use, and metacognitive growth. Purpose of the study The overarching goal is to design, implement, and evaluate an AI-powered SRL chatbot that functions as a reflective partner rather than an answer-giving tutor. Specifically, this study aims to:

1. Translate SRL theory into conversational scaffolds that foster self-reflection, metacognitive monitoring,

and strategic regulation.

2. Establish a design-based research (DBR) process that iteratively refines the chatbot through user

feedback and pedagogical validation.

3. Examine how learners across subjects engage with and respond to AI-empowered SRL support

Theoretical foundations The chatbot's architecture draws upon Pintrich’s (2000) four-phase SRL model: forethought/planning, monitoring, control, and reflection. This model is highly suitable for educational technology design as it delineates specific, targetable processes while integrating critical motivational and affective dimensions often underrepresented in simpler frameworks. The AI’s dialogue is constructed to guide the learner through each phase: setting goals (forethought), self-monitoring, adapting strategies (control), and assessing outcomes (reflection). Complementing this framework, this design incorporates meta-analytic findings (Jansen et al., 2019; Theobald, 2021) that identify key features of effective SRL interventions:

• Emphasis on metacognitive strategy training (g = 0.40) and resource management (g = 0.39).

• Integration of Feedback and reflection protocols (learning diaries, goal sheets).

• Contextual tailoring and ongoing, phased support to promote persistence and transfer.

D esign principles and AI affordances Drawing on SRL theory, empirical findings, and the affordances of large language model, the chatbot was designed around seven guiding principles:

1. Personalized SRL Support: The chatbot begins by assessing the learner’s prior knowledge, current

motivation, and strategy use to provide truly tailored prompts and adaptive feedback,

2. Metacognitive Reflection Prompts: Frequent, open-ended questions, such as “How do you usually

monitor your learning progress?”, are used to encourage awareness of cognitive and motivational processes (Winne & Azevedo, 2022).

3. Guidance through Learning Protocols: The chatbot supports structured planning and reflection tools (e.g.,

progress trackers, reflection logs) to foster consistency and intentionality, particularly when integrated with LMS environments.

4. Ongoing Multiphase Support: The bot remains available throughout all SRL phases (planning,

monitoring, reflection) to provide continuity and temporal scaffolding and feedback.

5. Domain-Specific Strategy Feedback: By using retrieval-augmented generation (RAG), the chatbot

allows learners to upload syllabi or course readings. This will dramatically reduce hallucinations and enable context-specific strategy suggestions.

6. Affective Support and Emotion Regulation: The chatbot is designed to detect cues of frustration or

disengagement and responds with affirmations or coping suggestions, supporting persistence

7. Feedback Usefulness Check-Ins: Learners periodically evaluate the usefulness and fairness of chatbot

feedback. These meta-dialogues enhance metacognitive calibration and help identify potential biases in AI-generated responses. Together, these principles illustrate how AI affordances (adaptivity, personalization, and natural language generation) can be harnessed within a learning-sciences framework (metacognition, motivation, scaffolding) to promote theoretically grounded learning support. Prototype interface and functionality The SRL Learning Assistant prototype (Figures 1 to 6) was developed using Botpress, a platform for building custom AI agents and chatbots, to translate the self-regulated learning model into an interactive conversational environment. Grounded in Pintrich’s (2000) four phases of SRL, it uses a structured dialogue flow to guide learners through planning, monitoring, control, and reflections. In line with the study’s goal of designing the chatbot as a reflective partner, this role is realized through prompt level rules that keep the interaction focused on learner’s SRL process rather than task completion. For example, when students ask for full answers or solutions, the bot is instructed not to provide them directly. Instead, it briefly acknowledges the request, offers a minimal starter example only when needed, suggest a strategy or next step, and poses a follow up question that prompts further thinking. During onboarding (Figure 1), learners provide a preferred name or nickname to establish social presence and rapport. They are also invited to share relevant course materials, such as a syllabus or assignment brief, so that the chatbot can contextualize its prompts and feedback based on the task. In the Planning phase (Figure 2), the chatbot invites students to articulate specific, measurable learning goals (e.g., “What’s your main academic goal this week?”), and follows up with structured prompts that help break tasks into manageable steps, anticipate potential challenges, and plan for self-monitoring. Figure 3 illustrates the three remaining phases of the chatbot interface. The Metacognition phase (a) supports the monitoring and evaluation of cognitive processes through reflective questioning, such as “How do you usually track your progress?”. The Strategy Control phase (b) engages learners in assessing the effectiveness of their learning strategies and fostering adaptive regulation (e.g., “What strategies have worked well or not as expected?”). Finally, the Reflection phase (c) focuses on emotional regulation and learning transfer, prompting learners to consider their affective experiences and future goals (e.g., “How do you feel about your learning this week? What insights could guide you moving forward?”). Figure 1 Onboarding Interface Figure 2 Planning Phase Figure 3 Chatbot interfaces illustrating the Metacognition (a), Strategy Control (b), and Reflection (c) phases.

(a) (b) (c)

Design-based research approach The chatbot’s development follows a Design-Based Research methodology emphasizing iterative co-design, theory refinement, and empirical grounding. The project is currently in an early DBR cycle focused on translating SRL theory into a functional conversational bot prototype and examining initial feasibility, usability, and alignment between intended scaffolds and actual interaction flow.

• Cycle 1 (Exploratory Design): Defined pedagogical and functional requirements based on SRL theory

and empirical work, with particular attention to how planning, monitoring, control, and reflection could be translated into conversational scaffolds.

• Cycle 2 (Prototype Development and Expert Review): Implemented the prototype in Botpress and

developed theory informed prompts, workflow logic, and cross session logging functions. Initial expert review provided formative evidence that the chatbot’s phase structure, reflective stance, and supportive tone were generally clear. On a 5-point scale, reviewers rated it 4.75 for prompt clarity, 4.5 for avoiding over directing or answer giving, 4.3 for emotional support, and 4.0 for phase structure clarity. Its overall rating as an effective SRL support tool was 3.5. Reviewers also identified several priorities for refinement, including strengthening task specific prompting, merging the monitoring and control phases, adding attribution support within the reflection phase, and providing phase entry guidance for learners unfamiliar with SRL.

• Cycle 3 (Small Scale Pilot Testing): Will deploy the refined prototype with students in short term,

individual task-based testing to further examine usability, engagement, and the quality of students’ planning, monitoring, strategy adjustment, and reflection. This cycle will also test the chatbot’s cross session information retrieval function to determine whether it can maintain continuity across interactions, provide consistent feedback, and generate weekly or semester level progress reports based on students’ activity across multiple sessions.

• Cycle 4 (Refinement and Extended Embedding): Will use the small-scale evidence from Cycle 3 to make

final refinements before wider course-based implementation. In this cycle, the study will examine longer term questions about how students use the chatbot across a semester, whether repeated interaction supports improvement in self-regulated learning processes, and how the quality of learner engagement changes over time. Data will be collected longitudinally through chatbot interaction logs, phase completion and transition patterns, the depth and quality of learner responses, indicators of strategy monitoring or adjustment across turns, usability and engagement feedback, and follow up user comments or interviews. These data will be used to refine prompt phrasing, pacing, memory functions, and adaptive logic, while also examining the chatbot’s potential influence on students’ self-regulated learning and learning outcomes in an authentic course context. Through this iterative process, the chatbot functions both as a learning tool and as a research instrument for studying AI-mediated self-regulation. Implications and future directions This work demonstrates how design principles derived from SRL theory and prior empirical evidence can be translated into an AI supported conversational tools. It highlights the potential for AI to function as a reflective co-partner that fosters learner agency and metacognitive growth, rather than replacing human instruction. At this stage, the contribution lies in showing how SRL principles can be operationalized through prompt design, workflow structure, and task grounded interaction. What remains to be tested more directly is how students engage with the chatbot over time and whether sustained use supports measurable changes in self-regulated learning processes and outcomes. Future research will focus on three interrelated directions:

• Exploring how SRL prompt and feedback can be applied across different subject areas.

• Evaluating the chatbot’s impact on students’ metacognitive growth and learning outcomes.

• Examining how this AI-powered SRL chatbot might support underrepresented groups in their transition

to college learning.

This prototype contributes to the ISLS community by demonstrating how theory-informed design and AI affordances can converge to enhance SRL at scale. By articulating its design logic and empirical grounding, this work positions the chatbot as both a pedagogical innovation and a research vehicle for advancing understanding of reflective learning with AI in an inclusive way. Reference Bail, F. T., Zhang, S., & Tachiyama, G. T. (2008). Effects of a self-regulated learning course on the academic performance and graduation rate of college students in an academic support program. Journal of College Reading and Learning, 39(1), 54–73. https://doi.org/10.1080/10790195.2008.10850312 Bernacki, M. L., Vosicka, L., & Utz, J. C. (2020). Can a brief, digital skill training intervention help undergraduates “learn to learn” and improve their STEM achievement? Journal of Educational Psychology, 112(4), 765–781. https://doi.org/10.1037/edu0000405 Broadbent, J., & Poon, W. L. (2015). Self-regulated learning strategies & academic achievement in online higher education learning environments: A systematic review. The Internet and Higher Education, 27(1), 1–13. https://doi.org/10.1016/j.iheduc.2015.04.007 Cao, L., & Nietfeld, J. L. (2007). College students’ metacognitive awareness of difficulties in learning the class content does not automatically lead to adjustment of study strategies 1. Australian Journal of Educational and Developmental Psychology, 7, 31–46. D örrenbächer, L., & Perels, F. (2016). More is more? Evaluation of interventions to foster self-regulated learning in college. International Journal of Educational Research, 78, 50–65. https://doi.org/10.1016/j.ijer.2016.05.010 Jansen, R. S., van Leeuwen, A., Janssen, J., Jak, S., & Kester, L. (2019). Self-regulated learning partially mediates the effect of self-regulated learning interventions on achievement in higher education: A meta-analysis. Educational Research Review, 28, 100292. https://doi.org/10.1016/j.edurev.2019.100292 Ng, K., Chee Wei Tan, & Lok, K. (2024). Empowering student self-regulated learning and science education through ChatGPT: A pioneering pilot study. British Journal of Educational Technology, 55(4). https://doi.org/10.1111/bjet.13454 Pan, M., Guo, K., & Lai, C. (2024). Using Artificial Intelligence chatbots to support English-as-a-Foreign Language students’ self-regulated reading. RELC Journal. https://doi.org/10.1177/00336882241264030 Pintrich, P. R. (2000). The role of goal orientation in self-regulated learning. Handbook of Self-Regulation, 451–

502. https://doi.org/10.1016/b978-012109890-2/50043-3

Theobald, M. (2021). Self-regulated learning training programs enhance university students’ academic performance, self-regulated learning strategies, and motivation: A meta-analysis. Contemporary Educational Psychology, 66, 101976. https://doi.org/10.1016/j.cedpsych.2021.101976 Winnie, P., & Azevedo, R. (2024). Metacognition and self-regulated Learning. In The Cambridge Handbook of the Learning Sciences (pp. 93–113). Cambridge University Press. Zimmerman, B. J. (1986). Becoming a self-regulated learner: Which are the key subprocesses? Contemporary Educational Psychology, 11(4), 307–313. https://doi.org/10.1016/0361-476x(86)90027-5

