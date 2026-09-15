# Creaticode: An AI Playground for Every Middle School Student

**Conference:** ISLS 2026

## Abstract & Introduction

### Abstract
Artificial intelligence (AI) increasingly influences how we communicate, create, and solve problems, making early AI education essential. Middle school is an ideal time for students to build AI literacy, yet teachers face barriers such as limited tools, steep learning curves, and lack of classroom-ready materials. CreatiCode addresses these challenges by extending the familiar Scratch platform with AI tools and AI-enhanced coding blocks that introduce generative and predictive AI concepts in an engaging, visual way. Supporting all four dimensions of AI literacy: understanding, using, evaluating, and creating, CreatiCode helps students move from AI consumers to creators. The platform includes free teacher support such as tutorials, lesson plans, and slide decks to simplify classroom integration. This paper introduces the CreatiCode AI toolset, describes partnerships with teachers to refine usability and curriculum alignment, and showcases examples of CreatiCode in action that highlight its potential as an accessible AI playground for every middle school student.

Creaticode: An AI Playground for Every Middle School Student Dana Saito-Stehberger, UC Irvine, dsaitost@uci.edu Bin Yu, CreatiCode.com, info@creaticode.com Abstract: Artificial intelligence (AI) increasingly influences how we communicate, create, and solve problems, making early AI education essential. Middle school is an ideal time for students to build AI literacy, yet teachers face barriers such as limited tools, steep learning curves, and lack of classroom-ready materials. CreatiCode addresses these challenges by extending the familiar Scratch platform with AI tools and AI-enhanced coding blocks that introduce generative and predictive AI concepts in an engaging, visual way. Supporting all four dimensions of AI literacy: understanding, using, evaluating, and creating, CreatiCode helps students move from AI consumers to creators. The platform includes free teacher support such as tutorials, lesson plans, and slide decks to simplify classroom integration. This paper introduces the CreatiCode AI toolset, describes partnerships with teachers to refine usability and curriculum alignment, and showcases examples of CreatiCode in action that highlight its potential as an accessible AI playground for every middle school student. Artificial intelligence (AI) is increasingly impacting all aspects of our daily lives, from how we communicate to how we learn, create, and solve problems. As AI becomes more pervasive, it is essential that all students begin learning about it early, particularly in middle school, when curiosity and computational thinking skills are rapidly developing (Touretzky et al., 2019; Long & Magerko, 2020). Students need to understand what AI is, why it matters, and how it can be used responsibly and creatively. However, teaching AI at the middle school level presents significant challenges. While there are many AI-related tools available (Druga, 2018; Carney et al., 2020; Ali et al., 2021), most are designed for students to passively observe instead of actively create or experiment. Even when effective tools exist, they often demand substantial preparation, technical expertise, and time from teachers, barriers that can make classroom implementation difficult (Chiu & Chai, 2020; Kim & Kwon, 2025). CreatiCode addresses these challenges directly. Built on the familiar Scratch platform, CreatiCode extends block-based programming with custom AI blocks that introduce core AI concepts in an engaging and accessible way. In addition, CreatiCode integrates AI-powered assistants and image generators, enabling students to develop their prompting skills while creating their own AI-driven projects. The platform supports all four dimensions of AI literacy (OECD & European Commission, 2025): understanding, using, evaluating, and creating AI, while maintaining the playful, exploratory spirit of Scratch. To further reduce barriers for teachers, CreatiCode includes comprehensive educator resources such as tutorial videos, ready-to-teach lesson plans, and classroom slide decks. Ongoing partnerships with teachers inform continuous improvements to both the tool and curriculum. It is available to everyone: the free version of CreatiCode provides all the functionality necessary for effective classroom use. CreatiCode is a playground for middle school students to engage with AI.

