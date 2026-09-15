# An Adaptive, Agile Learner-Centered Computer Science Curriculum Design Approach Based on Deep Knowledge Tracing

**Conference:** ISLS 2022

## Abstract & Introduction

### Abstract
While the focus of the curriculum is on the students, their voices are rarely heard in the creation or adaptation of the curriculum. It is often impractical and difficult to try to address the needs of each student in a single curriculum. With the use of Deep Knowledge Tracing (DKT), we propose a learner-centric curriculum design that is adaptive and agile, performing interventions on an individualized basis.

An Adaptive, Agile Learner-Centered Computer Scienc e Curriculum Design Approach Based on Deep Knowledge Tracing Ruiwei Xiao, Washington University in St. Louis, ruiwei@wustl.edu Chris Chi, Harvard University, cchi@gse.harvard.edu Abstract: While the focus of the curriculum is on the students, their voices are rarely heard in the creation or adaptation of the curriculum. It is often impractical and difficult to try to address the needs of each student in a single curriculum. W ith the use of Deep Knowledge Tracing (DKT), we propose a learner-centric curriculum desi gn that is adaptive and agile, performing interventions on an individualized basis.

## Introduction

A curriculum should enable learners, teachers, and managers to know and fulfill their obligations in r elation to the programme or course (Grant, 2019). Yet, as the central focus of the curriculum, student voices appear to have little impact on its design or adaptation (Jagersma, 2010). Though students may submit suggestions through course evaluation questionnaires, it is unlikely that such adjustments will be made in time and on a personal ized basis. This paper proposes an adaptive and agile approach to learner-centered curriculum design. Following th e assessment of specific learning objectives, the curriculum is then adapted according to the student's learning model, which is determined by pre-instructional and post-instructional tests. We implemented our technique using Deep Knowledge Tracing (DKT) on an online course study p latform for several undergraduate courses in Comput er Science (CS). Our design approach will incorporate students into the curriculum design process, develop a study plan tailored to the needs of the individual studen t, and provide educators and administrators with an  increased understanding of the design and instructional methods of the courses.

## Theoretical background

Student Voice The importance of student voice has been demonstrated both by the role of students in learning processes as well as the positive correlation between student voice a nd better academic performance (Jagersma, 2010). Th e Curriculum-ideas-Analytics (CiA) program, for examp le, uses Knowledge Forum and text mining tools to navigate and incorporate student voice into curriculum design (Teo et al., 2021). However, despite the success of existing approaches in identifying issues from stud ents' voices, few of them suggested practical approaches to improve current curricula. Additionally, students' suggestions are sometimes difficult to articulate precisely. Adaptive Learning and ACT Theory Adaptive learning, or intelligent tutoring, uses co mputer algorithms and artificial intelligence to or chestrate the interaction with the learner and deliver customized resources and learning activities to address the unique needs of each learner (Kaplan, 2021). The theoretical bas is of adaptive learning is ACT theory, which holds that cognitive skill acquisition involves the formulatio n of thousands of rules-relating task goals and tas k states to actions and consequences (Anderson, et al., 1995). ACT-based intelligent tutoring applications such as Cognitive Tutors for Mathematics have been prevalent in thousands of US schools (Ritter, et al., 2018). Deep Knowledge Tracing (DKT) Knowledge Tracing (KT) is a strategic approach in w hich machines are employed to model the knowledge o f a student as they interact with their coursework. As one of the most prominent KT approaches, Deep Knowl edge Tracing (DKT) makes use of Deep Neural Networks to simulate a student's learning behavior and achieves significant improvements in prediction performance over traditional KT models, such as Bayesian Knowle dge Tracing (BKT) (Piech et al., 2015). DKT offers greater modeling capability for complex cognitive processes, and it identifies one instance for all skills, whereas BKT identifies an instance for each (Montero et al., 2018).

## Methodology

