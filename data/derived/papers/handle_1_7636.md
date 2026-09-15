# Investigating Children’s Problem-Solving Patterns in Digital Game-Based Learning for Computational Thinking Development

**Conference:** ISLS 2021

## Abstract & Introduction

### Abstract
Although digital game-based learning (DGBL) can facilitate children to develop computational thinking (CT), solving problems in gameplay is yet challenging to younger children due to their insufficient cognitive resources and meta-cognitive skills. In this study, using sequential pattern mining, we investigated 79 children’s in-game problem-solving patterns in the game Penguin Go—designed to promote K-5 students’ CT development. In terms of children’s problem-solving, we found three in-game problem-solving patterns (i.e., solution implementation, consecutive implementation, and solution evaluation) on CT development. We also confirmed that children’s problem-solving patterns predicted CT development at near and far transfer on CT. Based on the study findings, we also discuss design implications.

Investigating Children’s Problem-Solving Patterns in Digital GameBased Learning for Computational Thinking Development Zhichun Liu, University of Massachusetts Dartmouth, liulukas91@gmail.com Jewoong Moon, Florida State University, jewoon.moon@gmail.com Abstract: Developing computational thinking (CT) in digital game-based learning through problem solving is challenging to younger children. In this study, we investigated 79 children’s in-game sequential problem-solving patterns in a CT game – Penguin Go. We found three in-game problem-solving patterns (i.e., solution implementation, consecutive implementation, and solution evaluation) and confirmed that children’s problem-solving patterns predicted CT development at near and far transfer on CT. Based on the study findings, we also discuss design implications.

Keywords: Digital game-based learning, computational thinking, problem solving, sequential data analytics

## Introduction

The recent prevalence of modern computing technologies and artificial intelli gence has drawn attention to computing education for the next generation. Hence, increasing interest arises  regarding how to incorporate the notion of computational thinking (CT) into the elementary curriculum wo rldwide (McGill & Decker, 2020) Several DGBL studies aimed at promoting children’s CT development thr ough in-game problem-solving experiences (Zhao & Shute, 2019). Specifically, DGBL benefits students  to understand underlying game logics and rules that drive CT development by in-game failures and success experiences. However, research has indicated that young children are likely to experience co gnitive challenges in gameplay. Such challenges may yield unsystemat ic behaviors during in-game problem solving and learning transfer failure due to their limited uses of cognitive and metacognitive resources (Liu et al., 2017). Understanding children’s in-game problem-solving patterns is essential because it indicates students’ gameplay patter ns representing diverse needs and challenges at different learning stages. In this study, we aim at investigating the relationship between childre n’s in-game problem-solving patterns and CT development through identifying emerging behavioral patterns by sequential pattern mining. Our research questions are:

(1) What are children’s in-game problem-solving patterns in the game Penguin Go?

(2) To what extent do the in-game problem-solving patterns predict children’s CT development?

## Study procedure

Penguin Go (PG) is an educational game teaching block-based programming language designed to enhance young children’s CT development (Zhao & Shute, 2019). Seventy-nine children between 9 to 11 years old from diverse ethnic backgrounds were randomly assigned to either the treatment or the control version of  Pengu in Go. The control group accessed only the basic game mechanism support, while the treatment group  received additional cognitive supports in the form of information prompts and parti al worked-examples during the gameplay. Participants played Penguin Go for 135 minutes.

Gameplay data and sequential pattern mining We collected computer logs from Penguin Go  to identify students’ game interactions. The log data contains students’ game ID, game action, level, code, and timestamp. We conducted  sequential pattern mining (SPM) to indicate students’ emerging in-game problem-solving patterns. We aggregated individu al gameplay data and arranged them based on each students’ game ID and gameplay sequences. We used the cSPADE algorithm (Zaki,

2000) to identify frequent behavior patterns among various in-game sequences in a given time period (max_gap

= 2, min_sup = 0.5).

## Results

