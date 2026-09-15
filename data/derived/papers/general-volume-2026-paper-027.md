# CoDialogue Space: Design of AI-supported Collaborative Learning Platform

**Conference:** ISLS 2026

## Abstract & Introduction

### Abstract
This paper introduces CoDialogue Space, a generative AI–supported collaborative learning platform that provides real-time facilitation during group dialogue. While computer-supported collaborative learning holds promise, it often depends on ad hoc analysis, scripted prompts, and static scaffolds. CoDialogue Space addresses these limitations through discursive facilitation strategies, multiuser–AI interaction, adaptive facilitation levels, and instructor-configurable prompts without requiring coding. We present its design features, offering a scalable, theoretically grounded environment for advancing AI-mediated collaborative learning.

CoDialogue Space: Design of AI-supported Collaborative Learning Platform Eunhye Flavin, Kunal Mohindra, Jeonghyun (Jonna) Lee, eflavin@gatech.edu, kmohindra3@gatech.edu, jonnalee@gatech.edu Georgia Institute of Technology Abstract: This paper introduces CoDialogue Space, a generative AI–supported collaborative learning platform that provides real-time facilitation during group dialogue. While computersupported collaborative learning holds promise, it often depends on ad hoc analysis, scripted prompts, and static scaffolds. CoDialogue Space addresses these limitations through discursive facilitation strategies, multiuser–AI interaction, adaptive facilitation levels, and instructorconfigurable prompts without requiring coding. We present its design features, offering a scalable, theoretically grounded environment for advancing AI-mediated collaborative learning. Learning is social. Computer-supported collaborative learning uses a variety of technological and pedagogical strategies to foster the social nature of learning such as technology-mediated discussion, project-based learning, and online collaborative writing—to support the co-construction of knowledge (Stahl et al., 2006; Ouyang & Zhang, 2024). However, computer-supported collaborative learning may break down when students lack the interpersonal connection and receive limited feedback, which causes greater distraction and a shift toward individual knowledge construction (Cress et al., 2019; Dina & Ciornei, 2013; Strijibos, 2010). Recent advancements in artificial intelligence (AI), including conversational capabilities and neural networks, may help overcome long-standing limitations of traditional computer-supported collaborative learning (Tan et al., 2022). AI-integrated tools now offer immediate feedback, personalized guidance, adaptive support, and advanced data analytics (Cress & Kimmerle, 2023). Despite the growing trend of integrating AI into collaborative learning, existing research reveals several limitations. Most studies focus on presenting statistical data for ad-hoc analysis, which lacks instructional interventions (e.g., alerts, suggestions, or facilitation) that support learning in the moment (Ouyang & Zhang, 2024). More research is needed to use AI effectively for realtime instruction and richer learning experiences in computer-supported collaborative learning. Our project addresses this gap by introducing a generative AI–supported collaborative learning platform, CoDialogue Space, in which an AI agent provides real-time facilitation as students engage in goal-oriented tasks assigned by the instructor. Unlike widely used one-to-one AI–user models, our design enables multiuser–AI conversations, supporting collaborative group work. Because instructors vary in their programming expertise, the platform requires no coding and allows instructors to adjust the level of AI facilitation as needed. This study extends prior research by articulating design principles for generative AI–supported collaborative learning, specifying the features of the AI agent, and examining the learning mechanisms through which the system supports students’ progress on goal-oriented tasks. Given the limited literature on the mechanisms and design principles of AI-agent–mediated collaborative learning (Ouyang & Zhang, 2024), this work contributes both a concrete instructional design and empirical insights into how, and under what conditions, such systems enhance learning sciences research.

## Conceptual framework: AI-assisted collaborative learning

Our conceptual framework builds on two school of thoughts: 1) Computer-supported collaborative learning, which emphasizes mediated interaction and collaborative knowledge construction (Stahl et al., 2006; Stahl, 2015) and 2) facilitation guides for social learning that highlight discursive strategies such as questioning, revoicing, pressing for reasoning, uptake, and balancing participation (Alexander, 2008; Hmelo-Silver & Brown, 2008; O’Connor & Michaels, 1996). We define AI-assisted collaborative learning as collaborative learning in which multiple users, including students and instructors, interact with an AI facilitator that supports shared inquiry in real time.