To illustrate the iteration of our methodology, we include three activities: pre-instructional quiz, i nstructional activity and post-instructional quiz in each module  of the curriculum for a CS course Introduction to C Programming. During each iteration of curriculum design for a module, we follow four steps (Figure 1): ICLS2022 Proceedings 2036 © ISLS

1. Identify learning goals and break them down into skill labels. Labels are the meta inputs of DKT models. As

the different learning goals are composed of one or  more skills, we disaggregate each learning goal in to skill labels, which act as a common unit of measurement and analysis.

2. Assess students via a standard labeled pre-instr uctional quiz.  Questions in the pre-instructional quiz

encompass all the skills that students will learn in this module, and DKT calculates a baseline model by using the student's mastery of each skill to recommend personalized instruction for the student.

3. Adjust the instructional activity using the data  of pre-instruction activities. The instructional activity is

categorized by skill and includes lectures, practice questions, and readings. A student who is weak in a particular skill will be assigned more instructional activities according to the DKT model.

4. Assess students via a standard labeled post-inst ructional quiz. There are different questions in the post-instructional quiz, but the difficulty and skill levels are the same as those in the pre-instructional quiz. Following submission of the quiz, DKT will update the student's learning model. Students are now presented with the option of completing this model's study and receiving thei r module score or engaging in the instructional act ivities suggested by the updated learning model and retaking the quiz. A participant is not restricted to taking this quiz a specific number of times, however, when they begin a new attempt, questions will be refreshed. Figure 1 The Four-Step Iteration for Each Module Ongoing and future works Currently, we are creating skill labels and labelin g existing activities and questions. In spring 2022, 200 undergraduate students who register for the class will use the system without DKT modeling and recommendation. Data collected from the study will serve as training data for the DKT algorithm in addition to the control group. We hope to undertake a curriculum design experiment with DKT in the fall semester of 2022.

## References

Anderson, J. R., Corbett, A. T., Koedinger, K. R., & Pelletier, R. (1995). Cognitive tutors: Lessons learned. The journal of the learning sciences, 4(2), 167-207.

Grant, J. (2019). 5. In Understanding Medical Education: Evidence, theory, and Practice (pp. 71–88). essay, John Wiley & Sons, Inc.

Jagersma, J. (2010, December 22). Empowering studen ts as active participants in curriculum design and implementation. Institute of Education Sciences. Retrieved November 19, 2021, from https://eric.ed.gov/?id=ED514196.

Kaplan, A. (2021). Higher education at the crossroads of disruption: the university of the 21st century. Emerald Group Publishing.

Montero, S., Arora, A., Kelly, S., Milne, B., & Moz er, M. (2018). Does Deep Knowledge Tracing Model Interactions among Skills?. International Educational Data Mining Society. Piech, C., Bassen, J., Huang, J., Ganguli, S., Sahami, M., Guibas, L., & Sohl-Dickstein, J. (2015). Deep knowledge tracing. In Proceedings of the 28th International Conference on Neural Information Processing Systems-Volume 1 (NIPS'15). MIT Press, Cambridge, MA, USA, 505–513.

Ritter, F. E., Tehranchi, F., & Oury, J. D. (2019). ACT‐R: A cognitive architecture for modeling cognition. Wiley Interdisciplinary Reviews: Cognitive Science, 10(3), e1488. Teo, C. L., Ong, A., & Lee, A. V. (2021). Exploring  the Role of Curriculum in Learning Analytics to Su pport Knowledge Building Practice. In Hmelo-Silver, C. E., De Wever, B., & Oshima, J. (Eds.), Proceedings of the 14th International Conference on Computer-Supported Collaborative Learning-CSCL 2021 (pp. 297-298). Bochum, Germany: International Society of the Learning Sciences. Wiles, J., & Bondi, J. (2007). Curriculum development: A guide to practice. Pearson Merrill Prentice Hall. ICLS2022 Proceedings 2037 © ISLS

