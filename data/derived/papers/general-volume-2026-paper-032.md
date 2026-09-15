# SEED: A Teachable-Agent System that Supports Elementary Students’ Self-Explanation by Teaching an AI Chatbot

**Conference:** ISLS 2026

## Abstract & Introduction

### Abstract
Self-explanation is a powerful strategy for conceptual understanding, yet elementary students struggle to produce coherent explanations without individualized scaffolding. LLM-based teachable agents offer a promising alternative—positioning the learner as teacher and the AI as student, leveraging the protégé effect to deepen understanding—yet most existing work targets undergraduate learners, leaving elementary students largely unaddressed. This demo introduces SEED (Self-Explanation Eliciting Dialogue), a prototype teachable-agent system that positions the child as the teacher and the AI as a novice learner. SEED features a role-reversal prompt engine, three-stage scaffolding flow, growth visualization, and auto-generated learning notebooks—all designed to sustain the protégé effect. This work demonstrates that LLM-based teachable agents, when designed around developmental principles, can meaningfully support self-explanation among elementary learners.

SEED: A Teachable-Agent System that Supports Elementary Students’ Self-Explanation by Teaching an AI Chatbot Seoyeon Lee, Haeun Choa, Dukhoi Koo eduseoyeon@gmail.com, choahaeun@gmail.com, dhk@snue.ac.kr Seoul National University of Education Abstract: Self-explanation is a powerful strategy for conceptual understanding, yet elementary students struggle to produce coherent explanations without individualized scaffolding. LLMbased teachable agents offer a promising alternative—positioning the learner as teacher and the AI as student, leveraging the protégé effect to deepen understanding—yet most existing work targets undergraduate learners, leaving elementary students largely unaddressed. This demo introduces SEED (Self-Explanation Eliciting Dialogue), a prototype teachable-agent system that positions the child as the teacher and the AI as a novice learner. SEED features a rolereversal prompt engine, three-stage scaffolding flow, growth visualization, and auto-generated learning notebooks—all designed to sustain the protégé effect. This work demonstrates that LLM-based teachable agents, when designed around developmental principles, can meaningfully support self-explanation among elementary learners. Self-explanation is a well-established learning strategy that supports conceptual understanding and knowledge integration (Chi et al., 1994). However, learners often struggle to spontaneously generate high-quality selfexplanations on their own (Renkl, 1997). This challenge is particularly pronounced among elementary students, who are still developing the metacognitive skills needed to monitor and regulate their own understanding (Flavell, 1979). Although prompting students to self-explain can substantially deepen their understanding (Chi et al., 1994), providing individualized scaffolding to every learner in a classroom of nearly thirty students remains a persistent challenge for a single teacher.

Recent generative AI systems are often designed to respond to users' questions immediately and deliver information with ease, which risks inducing cognitive offloading—the outsourcing of cognitive processing to AI—among students (Risko & Gilbert, 2016; Gerlich, 2025). A more productive alternative is the teachable agent model, in which the learner assumes the role of teacher and the AI assumes the role of student. This framework leverages the protégé effect—the tendency to invest greater effort and achieve deeper understanding when one believes their explanations are helping another learn (Chase et al., 2009). Early teachable agent systems such as Betty's Brain demonstrated these effects (Leelawong & Biswas, 2008), yet relied on rule-based architectures that imposed limits on flexibility and scalability. More recently, researchers have begun exploring LLM-based teachable agents capable of open-ended dialogue (Jin et al., 2024; Kucharavy et al., 2025; Rogers et al., 2025). However, most of this work targets undergraduate learners, leaving the needs of elementary students largely unaddressed.

This demo introduces SEED (Self-Explanation Eliciting Dialogue), a teachable-agent prototype that positions the student as the "teacher" and the AI as the "learning student." Unlike recent LLM-based teachable agent systems, SEED is grounded in developmental and motivational design principles tailored for elementary learners—including psychologically safe, non-evaluative feedback and tangible reinforcement of the protégé effect through growth visualization and auto-generated learning notebooks. Our aim is not to present a polished product, but to share a working prototype and early classroom experiences that expose both the promise and the limitations of LLM-driven teachable agents.

System overview Design principles SEED was developed through a design-based research process involving literature review, needs analysis, and expert validation. Six design principles guided the prototype:

1. Developmentally Appropriate Scaffolding and Language Use

2. Inquiry-Driven Prompts for Explanation Construction

3. Role-Reversal interaction in a Teachable-agent Frame

4. Psychological Safety Through Non-Evaluative Responses