AI-assisted collaborative learning extends traditional computer-supported collaborative learning by moving beyond scripted prompts and static representational scaffolds (Kollar et al., 2018; Vogel et al., 2017) toward adaptive, moment-to-moment facilitation (Liu et al., 2024). Recent work on conversational agents and large language models (LLM) demonstrates that AI can monitor participation, detect discourse breakdowns, and trigger targeted facilitation moves such as elaboration prompts, clarification checks, consensus-building cues, and s ocio-emotional support (Do et al., 2023; Kim et al., 2021). Yet, existing AI tools rarely operationalize established facilitation moves; most provide generic prompts or participation nudges rather than targeted strategies that shape collaborative reasoning. Many tools rely on fixed rules or predefined cues primarily in highly structured debate or small-scale settings, rather than supporting nuanced interactions that drive deeper peer dialogue. (Do et al., 2023; Sahab et al., 2024). Our system, CoDialogue Space, addresses this gap by integrating real-time discursive facilitation strategies within AI’s adaptivity.

Design features of CoDialogue Space This section introduces four distinct but inter-related design features of CoDialogue Space for meaningful collaborative learning and instructions.

Design feature 1: Timely, meaningful facilitation by AI for collaborative learning CoDialogue Space was developed with the belief that dialogue—understood as a structured exchange of ideas in which participants collaboratively explore perspectives to build shared understanding—is a powerful means for learning. CoDialogue uses GPT-3.5 Turbo as the foundational model for the facilitator in our collaborative learning.

Our LLM-powered agent functions as a facilitator rather than an answer-giver. Drawing on established dialogue-facilitation strategies, the agent follows system-level prompt created by the development team. The strategies involve: clarifying ambiguities, connecting earlier ideas, resolving emerging disagreements, encouraging synthesis across contributions, and redirecting off-task drift. Additionally, the system includes participation-support features. For example, if participants remain inactive for a defined period (e.g., two minutes), the agent can send a private, encouraging prompt to re-engage them in the discussion. As discursive moves are critical for productive collaborative meaning making and knowledge coconstruction (Ouyang & Zhang, 2024), CoDialogue Space provides a not only pedagogically grounded but also scalable model for AI-assisted CL.

Design feature 2: Human-centered AI interface that requires no instructor coding CoDialogue Space provides an interface for instructors to create personas for AI facilitators. This input will be converted into system prompts once the individual parts are filled out or selected. This design feature enables users to explore various perspectives in dialogue and are contributing towards the learning goals. A sample template for defining the persona of the AI facilitator is shown below (See Figure. 1) Figure 1 Template for Defining the Persona of the AI Facilitator Description of each function in Figure 1

## • Context/scenario: Overall goal of the discussion

• Desired learning outcome: Primary learning goals that

## students should achieve in the discussion

• Assessment rubric: Criteria that students will be

assessed on based on the quality of their responses in

## the discussion

• Level of AI interaction: Selection to choose whether or

## not AI should be a facilitator during the discussion. If

Active AI Interaction is selected for the Level of AI Interaction, an additional field (i.e., number of messages) needs to be filled out below. Number of messages indicates how often the AI facilitator should

## respond in the discussion based on the number of

student messages that have been sent.

## focus on– this will help the AI guide the discussion to

focus on these topics The context/scenario, desired learning outcome, assessment rubric, and key concepts are appended to the existing prompt used for the AI facilitator.

D esign feature 3: Multi-user dialogues with an adjustable level of facilitation Table 1 presents two modes of AI-agent facilitation. The first illustrates “little to no interaction” between the AI agent and students, while the second illustrates active AI facilitation. Descriptions for each mode are provided in the table.

Table 1 An Example of the Level of AI Interaction Provided by CoDialogue Space Level of AI Interaction A screen capture of each level Little to no interaction: Figure on the right shows how an AI agent merely facilitates limits to identifying students who have not contributed to

## the discussion in the past two

minutes. The AI agent sends messages to those students to encourage them to participate.

Active interaction: This example shows an AI agent’s active facilitation of

## student discussion. The AI

agent detects 4 messages sent by other students. Then, the agent responds by considering the current goals of the approach guides students to critically analyze the topics and explore other perspectives.

Design feature 4: Seamless student workflow that spans learning and evaluation Students access the CoDialogue Space through a shareable web link provided by the instructor and log in using Single Sign-On or a social identity provider such as Google. Before the dialogue begins, they receive brief onboarding instructions (e.g., “You may type your ideas” and “Take turns when responding”). Once the dialogue starts, the LLM-powered AI agent initiates the conversation using instructor-specified prompts aligned with the goal-oriented task. The dialogue is designed to be interactive; depending on the level of facilitation set by the instructor (as shown in Table 1). At the conclusion of the activity, when students demonstrate sufficient understanding of the target concepts (as determined by rubric settings provided by the instructor), the AI agent delivers a closing message and suggests next steps for continued learning. It can also direct students to subsequent pages—such as a user experience survey—if enabled by the instructor. Architecture and security of CoDialogue Space Our team developed CoDialogue Space using Next.js (Vercel, 2024). MongoDB (MongoDB, 2024) is used as the database to store messages, student names, and other information from chat logs. We use Vercel to host the website for the AI Collaborative Discussion Platform and the frontend page for the discussion interface as well. For the backend, we use Railway and provide resources to enable students to join and leave discussions and the AI to facilitate the discussions (Railway, 2024) We have also created a dashboard for teachers to see student learning engagement data. The platform supports multi-layered analytics combining discourse analysis, temporal learning analytics, network analysis, and process mining. Researchers can trace how meaning-making unfolds over time, analyze shifts in cognitive presence, and identify markers of productive or unproductive collaboration. T he number of users that the platform can support depends on the amount of resources provided by the various pricing plans on Railway and Vercel.