The CreatiCode AI toolset The CreatiCode platform extends MIT Scratch (Resnick et al., 2009) with a wide variety of free coding and learning tools, enabling students to become both consumers and producers of AI. Students not only learn how to select the right tool for the task, but also gain the insight and creativity to harness their full potential. AI coding assistant The AI assistant “CreatiCode XO” is a ChatGPT-like chatbot in the coding playground. It is designed to accommodate the learning needs of middle students in the following ways.

1) While most mainstream chatbots can only read or write pseudocode for blocks and tend to make

syntactical errors, XO can read students’ block code in the editor directly and can write block code with high accuracy.

2) For students who are new to block-based coding, XO can help them catch up quickly by illustrating the

coding concepts with intuitive example code.

3) XO can chat in the same language as each student, removing a major hurdle for non-English speaking

students.

4) XO offers a “socratic mode” that withholds direct answers, guiding students with questions and hints

instead. Teachers can also enforce it class-wide to ensure students actively work through problems.

5) XO can also work in an “agent mode” - it discusses the design with the student and then edits the code

directly. This prepares students to work with advanced agentic tools like Claude Code in the future.

6) XO maintains a continually updated “learning profile” for each student based on their chat history. It

tracks what concepts and skills they’ve mastered or they’re struggling so XO can personalize future responses.

Figure 1 AI Coding Assistant “CreatiCode XO” AI image library and generator MIT Scratch offers only a few hundred images for sprites and backdrops, significantly limiting personalization. CreatiCode provides millions of moderated, AI-generated images, and students can create new ones with prompts. Figure 2 Generate a New Image and then Generate a Variation of It The image search/generation tool is designed to assist students to engage and create with AI.

1) Students can select an existing image as reference and generate a variation of it. This allows them to improve

an image iteratively with better prompts, or generate multiple images with consistent characters.

2) Students can view the original prompt used to generate each image to learn how to generate similar images.

3) Images generated by any student become part of the public library automatically, so other students can use it

as well. This model is similar to how students create and share code, encouraging creativity and collaboration. Generative AI blocks While students can learn to write effective prompts by using the AI coding assistant and image generator, a higher level of AI fluency can be achieved by building projects powered by AI. ● Students have the opportunity to design programs with integrated AI blocks and are encouraged to consider the strengths and limitations of AI; ● Students are challenged to craft highly resilient prompts capable of handling unpredictable user inputs, as these prompts become fixed and uneditable once the projects are released to the public To that end, the CreatiCode platform offers generative AI blocks, such as the ChatGPT request block: Figure 3 The ChatGPT Block The ChatGPT block sends requests to OpenAI’s ChatGPT service via CreatiCode’s server, which will reject any inappropriate requests. It also retains all previous messages in the chat session, so the student code can be much simpler. This block is central to many projects in the open-source Creaticode curriculum. Some projects include: a chatbot for students to interact with a historical figure, a mystery game where the player interrogates characters to find the thief, and an app that generates quiz problems for any subject and skill level (see Figure 4). Figure 4 AI Projects: <Chat with Einstein>, <Who’s the spy?>, <AI Quiz Writer> Predictive AI blocks The CreatiCode platform provides predictive AI blocks that enable fast and accurate forecasting and decisionmaking. Some features that depend on predictive blocks include text-to-speech and speech-to-text, vision models for hand tracking and body tracking, classification models like K-Nearest-Neighbors, and Tensorflow blocks for training Neural Network models. Students apply the predictive AI blocks in the projects where they develop an app that listens to user speech in one language and speaks it in another, a training game that asks players to make various poses and checks their pose in realtime, and a neural-network model that classifies random 2D dots based on the training data (see Figure 5).

Figure 5 AI Projects: <AI Voice Translator>, <Fitness Game>, <Random dots classifier>

## Partnering with teachers to get better perspectives

When it comes to AI-literacy education, a key design decision in CreatiCode is to always include teachers in the loop. Many of Creaticode’s key features are a result of feedback received from teachers who were teaching with Creaticode in their classrooms.

