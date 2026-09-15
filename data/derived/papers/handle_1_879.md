# Using Multiple Embodied Representations to Support Learners in Making Connections Across Modeling Activities

**Conference:** ICLS 2018

## Abstract & Introduction

### Abstract
Existing methods for automating curriculum design have had limited impact over

Computation, Constructivism, and Curriculum Design Shayandoroudi, Carnegie Mellon University, shayand@cs.cmu.edu Abstract: Existing methods for automating curriculum design have had limited impact over the past fifty years. I propose two ways to potentially get around this limitation: developing adaptive content selection policies that are robust  to different conceptions of student learning and taking an orthogonal approach to automated curriculum design that use s learner-generated solutions to help students learn.

Vision From the mechanical teaching machines of the early twentieth century to intelligent tutoring systems a nd the wave of massive open online courses (MOOCs) in recent years, many have been motivated by the dream of personalized, adapt ive instruction for all students. To achieve this dream, learni ng scientists and educational technology researchers have largely focused on rule-based systems that rely on extensive domain and psychology expertise. To do adaptive content selection, these sys tems use simple forms of rule-based AI (possibly combined with constrained machine learnin g algorithms). While this approach has led to the development of successful intelligent tutoring systems with high quali ty content, (1) such systems use a very limited form of adaptive content selection, and (2) developing such syste ms can be very costly. In contrast, some researchers are now starting to apply black box machine learnin g algorithms to do adaptive content selection. However, in my dissertation I will s how through a comprehensive literature review that these approaches have had relatively limited impact.

Instead, I hope to demonstrate that combining insights from both approa ches can help in automating curriculum design. In particular, I focus on three as pects of automated curriculum design: content creation, content curation, and adaptive content selection. I propose a numbe r of methods for impactful, cost-effective automated curriculum design that combine machine learning, human computa tion, and principles from the learning sciences.

First, I will describe how reasoning about model mi smatch (i.e., the fact that our statistical models of student learning do not accurately describe student learning) can help point out limitations in existing approaches [Doroudi and Brunskill, 2017] and help in creating more robust adaptive cont ent selection policies [Doroudi et al., 2017].

Second, I will show experiments that demonstrate how we can leverage the work that students naturally do to create new content in a cost-effective way [Doroudi et al., 2016]. In doing so, I will take  motivation from the constructivist philosophy of education, whereby I view learner-generated solutions as being a projection of students’ constructions on the written plane, which can then be us ed to inform other students as they construct their own understandings.

Third, I propose to demonstrate how using machine learning  (in parti cular, multi-armed bandits) can help curate the best content among a pool of learner-generated solutions that continues to grow over time. Finally, I propose to show how we can use learning science principl es to constrain the search for good content selection policies. In particular, I hope t o show that constraining adaptive content selection  algorithms with insights from the expertise reversal effect can help improve upon strictl y black box approaches to adaptive content selection that disregard what we know about student learning.

## References

Shayandoroudi and Emma Brunskill. The misidentified  identifiability problem  of Bayesian Knowledge Tracing. In Educational Data Mining, pages 143 –149. International Educational Data Mining Society, 2017.

Shayandoroudi, Ece Kamar, Emma Brunskill, and Eric Horvitz.  Toward a learning science for complex crowdsourcing tasks. In Proce edings of the 2016 CHI Conference on Human Factors in Computing Systems, pages 2623–2634. ACM, 2016.

Shayandoroudi, Vincent Aleven, and Emma Brunskill. Robust Evaluation Matrix: Towards a more principled offline exploration of instructional policies. In P roceedings of the Fourth (2017) ACM Conference on Learning@ Scale, pages 3–12. ACM, 2017.

1882