Plan for the presentation The annual International Society of Learning Sciences (ISLS) conference hosts the Interactive Tools and Demos session. We plan to provide a 20–30 minute presentation designed to introduce our new interactive learning platform for teaching and learning (i.e., CoDialogue Space), showcase activity designs, and connect these tools to ongoing research and practice.

During the session, we will set up a laptop to demonstrate the CoDialogue Space and provide a QR code so participants can explore the platform on their own devices. We structured the session to integrate a livedemonstration with discussion of the related research project. Our goal is not simply to highlight the technological features but to illustrate how participants have used the platform, how it is contextually grounded, and how it enhances learning experiences—aligning closely with the conference theme. Proposed Session Structure is

• 0–5 minutes: Overview of the project and introduction of the team

• 5–10 minutes: Interactive demonstration of the tool

## • 10–15 minutes: Presentation of preliminary results from the pilot study

• 15–20 minutes: Discussion of planned tool improvements and future studies, including opportunities for

audience collaboration

• 20–30 minutes: Question-and-answer session

## Implications and conclusions

In this paper, we showcased CoDialogue Space, an AI-supported collaborative learning platform. Our design features demonstrate that the platform is contextually grounded, adaptable to various learning environments. We also presented the system architecture, offering a replicable model for researchers and technologists interested in creating or implementing similar tools. This project has implications for theory, methodology, and practice across the learning sciences and learning technologies.

The first implication lies in its theoretical grounding. Our platform is built on a clear AI-supported collaborative learning framework and enables the study of AI-mediated facilitation in authentic group settings. By implementing varied discursive moves, it allows researchers to examine when, how, and for whom specific facilitation strategies are effective. This supports investigations into mechanisms of productive talk—such as uptake, co-elaboration (Damşa & Ludvigsen, 2016), and epistemic agency (Scardamalia, 2002). The platform also permits controlled manipulation of AI behaviors (e.g., facilitation level, timing, frequency of interventions), creating conditions for causal inference in AI-assisted collaborative learning research. The system’s multi-user structure enables investigation of group-level constructs, such as collective regulation, shared metacognition, and distributed reasoning, which are difficult to capture in one-to-one AI systems (Law et al., 2021). Second, our study generates a practical tool, readily usable in various learning environments because instructors can set learning topics modulate AI’s intervention while students can seamlessly engage in instructor-generated discussion chats. This platform design also creates a replicable research infrastructure: an open, instructor-configurable environment that can be deployed across varied disciplines, task types, and learner populations. This flexibility supports cross-context comparisons and the accumulation of generalizable evidence about AI-assisted CL.

Third, CoDialogue Space offers significant methodological contributions to research in the learning sciences and learning analytics. Our dashboard enables fine-grained, real-time analysis of collaborative learning processes. Unlike traditional CSCL and discourse analytics approaches that rely heavily on post-hoc coding of transcripts, our platform captures time-stamped interaction data, including conversational turns, AI interventions, participation patterns, and discourse trajectories. This allows researchers to study dynamic mechanisms such as breakdown repair, idea integration, and conceptual drift. Alexander, R. J. (2008). Towards Dialogic Teaching: rethinking classroom talk (4th Edition). Dialogos. Cress, U., & Kimmerle, J. (2023). Co-constructing knowledge with generative AI tools: Reflections from a CSCL perspective. International Journal of Computer-Supported Collaborative Learning, 18(4), 607–

614. https://doi.org/10.1007/s11412-023-09409-w

## References & Back Matter