Monitoring students’ interactions with AI tools Since each student can interact with AI tools individually, a top request from teachers is to have access to transcripts between XO and each individual student. Teachers can also view each image generation question and the image that was generated (see Figure 6.) Figure 6 Teacher View of Student’s Chat with XO and Image Generation Request Teacher control panel An equally important feature for teachers is to enable/disable coding tools based on their teaching goals. For example, they can force students to use the “socratic mode” or disable the AI image generator. Figure 7 Teacher’s Control Panel Integrated AI curriculum A year-long AI curriculum with over 50 well-structured lessons is available for free for teachers to make full use of the AI tools in CreatiCode systematically (reference to curriculum paper). All lessons come with lesson plans, slide decks, assessment questions and student workbooks. The lessons start with using AI tools for coding help and image generation, which are crucial skills that students can practice in later lessons. These later lessons are all project-based activities, where students first build a baseline project following given steps, and then work on a “creative adaptation” of the project to demonstrate the skills/concepts they have learned in a new project. Demo setup This 25-minute interactive demo follows a show-then-try cadence for each key feature. For each segment, the presenter gives a 2-3 minute live walkthrough on the projector, then invites a 3-4 minute hands-on tryout plus brief Q&A before moving on. Participants work in pairs on their own laptops; QR codes provide one-click access to starter projects. Materials and starters are distributed via a single short link. For more information, visit https://www.curriculum.elementarycomputingforall.org/act4 CreatiCode shows how AI can be approachable, creative, and meaningful for middle school students. By extending the familiar Scratch environment with AI-powered assistants, generative and predictive blocks, and a structured curriculum, it bridges the gap between AI use and creation. Built with teachers, CreatiCode stays accessible and educationally sound. Students learn to use, question, and design with AI, developing literacy in understanding, application, and creation. As AI reshapes learning and life, platforms like CreatiCode model equitable, engaging, and hands-on education that empowers young learners to shape an AI-driven future. R eferences Ali, S., DiPaola, D., Lee, I., Sindato, V., Kim, G., Blumofe, R., & Breazeal, C. (2021). Children as creators, thinkers and citizens in an AI-driven future. Computers and Education: Artificial Intelligence, 2, 100040. https://doi.org/10.1016/j.caeai.2021.100040 Carney, M., Webster, B., Alvarado, I., Phillips, K., Howell, N., Griffith, J., … & Chen, A. (2020). Teachable Machine: Approachable web-based tool for exploring machine learning classification. In Extended Abstracts of the 2020 CHI Conference on Human Factors in Computing Systems (pp. 1–8). New York, NY: ACM.

Chiu, T. K. F., & Chai, C. S. (2020). Addressing artificial intelligence in K–12 education: A literature review and recommendations for curriculum design. (In Proceedings of the International Conference on Computers in Education, 2020). [Retrieved from academic database]. Druga, S. (2018). Growing up with AI: Cognimates – from coding to teaching machines (Master’s thesis, Massachusetts Institute of Technology, Media Lab).

