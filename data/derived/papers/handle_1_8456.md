# Students’ Prior Knowledge of Disease Spread and Prevention

**Conference:** ISLS 2022

## Abstract & Introduction

### Abstract
The COVID-19 pandemic has highlighted a need for students to learn about public health issues, including the transmission of disease and methods for the prevention of epidemics. This study presents data from a project focused on developing an emergent systems microworld to help middle school students learn about these topics. The microworld is designed to help students model and test their ideas about how a disease spreads through a population and how an epidemic can be prevented. The paper presents an analysis of students’ prior knowledge of disease spread and prevention, which they shared during an activity preceding their exploration of the microworld. We present student ideas in categories of disease transmission, recovery from disease, and disease protection strategies. We describe their ideas and suggest how they may be integrated into the design of the microworld.

Students’ Prior Knowledge of Disease Spread and Pre vention Siyu Wu, siyu.wu@aggiemail.usu.edu; Hillary Swanson, hillary.swanson@usu.edu; Utah State University Bruce Sherin, bsherin@northwestern.edu; Uri Wilensky, uri@northwestern.edu; Northwestern University Abstract: The COVID-19 pandemic has highlighted a need for s tudents to learn about public health issues, including the transmission of disease and methods for the prevention of epidemics. This study presents data from a project focused on developing an emergent systems microworld to help middle school students learn about these to pics. The microworld is designed to help students model and test their ideas about how a disease spreads through a population and how an epidemic can be prevented. The paper presents an analysis of students’ prior knowledge of disease spread and prevention, which they shared during an activity preceding their exploration of the microworld. We present student ideas in cate gories of disease transmission, recovery from disease, and disease protection strategies. We describe their ideas and suggest how they may be integrated into the design of the microworld.

The COVID-19 pandemic has highlighted the need for a health-literate society. This means enhancing the public’s knowledge of public health issues, including the tr ansmission of disease and methods for the preventio n of epidemics. Epidemiology is a branch of science that studies health-related behaviors and outcomes in populations. This includes subjects such as disease causation and transmission, outbreak investigation, and disease surveillance. At present, learning about epidemiology is primaril y limited to graduate and undergraduate students. B y comparison, few middle school students have access to courses in epidemiology (D’Agostino, 2018). Some scholars have found that developing material on epidemiology for middle school students is challenging (Hlaing, 2014). However, learning about epidemiological topi cs at a young age is essential for helping students  make informed decisions regarding their health and havin g critical thinking regarding public health policy (Bracken, 2014).

To address this need, we are designing student-cent ered epidemiology education materials for middle school students. We use NetTango (Horn, Baker, & Wi lensky, 2020), a block-based interface to the NetLo go modeling platform (Wilensky, 1999). NetTango blocks allow students to create, test, and debug models of disease spread based on their own ideas. Blocks in NetTango are not general-purpose programming primitives, but rather, are semantic blocks relevant to the modeled phenomenon. The approach engages students in the construction of an agent-based computational model of the spread of disease in the context of an emergent systems microworld (ESM) (Dabholkar, Anton & Wilensky, 2018). Students candevelop ideas about disease spread and prevention at the level of a population by exploring individual agent behavior and multi-agent interactions. Emergent systems microworlds and the value of their  application have been investigated by many research studies, including studies that specifically examine the impact on students’ understanding of  scientific phenomena (Levy and Wilensky, 2009; Wilensky & Reis man, 2006; Wilkerson-Jerde, Gravel, & Macrander, 2015). We are investigating how to integrate students’ prior knowledge into the design of the ESM, so that students can construct, test, and revise models that represent their thinking. Our aim is to build a computational modeling environment that very consciously meets students halfway. This means giving students programming blocks that allow them to work with ideas that closely match their intuitions, which in turn requires research into what these intuitions are. The present work investigates stude nt intuitions about the spread of disease and based  on these findings, makes recommendations for refinements to the primitive coding blocks in the microworld, so t hat students can model, test, and debug their thinking.

Theoretical Foundations This research draws on a constructivist view of kno wledge and learning called Knowledge in Pieces (KiP; diSessa,1993). KiP argues that knowledge is a complex system composed of knowledge elements. KiP instruction advocates that learning starts with eliciting students’ prior knowledge and develops by reorganizing and refining the learner’s knowledge networks. To our constructivist lens, we add the lens of constructionism (Papert, 1980). Constructionism is a theory of pedagogy, which posi ts that learning happens best through the construct ion of publicly shareable artifacts. Constructing a publicly shareable artifact helps students learn because they can gain knowledge and skills by creating, reflecting on, and discussing their artifacts. In the case of our pr oject, the learning-by-modeling approach has students use comp utational models to refine their thinking through t he building, testing, and debugging of models.

ICLS2022 Proceedings 1241 © ISLS

## Methods