5. Teacher-Centered Monitoring Through a Simple Dashboard Interface

6. Character-Based Growth Visualization to Strengthen the Protégé Role

These principles were operationalized into nine detailed design guidelines through expert validation and were embedded into the system’s prompt design, interface, and teacher dashboard. Architecture SEED follows a four-layer architecture:

• Interface layer: React-based app with (1) home screen, (2) student chat interface with messenger-style

dialogue, (3) teacher dashboard

• Application layer: A lightweight application layer that handles HTTP requests from the client, logs

conversations, tracks basic dialogue state (e.g., current phase in the three-stage flow), and formats API calls using structured system prompts.

• LLM layer: An LLM-based dialogue engine that generates child-directed responses and learning-notebook summaries. The system prompt encodes SEED’s persona, design principles, and scaffolding strategies. Because SEED relies on LLM-based generation, these guidelines are instantiated in contextdependent ways consistent with the generative model's behavior, rather than as rigid rule-based operations.

• Data layer: A simple tabular data store that maintains student accounts, curriculum key concepts, growth

levels, and conversation logs. Key concepts are pre-loaded per lesson and injected into the system prompt; the LLM draws on both these provided concepts and its pre-trained knowledge to interpret student explanations.

A three-stage scaffolding strategy supports explanation development:

1. Elicitation: SEED adopts a curious student persona, inviting the learner to ‘teach’ the topic through free-form explanation.

2. Adaptive feedback: Guided by structured prompts, the LLM tends to follow one of four pathways—

prompting error reconsideration, filling gaps, help-seeking support, or extending reasoning—using conceptual, procedural, metacognitive, and strategic supports.

3. Consolidation: SEED requests integrated re-explanation and generates a “My Learning Notebook”

summary of what it has “learned”. The notebook is generated for the student's reflection and does not update the LLM's parameters or persistent context.

Key features SEED’s role-reversal prompt engine positions the chatbot as a novice learner who consistently addresses the child as "teacher" and requests explanations ("I don't know—could you teach me?"). To deepen relational engagement, students are first invited to give SEED a personal nickname (Figure 1a), fostering a sense of ownership and responsibility toward their protégé from the outset. This ownership is further reinforced through auto-generated Learning Notebooks (Figure 1b) that document what SEED has "learned" from each teaching session, creating the impression that the student's explanations are genuinely building SEED's understanding—a key mechanism for sustaining the protégé effect. SEED also provides growth visualization that progresses from seed → sprout → leaf → flower → fruit as explanations accumulate, offering a tangible representation of the protégé's learning progress.

Figure 1 Learner-Facing Features of SEED: (a) Nickname Setup and (b) Auto-Generated Learning Notebook with Growth Visualization

(a) (b)

I nteraction scenario Figure 2 Interaction Flow A typical SEED interaction begins with SEED's opening prompt inviting the student to explain a concept they have studied (Figure 2) (e.g., "Can you teach me what you learned today?"). The student then provides an initial explanation (e.g., "At the end of Silla, local warlords appeared and began creating new states"), after which SEED applies one of four scaffolded response modes. When a misconception is detected, SEED responds as a confused learner whose prior understanding conflicts with the student's account (e.g., "Hmm, that's a bit different from what I learned before—could you help me understand which part is right?"), prompting conceptual revision without signaling a simple error. When an explanation is incomplete, SEED asks targeted gap-filling questions to elicit missing elements, as illustrated in Figure 3, where SEED prompts the student to elaborate further on the local warlords and new states mentioned in their initial explanation. When a student requests help, SEED provides scaffolded hints that reduce cognitive load without revealing the answer (e.g., "That's okay—can you start by telling me just one thing you remember?"). When an explanation is sufficient, SEED extends reasoning through hypothetical and critical questions that encourage deeper thinking (e.g., "If you were the ruler at that time, what would you have done?"). This iterative exchange continues until SEED requests a final explanation, prompting the student to synthesize the full interaction into a consolidated response. This protégé framing motivates learners to refine their explanations more actively. As students provide higher-quality explanations, growth visualization appears and a learning notebook is generated to reinforce metacognitive reflection.

Figure 3 Example of SEED’s supplement-based prompt interaction I mplementation SEED was implemented as a web-based prototype with a React front-end deployed on Vercel, a Google Apps Script back-end that handles API calls and logs conversations, Google Sheets as a lightweight data store, and an OpenAI GPT-4–based dialogue engine driven by structured system prompts. The prototype was iteratively refined through fifth-grade classroom deployment, teacher feedback, and conversation log analysis.