Kim, K., & Kwon, K. (2025). From co-design to co-teaching: A comprehensive approach to an integrated AI curriculum in middle school STEM education. Smart Learning Environments, 12, Article 57. https://doi.org/10.1186/s40561-025-00413-1 Long, D., & Magerko, B. (2020). What is AI literacy? Competencies and design considerations. In Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems. New York, NY: ACM. https://doi.org/10.1145/3313831.3376727 OECD & European Commission. (2025). AI Literacy Framework for Primary and Secondary Education. Retrieved November 5, 2025, from https://ailiteracyframework.org/ Resnick, M., Maloney, J., Monroy-Hernández, A., Rusk, N., Eastmond, E., Brennan, K., … & Kafai, Y. (2009). Scratch: Programming for all. Communications of the ACM, 52(11), 60–67. https://doi.org/10.1145/1592761.1592779 Touretzky, D. S., Gardner-McCune, C., Martin, F., & Seehorn, D. (2019). Envisioning AI for K-12: What should every child know about AI? In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 33, pp. 9795–9799). https://doi.org/10.1609/aaai.v33i01.33019795 How AI Can Improve Student Learning Motivation and Engagement While Reducing Faculty and Admin Burden Patrick Hong, University of California, Irvine, pphong@uci.edu Abstract: My Learning Coach (MLC) is an AI-powered software application designed to enhance student engagement by providing real-time, data-driven guidance. MLC addresses persistent student disengagement and the need for durable human skills (critical thinking, resilience, agency) in the age of AI. Grounded in learning science, including Expectancy-ValueCost (EVC) Theory and Bloom’s Taxonomy, MLC detects learning motivation via biweekly "State of Mind" (SOM) check-ins and correlates this affective data with behavioral metrics such as Learning Management System (LMS) data. This demo session showcases the MLC workflow: from a student completing a check-in to receiving personalized guidance, and how faculty utilize the same tool to make in situ pedagogical adjustments. Early randomized controlled trials at UC Irvine demonstrated an increase of 2.1 study hours per week and 11.2% more LMS pageviews among MLC users compared to their peers. MLC directly aligns with the National Academies' recommendations for transforming undergraduate STEM education. The need for an AI-augmented learning intervention The landscape of undergraduate education faces significant challenges, notably student disengagement and high dropout rates—three out of five students may not graduate from college (National Center for Education Statistics, 2023), and 41% of employers agree that recent graduates are ready for entry-level roles (American Association of Colleges and Universities, 2023). In the context of computer-supported collaborative learning (CSCL), impactful learning must be culturally responsive, contextually grounded, and collaboratively shaped, requiring solutions that move beyond traditional content delivery. My Learning Coach (MLC) is proposed as a solution: an AI-powered learning coach software that acts as a co-pilot, augmenting in-person assistance during a student’s educational journey.

MLC is specifically engineered to foster durable skills—a growth mindset through critical thinking, resilience forged by perseverance, and agency grounded in self-determination. It achieves this by identifying each student's unique learning context, including academic and non-academic constraints, motivational misalignment, and behavioral gaps.

This demonstration aligns with the ISLS 2026 theme, "Partnering with Purpose," by showcasing a technological/design contribution that uses data science and learning theories to create a scalable platform for personalized coaching. The demo will illustrate how MLC provides the deep, real-time data necessary for instructors and institutions to partner more effectively with students to achieve equitable and effective learning.

## Theoretical framework for data collection

MLC’s design is grounded in established learning science frameworks to ensure diagnostic precision beyond simple engagement metrics.

The Expectancy-Value-Cost (EVC) Theory (Eccles, 1983; Barron & Hulleman, 2014) is central to MLC’s assessment of student motivation. The biweekly State of Mind (SOM) check-ins utilize 15 Likert-scale questions (-3 strongly disagree to +3 strongly agree, omitting a neutral midpoint) to measure three domains:

1. Expectancy (I can master content): Measures self-efficacy and belief in the ability to grasp subject matter,

aligning with Principle #3 (Social Dimensions).

2. Value (I see value in mastering content): Measures perceived relevance to goals and intrinsic motivation,

linking to career aspirations and collaborative learning value.

3. Cost (What is holding me back?): Explicitly addresses non-academic stressors, excessive demands, and

fairness concerns that act as barriers, aligning with Principle #6 (Flexibility). MLC integrates motivation measurement with Bloom's Taxonomy (Build, Practice, Reflect, Transfer Knowledge) (Bloom, Engelhart, Furst, Hill, & Krathwohl, 1956) to track cognitive learning progression. For instance, Expectancy questions map directly to Bloom’s levels, such as connecting confidence in mastering material to the Build Knowledge (Understand) stage.