C ress, U., Rosé, C. P., Law, N., & Ludvigsen, S. (2019). Investigating the complexity of computer-supported collaborative learning in action. International Journal of Computer-Supported Collaborative Learning, 14(2), 137-142. https://doi.org/10.1007/s11412-019-09305-2 Damşa, C. I., & Ludvigsen, S. (2016). Learning through interaction and co-construction of knowledge objects in teacher education. Learning, culture and social interaction, 11, 1-18. Dina, A. T., & Ciornei, S. I. (2013). The advantages and disadvantages of computer assisted language learning and teaching for foreign languages. Procedia-Social and Behavioral Sciences, 76, 248-252. Do, H. J., Kong, H. K., Tetali, P., Lee, J., & Bailey, B. P. (2023). To Err is AI: imperfect interventions and repair in a conversational agent facilitating group chat discussions. Proceedings of the ACM on HumanComputer Interaction, 7(CSCW1), 1-23. https://doi.org/10.1145/3579532 Hmelo-Silver, C. E., & Barrows, H. S. (2008). Facilitating collaborative knowledge building. Cognition and instruction, 26(1), 48-94. https://doi.org/10.1080/07370000701798495 Kim, S., Eun, J., Seering, J., & Lee, J. (2021). Moderator chatbot for deliberative discussion: Effects of discussion structure and discussant facilitation. Proceedings of the ACM on Human-Computer Interaction, 5(CSCW1), 1-26. https://doi.org/10.1145/3449161 Kollar, I., Wecker, C., & Fischer, F. (2018). Scaffolding and scripting (computer-supported) collaborative learning. In F. Fischer, C. E. Hmelo-Silver, S. R. Goldman, & P. Reimann (Eds.), International handbook of the learning sciences (pp. 295–304). Routledge.

Liu, C. C., Chiu, C. W., Chang, C. H., & Lo, F. Y. (2024). Analysis of a chatbot as a dialogic reading facilitator: Its influence on learning interest and learner interactions. Educational technology research and development, 72(4), 2103-2131. https://doi.org/10.1007/s11423-024-10370-0 Law, N., Zhang, J., & Peppler, K. (2021). Sustainability and scalability of CSCL innovations. In International handbook of computer-supported collaborative learning (pp. 121-141). Cham: Springer International Publishing. https://doi.org/10.1007/978-3-030-65291-3_7 MongoDB. (2024). MongoDB. MongoDB. https://www.mongodb.com/ O’Connor, M. C., & Michaels, S. (1996). Shifting participant frameworks: orchestrating thinking practices in group discussion. In D. Hicks (Ed.), Discourse, Learning, and Schooling (pp. 63–103). chapter, Cambridge: Cambridge University Press.

Ouyang, F., & Zhang, L. (2024). AI-driven learning analytics applications and tools in computer-supported collaborative learning: A systematic review. Educational Research Review, 44, 100616. Railway. (2024). Railway. https://railway.com/ Sahab, S., Haqbeen, J., & Ito, T. (2024). Conversational ai as a facilitator improves participant engagement and problem-solving in online discussion: Sharing evidence from five cities in Afghanistan. IEICE TRANSACTIONS on Information and Systems, 107(4), 434-442. Scardamalia, M. (2002). Collective cognitive responsibility for the advancement of knowledge. Liberal Education in a Knowledge Society, 97, 67-98.

Stahl, G. (2015). A decade of CSCL. International Journal of Computer-Supported Collaborative Learning, 10(4), 337-344. https://doi.org/10.1007/s11412-015-9222-2 Stahl, G., Koschmann, T., & Suthers, D. (2006). Computer-supported collaborative learning: An historical perspective. In R. K. Sawyer (Ed.), Cambridge handbook of the learning sciences (pp. 409–426). Cambridge University Press.

Strijbos, J. W. (2010). Assessment of (computer-supported) collaborative learning. IEEE transactions on learning technologies, 4(1), 59-73.

Tan, S. C., Lee, A. V. Y., & Lee, M. (2022). A systematic review of artificial intelligence techniques for collaborative learning over the past two decades. Computers and Education: Artificial Intelligence, 3,

100097. https://www.sciencedirect.com/science/article/pii/S2666920X22000522

Vercel. 2024. Next.js: The React Framework for Production. https://nextjs.org Version 13.4. Vogel, F., Wecker, C., Kollar, I. et al. Socio-Cognitive Scaffolding with Computer-Supported Collaboration Scripts: a Meta-Analysis. Educ Psychol Rev 29, 477–511 (2017). https://doi.org/10.1007/s10648-0169361-7

## Acknowledgments

This work was supported in part by the Georgia Institute of Technology’s 2025 Provost Teaching and Learning Initiatives Grant (Project titled: Building an AI-Assisted Online Course for the College of Lifetime Learning). The views expressed herein are those of the authors and do not necessarily reflect the views of the Georgia Institute of Technology. Contact the first author, Eunhye Flavin (also the PI of the funded project) if you have further questions.