## Preliminary findings

In an initial classroom deployment with fifth-grade students, many described SEED as "a younger student I want to help," suggesting that the protégé framing fostered psychological safety and a sense of responsibility. While some students initially questioned whether SEED truly did not know the material, this was mitigated by SEED's design as a curious and confused learner rather than a knowledge-withholding agent—a framing that positions SEED's responses as genuine expressions of uncertainty rather than implicit error signals. Engagement was further reinforced through the learning notebook and growth visualization, which supported the impression of SEED's ongoing learning over time.

Interactive demo session This interactive demo will let participants:

• Experience SEED as a “teacher”. Participants will interact with SEED directly and observe how it

responds adaptively to their explanations. For the conference demo, a topic accessible to international attendees will be used in place of the Korean history content shown in the examples above.

• Explore learner-facing features: growth visualization and the learning notebook. The demo will show

how SEED represents its “learning progress” through growth levels and automatically generates a learning notebook summarizing what SEED has understood, reinforcing the protégé framing.

• Inspect the teacher dashboard. Participants can switch to the teacher view to review conversation logs,

monitor students’ SEED levels, access auto-generated summaries, and observe how the dashboard supports lightweight classroom management.

• Examine SEED’s underlying prompt and data structures. The demo will showcase how SEED’s three-stage scaffolding strategy is implemented using prompt templates and structured data stored in Google Sheets, allowing participants to see how the system generates adaptive responses through LLM-based prompting rather than hard-coded rules.

## Implications and conclusion

Taken together, SEED demonstrates that inverting the conventional AI-as-tutor framing—positioning the LLM as a novice learner rather than an expert explainer—can create conditions for deeper self-explanation and protégélike engagement in elementary classrooms. For designers and teachers, our work highlights that how an AI is framed may matter as much as what it does. Limitations include a single subject domain and the probabilistic nature of LLM-based scaffolding. Future work will explore how teachable-agent framing scales across subjects, and investigate multimodal extensions—such as voice-based interaction—that may better support young learners who struggle with text input.

Chase, C. C., Chin, D. B., Oppezzo, M. A., & Schwartz, D. L. (2009). Teachable agents and the protégé effect: Increasing the effort towards learning. Journal of Science Education and Technology, 18(4), 334–352. https://doi.org/10.1007/s10956-009-9180-4 Chi, M. T. H., De Leeuw, N., Chiu, M. H., & LaVancher, C. (1994). Eliciting self-explanations improves understanding. Cognitive Science, 18(3), 439–477. https://doi.org/10.1207/s15516709cog1803_3 Flavell, J. H. (1979). Metacognition and cognitive monitoring: A new area of cognitive–developmental inquiry. American Psychologist, 34(10), 906–911. https://doi.org/10.1037/0003-066X.34.10.906 Gerlich, M. (2025). AI tools in society: Impacts on cognitive offloading and the future of critical thinking. Societies, 15(1), 6. https://doi.org/10.3390/soc15010006 Jin, H., Lee, S., Shin, H., & Kim, J. (2024). Teach AI how to code: Using large language models as teachable agents for programming education. In Proceedings of the 2024 CHI Conference on Human Factors in Computing Systems (pp. 1–28). https://doi.org/10.1145/3613904.3642349 K ucharavy, A., Vallez, C., & David, D. P. (2025). LLMs protégés: Tutoring LLMs with knowledge gaps improves student learning outcomes. In Proceedings of the 20th Workshop on Innovative Use of NLP for Building Educational Applications (pp. 248–257). https://doi.org/10.18653/v1/2025.bea-1.19 Leelawong, K., & Biswas, G. (2008). Designing learning by teaching agents: The Betty's Brain system. International Journal of Artificial Intelligence in Education, 18(3), 181–208. https://doi.org/10.3233/IRG-2008-18(3)02 Renkl, A. (1997). Learning from worked-out examples: A study on individual differences. Cognitive Science, 21(1), 1–29. https://doi.org/10.1207/s15516709cog2101_1 Risko, E. F., & Gilbert, S. J. (2016). Cognitive offloading. Trends in Cognitive Sciences, 20(9), 676–688. https://doi.org/10.1016/j.tics.2016.07.002 Rogers, K., Davis, M., Maharana, M., Etheredge, P., & Chernova, S. (2025). Playing dumb to get smart: Creating and evaluating an LLM-based teachable agent within university computer science classes. In Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems (pp. 1–22). https://doi.org/10.1145/3706598.3713644