Multi-Modal Data Strategy: MLC combines quantitative SOM data with qualitative data from the threequestion Retrospective (RETRO) check-in, in which students provide free-form text feedback on "What went well?", "What didn't go well?" and “What can be improved?” This correlates with behavioral data from the LMS, s uch as pageviews and assignment submissions. This robust approach allows MLC to deliver diagnostic insights— revealing why a student might be struggling (e.g., motivational barrier or cognitive misalignment) rather than just what their grades or clicks are.

MLC demonstration components The demo session will walk through the MLC workflow and the data-rich artifacts it generates, focusing on how the tool supports both the student and the instructor in real time.

1. The Student Workflow: Reflection and Personalized Action. The demo will begin by simulating a student

completing their biweekly SOM check-in. The focus then shifts to the resulting Personalized Student Action Report. This report provides the student with insights into their longitudinal progress.

• Wellness Analysis: The report visualizes shifts in emotional states (e.g., "Content," "Stressed,"

"Confused") over the term. For one sample student, wellness shifted from "Content" to primarily "Stressed" due to growing workload pressure, demonstrating "clear comprehension amid growing workload" (resilience).

• Data-Driven Recommendations: Based on the analyzed motivation and behavior patterns, the student

receives targeted, actionable recommendations. Examples include suggestions to "Schedule short mindfulness breaks" to reduce stress, "Engage in weekly peer study groups" to build accountability (fostering relatedness and agency), or "Review analytics each Friday" (fostering a growth mindset).

2. The Instructor Workflow: In-Situ Adjustments via Faculty Action Reports. The MLC demo will showcase

the Faculty Action Report (e.g., the End-of-Term Report). This report aggregates student data on learning motivation, Bloom’s progression, sentiment, and wellness.

• Holistic Evidence for Evaluation: The report provides "new forms of evidence" beyond traditional

student surveys, supporting a holistic evaluation of teaching. One faculty member noted this data provided "additional evidence for my upcoming professional advancement review".

• Pedagogical Insights: Faculty can identify class-wide trends for in situ adjustments. For instance, analysis

revealed that "Build, Practice, Reflect, and Transfer Knowledge all trended upward," indicating steady student confidence and mastery. Conversely, data might highlight "Stressed" states peaking in Week 4, reflecting early workload pressures, allowing the instructor to incorporate stress management strategies or adjust assignment timing.

3. Future Capabilities: The Agentic AI Chatbot. The demonstration will preview the planned Agentic AI

Chatbot. This chatbot will be trained on anonymized historical class data (including student freeform text feedback) to serve as a specialized Teaching Assistant (TA).