In this paper, we ask “What intuitions do students have about disease spread and prevention, and how can those be used to inform our microworld design? ” To address these questions, we employed a lab-bas ed case study approach (Yin, 1998) and conducted one-on-one, 1.5-hour recorded interviews through Zoom with middle school students (ages 12-14). During the interview, studen ts were asked questions about the spread and preven tion of disease and then invited to model and test their ideas in the microworld shown in Figure 1.

Figure 1. Screenshot of the Disease Spread microworld (Martin et al., 2021).

Figure 1 shows the microworld display. The box on the left represents the world, where agents interact with each other. The modeling space on the right of the inter face has blocks including “setup,” “go,” “add healt hy,” “add sick,” “ask healthy people,” “ask sick people,” “move,” “chance,” “if sick, infect,” “if sick, recover,” and “if sick, die.” These blocks can be used to model the spread of disease by arranging them in the modeling space.  The microworld is agent-based, meaning each agent is as ked to behave, at each tick of the clock, according  to the blocks assigned to them in the “go” procedure. For example, healthy agents might be asked to move rand omly throughout the world and become infected with some probability if they cross paths with an agent who is sick. The interviewer began the session by sharing their screen and presenting the student with a story about the spread of disease. The story was about Jack, who goes to a party and interacts with Mary, who has been sick. Jack gets sick the next day and then, having recove red, goes to play soccer with his friends. One of t he friends gets sick the next day. The interviewer asked open-ended questions and probed for additional information after each explanation offered by the student. After answ ering the questions, the students were invited to m odel and test their ideas in the microworld.

This study focuses on interviews with three middle school students: Alex (13), Max (12), and Sam (14).

The interviews were recorded and transcribed. A microanalysis (diSessa, Sherin, & Levin, 2016) was conducted to produce a list of the students’ initial ideas about the spread and prevention of disease. The audio recording of each student’s interview was reviewed, and times we re noted during which they revealed their thinking.  These episodes were then marked on the transcript, which was then read for evidence of their initial thinking. Our analysis of the data was driven by the aim of refining the set of coding blocks used in the microworld, and our own intuitions about the appropriate grain size for these blocks. We began by paraphrasing the  student explanations, and then looked across students for common ideas. The ideas were organized based on similarities and grouped into the following categories: 1) disease transmission, 2) recovery from disease, and 3) disease protection strategies. These students’ ideas can help us get a sense of what intuitions students have about disease spread and prevention and how we might revise the e mergent systems microworld by adding new blocks and adding parameters to existing blocks.

## Findings

The analysis revealed 11 pre-instructional ideas across the three categories. We propose 6 corresponding revisions to the microworld, which would allow students to model and test these ideas. We present each knowledge category, listing student ideas (with illustrative segments of transcript) and proposed model revisions. Disease transmission Pre-instructional ideas belonging to this category emerged when the students explained why Jack took a  day to develop symptoms after he played with Mary and transmitted the virus to others even though he had no symptoms. Table 1 organizes students’ ideas about disease transmission and implications for the design of our ESM. Table 1. Pre-instructional ideas about disease transmission and design implications. ICLS2022 Proceedings 1242 © ISLS Disease Recovery This category of pre-instructional ideas emerged wh en students explained what disease Jack caught. Tab le 2 organizes students’ ideas about disease recovery and implications for the design of our ESM. Table 2. Pre-instructional ideas about disease recovery and design implications

## Transcript Pre-Instructional Ideas Implications for Block Design

Alex: …When he recovers from the normal flu, he can't affect it to someone else. [...] A flu. You get it once. Because after your body sees the virus, they will get rid of it right away.

A body can gain immunity when it gets used to a disease.

Add an “if recover, gain immunity” block, with an adjustable probability parameter.

Max: Probably COVID. Coronaviruses, however, our body can’t identify them, so it takes a process for our body to notice that we are sick and clear the virus.

It takes time for our body to recover from Coronavirus.

Add the blocks “get flu” and “get COVID-19” to pair with the variable probability “if sick, recover” block.

Disease Protection Strategies This category of pre-instructional ideas emerged when students were asked to explain which kind of pro tection strategies would be effective in protecting themselves from infection when vaccines are still in short supply. Table 3 organizes students’ ideas about disease protection strategies and implications for the design of our ESM. Table 3. Pre-instructional ideas about disease protection strategies and design implications

## Transcript Pre-Instructional Ideas Implications for Block Design

Sam: …You do not show symptoms right away, it takes time for you to start to feel it.

It takes time to get sick and show symptoms.

Add a “set incubation time” block, to cause a delay between being exposed and getting sick.

Max: Mary sneezed or coughed, the species, the sneeze or cough went into the body of Jack and took time to process and get into his body and get infected.

Alex: The virus got on, for example, his hand. And then when he got home, he had to eat and touch the food. That was with his hand. So, he ate the food, so now it is in his stomach.