RQ1. What are children’s in-game problem-solving patterns in the game A total of 28 gameplay sequences containing five unique behaviors were ident ified. Based on the characteristics of the identified gameplay sequences, we classified the identified seque nces into three pattern categories (Table 1). Second, in comparison to SI and CI patterns, children showed less S E patterns, which denote that children tended to have trouble with systematic problem-solving. Third, the SPM result demonstrated child ren’s rare interactions with embedded learning supports during gameplay. Table 1: In-Game Problem-solving Pattern Categories

## Category Pattern description Implications

Solution implementation (SI) (average support value = 0.81) Start with a series of Create Blocks and end with Run Blocks.

Implements and executes a solution with a clear algorithm in mind. The frequent occurrence of the SI behavior indicates an inefficient problem-solving heuristic (e.g., trial-and-error).

Consecutive implementation (CI) (average support value = 0.80) Only contains consecutive Create Blocks with no Run Blocks.

Does not have a clear plan of the algorithm, which indicates unsystematic exploration or sometimes random block creation.

Solution evaluation (SE) (average support value = 0.64) Contains Reset Blocks in combination with Run Blocks or Reset Blocks.

Interrupts the solution execution. Involves prediction of where the penguin is moving and the evaluation of the solution. Often associate with debugging.

RQ2. Effect of in-game problem-solving patterns on CT development? We then examined how the frequency of the in-game problem-solving patterns across all in-game sequences predicted children’s CT performance at the near and far transfer level. In terms  of the in-game problem-solving patterns, the results indicated that the CI pattern was a statistically sig nificant predictor for the near transfer (t = 2.33, p =.02) but not for the far transfer performance (t = 1.21, p =.23). On the other hand, the frequency o f SE behavior predicted the far transfer performance (t = 1.92, p =.06) with a marginal significance instead of the near transfer performance (t = -.94, p =.35). This result infers that debugging-related behaviors influenced learning transfer in the long  run, although this pattern was not efficient for learning immediately. The frequency of SI pattern was not a significant predictor for neither near transfer performance nor the far transfer performance.

## Discussion and conclusion

The results displayed tha t children experienced inefficient  and unsystematic problem-solving during gameplay. Such results echoed with the literature that students are likely to demonstrate inefficient behaviors due to the high cognitive load in a digital learning environment (Kir schner, Sweller, & Clark, 2006). The key design challenge we confirmed here is that children are difficult to distill abstract knowledg e out of their learning experience with high cognitive load (Mulder, Bollen, de Jeong, & Lazonder, 2016). Therefore, demonstrating knowledge and skill transfer across contexts can be challenging. Therefore, it is essential to pr esent a learning support that reminds children of what certain blocks and their combinations they can experi ment with further. Further regression analysis also highlights the importance of evaluation-and prediction-related actions in gameplay.

## References

Kirschner, P. A., Sweller, J., & Clark, R. E. (2006). Why minimal guidance during instruction does not work: An analysis of the failure of construct ivist, discovery, problem-based, experiential, and inquiry-based teaching. Educational Psychologist, 41(2), 75–86. https://doi.org/10.1207/s15326985ep4102_1 Liu, Z., Zhi, R., Hicks, A., & Barnes, T. (2017). Understanding prob lem solving behavior of 6 –8 graders in a debugging game. Computer Science Education, 27(1), 1-29. McGill, M. M., & Decker, A. (2020). Tools, languages, and environme nts used in primary and secondary computing education. In Proceedings of the 2020 ACM Conference on Innovation and Technology in Computer Science Education (pp. 103-109). Trondheim, Norway. Mulder, Y. G., Bollen, L., de Jong, T., & Lazonder, A. W. (2016). Scaffolding learning by modelling: The effects of partially worked‐out models. Journal of research in science teaching, 53(3), 502-523. Zaki, M. J. (2000, November). Sequence mining in categorical domains: incorporating constraints. In Proceedings of the 9th International Conference on Information and Knowledge Management (CIKM ’00), Agah, A., Callan, J., and Rundensteiner, E., (Eds.,) ACM Press, 422–429. Zhao, W., & Shute, V. J. (2019).  Can playing a video game foster computational thinking skills?.  Computers & Education, 141, 1-13.