• Proactive Guidance: The AI can answer student questions (e.g., "How much time have A students spent

in this class in the past?") by retrieving relevant historical data.

• Targeted Assistance for Instructors: Instructors can query the AI for class issues (e.g., "What is the most

common issue that the students scoring 50% overall are struggling with?"), receiving real-time insights based on the collected SOM and RETRO data.

## Pilot results and alignment with equity principles

The 2024–2025 MLC pilot at UC Irvine involved 3,195 undergraduates across 26 courses. The data collected support the efficacy of the reflection tool, even before the implementation of automated coaching reports and the AI chatbot.

Proven Impact: In a randomized control trial in the ENGR190W course, MLC users reported an additional 2.1 hours of weekly study time and 11.2% more LMS pageviews than their peers without access. Student feedback confirms MLC's motivational impact: 61% report a 10% increase in class engagement, and 54% note a 12% improvement in keeping up with coursework. Furthermore, 94% of respondents felt comfortable using MLC, and 83% believed it could inform AI-driven or in-person support interventions. Additionally, the MLC aligns with the National Academies' Principles for Equitable and Effective Teaching (National Academies, 2025). The alignment is summarized in Table 1. T able 1 My Learning Coach mapping with Bloom’s Taxonomy and Expectancy-Value-Cost Learning Theory, and alignment with the National Academies’ 7 Principles for Equitable and Effective Teaching MLC National Academies How MLC Meets the Principle Feature/Mechanism Principle

## Measures and motivates engagement (e.g., +11.2% LMS

Bloom's Taxonomy Principle #1: Active pageviews) and tracks cognitive progression (Build to Tracking & LMS Data Engagement Transfer Knowledge), foundational to active learning.

Provides real-time data on non-academic "Cost" barriers, Principle #6: EVC/Cost Questions & allowing faculty and support staff to make "in situ Flexibility & Wellness Checks adjustments" based on students' evolving, individualized Responsiveness needs.

Collects quantitative (EVC, LMS activity) and qualitative Faculty & Student Action Principle #5: Multiple (wellness, freeform text sentiment) data to provide holistic, Reports Forms of Data actionable insights for continuous improvement at all levels. Makes the learning process and overall class state visible, Principle #7: Dashboard Function & revealing "hidden challenges" like time management Intentionality & Proactive Guidance struggles and using anonymized historical data to set Transparency expectations for future cohorts.

Designed using primary research from diverse institutions Training Data/Inclusive Principle #4: Identity (including MSIs) and employs culturally responsive Design & Sense of Belonging frameworks (EVC) to foster agency, resilience, and an identity-safe environment.

MLC is a direct example of the infrastructure called for by Recommendation 11—collecting, monitoring, and providing transparent access to diverse data about student outcomes, experiences, and affective measures for systemic improvement. Furthermore, by grounding its design in EVC, Mindset Theory, and Self-Determination Theory, MLC directly addresses Recommendation 3 by using the Principles from the initial conceptual stage.

## CSCL implications

The My Learning Coach demo illustrates how AI and learning science can be combined to operationalize key principles of equitable and effective teaching. The platform provides faculty with timely, nuanced insights necessary for making data-informed pedagogical decisions, while simultaneously empowering students with selfawareness (metacognition) and the skills (growth mindset, agency) needed for long-term academic adaptability. A crucial area for future development that directly engages the CSCL community is the planned Social Comparison Assessment. This feature measures a student’s emotional and motivational response to peers who perform better or worse (upward/downward comparisons). The resulting data guides highly targeted coaching strategies, such as promoting mastery goals for envious students or fostering empathy for "elitist" students, demonstrating how the system will facilitate personalized, adaptive, and human-skills-focused collaborative support.

MLC demonstrates that technology can serve as a robust, theory-driven partner—a key objective of the CSCL 2026 conference theme—for managing the vast amounts of data required for individualized, equitable, and effective learning at scale.

## References & Back Matter

American Association of Colleges and Universities. (2023). The Career-Ready Graduate. Washington DC: American Association of Colleges and Universities.

Barron, K. E., & Hulleman, C. S. (2014). Expectancy-value-cost model of motivation. International encyclopedia of the social & behavioral sciences, 8, 503–509.

Bloom, B. S., Engelhart, M. D., Furst, E. J., Hill, W. H., & Krathwohl, D. R. (1956). Taxonomy of educational objectives: The classification of educational goals. Handbook I: Cognitive domain. New York: David McKay Company, Inc.

Eccles, J. (1983). Achievement and achievement motives: Psychological and sociological approaches (Vol. W. H. Freeman and Company). (J. T. Spence, Ed.) New York: W. H. Freeman and Company. G arcia, S., Song, H., & Tesser, A. (2010). Tainted recommendations: The social comparison bias. Organizational Behavior and Humandecision Processes, 113, 97-101.

National Academies. (2025). Transforming Undergraduate STEM Education: Supporting Equitable and Effective Teaching. Washington, DC: National Academies Press.

National Center for Education Statistics. (2023). National Center for Education Statistics. Retrieved from National Center for Education Statistics: https://nces.ed.gov/programs/digest/d23/tables/dt23_326.27.asp?current=yes

## Acknowledgments

My Learning Coach is funded by the National Science Foundation (NSF) Small Business Innovation and Research (SBIR) and the University of California, Irvine, Office of Vice Provost Teaching and Learning.