Agents of disease can transmit through the human mouth and nose when coughing and sneezing.

Agents of disease can stay on objects and transfer through touch.

Add “cough,” “sneeze,” and “touch objects” blocks to the “ask sick people” and “ask healthy people” block sets. The parameters of each block could be varied with respect to probability of infection.

Alex: Maybe even Jack recovered from the virus. He still had something in his body when they were playing.

Max: …it's like since he is lying on the bed for like a week, perhaps the disease stops working, but when Jack started to play, they started working again.

Agents of disease can still be in your body even when you are healthy.

Viruses would “sleep” in a deactivated body and “wake up” when the body is active again.

Add a “show symptoms” block with a variable probability parameter, to allow agents to be sick with or without showing symptoms.

## Transcript Pre-Instructional Ideas Implications for Block Design

ICLS2022 Proceedings 1243 © ISLS

## Discussion

Our larger research project aims to develop emergen t systems microworlds that intentionally meet stude nts halfway. We approach this by providing students wit h programming blocks that correspond to their intui tions, which requires investigating what those intuitions are. This study examined students’ intuitions about  disease spread and prevention. Findings suggest that students have many intuitions about the spread, recovery from, and prevention of disease. Our findings offer insight into what coding blocks a pandemic microworld should have so that students can build, test, and debug models that represent their thinking. We anticipate that adapting blocks to accommodate students’ intuitions will help students  build models that represent their thinking and all ow those without programming experience to use agent-based modeling to learn about complex systems phenomena.

## References

Bracken, MB. (2014). Epidemiology as a liberal art: from graduate school to middle school, an unfulfilled agenda. Annals of Epidemiology. 24(3), 171–173.

Dabholkar, S., Anton, G., & Wilensky, U. (2018) Gen Evo-An emergent systems microworld for model-base d scientific inquiry in the context of genetics and evolution. Proceedings of the International Conference for the Learning Sciences, London, UK. d’Agostino, E.M. (2018). Public Health Education: T eaching Epidemiology in High School Classrooms. American Journal of Public Health, 108, 324-328. diSessa, A. A. (1993). Toward an epistemology of physics. Cognition and instruction,10 (2-3), 105-225. diSessa, A. A., Sherin, B., & Levin, M. (2016). Knowledge analysis: An introduction. In A. A. diSessa, Hlaing W. M. (2014). Regarding "Educating epidemiologists". Annals of epidemiology, 24(7), 558–559. Horn, M.S., Baker, J. & Wilensky, U. (2020). NetTan go Web [Computer Software]. Evanston, IL: Center fo r Connected Learning and Computer-Based Modeling, Northwestern University. Levy, S.T., & Wilensky, U. (2009). Students’ Learni ng with the Connected Chemistry (CC1) Curriculum: Navigating the Complexities of the Particulate World. Journal of Science Educational Technology, 18, 243–254.

Martin, K., Wu, S., Swanson, H. & Wilensky, U. (202 1). Simplified disease model. Center for Connected Learning and Computer-Based Modeling. Northwestern University, Evanston, IL. Papert, S. (1980). Mindstorms: Children, computers, and powerful ideas. Basic Books, Inc. Wilensky, U. (1999). Netlogo. http://ccl.northweste rn.edu/netlogo/. Center for Connected Learning and Computer-Based Modeling. Northwestern University, Evanston, IL. Wilensky, U. & Reisman, K. (2006). Thinking like a wolf, a sheep, or a firefly: Learning biology throu gh constructing and testing computational theories—An embodied modeling approach. Cognition and Instruction, 24(2), 171–209.

Wilkerson-Jerde, M. H., Gravel, B. E., & Macrander,  C. A. (2015). Exploring shifts in middle school le arners’ modeling activity while generating drawings, animat ions, and computational simulations of molecular diffusion. Journal of Science Education and Technology, 24(2–3), 396–415. Yin, R. K. (1998). The abridged version of case study research. Handbook of applied social research methods, 2, 229-259.

## Acknowledgements

This work was supported by the National Science Foundation (1842375). Sam: I'm kind of staying at home and stuff.  [...] I don’t think wearing masks works. The virus would stay on the masks. Your mouth touches the masks, then the virus comes into your body.

Alex: I think every time you go out, wear masks. Some people wear masks and facial to protect their eyes too. Wash hands often. Sanitize your clothes and shoes when back home.

Stay home more of the time.

Wear masks and facial shields.

Wash hands.

Sanitize personal objects and the environment.

Add “wear masks,” “wash hands,” “wear facial masks,” and “sanitize the environment and belongings” blocks to the “ask sick people” and “ask healthy people” sets of blocks. Each block could have different parameters for probability of infection. It would be

## possible to display the results of single

or multiple disease prevention strategies by stacking or using them separately.

ICLS2022 Proceedings 1244 © ISLS

