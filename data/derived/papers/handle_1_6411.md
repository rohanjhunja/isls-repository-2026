# Increasing Children’s Knowledge of Pattern Detection and Skip Counting Using a Tablet-based Math Activity

**Conference:** ICLS 2020

## Abstract & Introduction

### Abstract
This study uncovers the potential learning difficulties that K-2 students faced while learning about missing number completion in a tablet-based program called RoboTutor. We analyzed 185,064 cases of log-data from 283 students to determine the tutor pass rates and learning curves for each activity within that knowledge component. Students are likely not well-prepared or do not have the prerequisite skills to do this activity, therefore, we conclude that the activities need to be redesigned.

Increasing Children’s Knowledge of Pattern Detection and Skip Counting Using a Tablet-Based Math Activity Cheyeon Ha, Florida State University, ch16c@my.fsu.edu Xinying Hou, Carnegie Mellon University, xhou@andrew.cmu.edu Anh Huy Nguyen, Carnegie Mellon University, hn1@andrew.cmu.edu Judith Odili Uchidiuno, Carnegie Mellon University, jio@andrew.cmu.edu Abstract: This study uncovers the potential learning difficulties that K-2 students faced while learning about missing number completion in a tablet-based program called RoboTutor. We analyzed 185,064 cases of log-data from 283 students to determine the tutor pass r ates and learning curves for each activity within that knowledge component. Students are likely not wellprepared or do not have the prerequisite skills to do this activity, therefore, we conclude that the activities need to be redesigned.

## Introduction

Learning number sense involves developing several basic mathematical skills such as number counting, transformation, estimation and pattern detection (Andrews  et al, 2015). Young children often need extensive support and practice opportunities to develop their pattern detection and skip counting as it requires the knowledge of multiple mathematical skills. However, this level of support is typically not available to children in low-income families, who are more susceptible to math learning difficulties (Jordan  et al., 2006). The RoboTutor program addresses this challenge by designing tablet-based learning activities for children in rural Tanzania (Uchidiuno et al., 2018). In this work, we analyze log data from prior RoboTutor sessions to identify potential improvements to the learning content especially focused on increasing pattern detection and skip countin g. We investigated the following research questions:

• Q1. How do the students’ error rates change as the pattern detection activity difficulty increases?

• Q2. How are different difficulty features (e.g. counting integer, blank position, etc.) related to students’

error rates in this activity?

## Method

Learning program The RoboTutor program aims to provide a supplement or substitute for math and reading activities typically taught to students in K-2 (example activity shown in Figure 1). After mastering number identificati on, number discrimination, and basic addition, students engage in a pattern detection number activity that asks them to detect the pattern of a number sequence and fill in the next number in the sequence. Students ar e required to score at least 70% on each 10-question activity to proceed to the next activity; otherwise, they are presented with an easier activity or allowed further practice on the target activity. Dataset and Analysis 283 K-2 children living in rural Tanzania participated in tablet-based math learning activities. In this analysis, we focused on the pattern detection activity results and how studen ts’ error rates changed as the activity difficulty increased. The final data set includes 185,064 cases of log data from 96 different  activities (10 questions per activity). The tutor levels were sequential and ordered according to increasing diffi culty, such as a broader range of numbers (i.e., 0-9, 10-99, 100-900), larger interval, different blank spaces, etc. We aggregated the log dataset and tracked the pass rates of each session as well as each questions’ error rates. Al so, we conducted a logistic regression analysis with three input features: tutor level (a range of numbers),  numerical interval, and blank location.

## Results

First, we explored students’ pass rates each tutor (with 10 questions) with a  target pass rate of. 70. The chance/guessing pass rate of each activity was set at.33 as children could pick fr om one of three answer options and had three attempts at each ques tion. Also, children could retry any activities they failed. Howeve r, most students were performing worse than the baseline rate (33%), scoring an average o f 24% on even after multiple attempts (Figure 2).

Next, we explored the children’s error rate in each question category with lear ning curves (Figure 3). In each of the graphs, the x-axis denotes the number of practice opportunities for a given problem, and the y-axis denotes the average error rate (between 0 and 1). The learning curves corresponding to detecting patterns between 0-9 and 4-9 are smoother than others and decreasing in general, which is a good sign of students le arning. However, the learning curves corresponding to detecting patterns between 10-99 and 40-99 are mostly flat but also show wide fluctuation towards the end.

Figure 1. Example activity in RoboTutor.

Figure 2. Pass rates of the bubble pop tutors (ex).

Figure 3. Error rates of each question in the tutors (ex. at numbers 4-9 and 10-99).

A binomial logistic model was conducted to find what factors influence students’ erro r rates. (Table 1). When controlling other relative variables (the question type and hint), two possible factors are a numerical interval and blank locations. We assumed that higher numerical interval would be more difficult, however, it only happens at the 10-99 level (p <.001). When controlling other relative variables, the patterns of correction rates were similar in the 0-9 and 10-99 levels, however the direction was reversed in the 4-9 level. Table 1: Estimation of logistic regression model (*p<.05, **p<.01, and ***p<.001) Variables                                   Ranges 0-9 4-9 10-99 40-99 Numerical interval (1,2,5,10) 0.015 ** 0.036 *** -0.199 *** NA Blank location (1,2,3,4) -0.017* 0.079 *** -0.135*** 0.005 Other variables --- --- --- --(Intercept) 1.049 *** 0.972 *** 1.620 *** 0.957 *** Our takeaway is that children did not have sufficient background knowledge to engage in and master the activities covering the detection of patterns between 10-99, 40-99, and 100-900. Children need more exposure to basic skills such as adding and subtracting and skip counting within those intervals before they are presented with those activities. We conclude that children need more teaching guidance to engage in and master this tablet-based activity.

## References

Andrews, P., & Sayers, J. (2015). Identifying opportunities for grade one children to acquire foundational number sense: Developing a framework for cross-cultural classroom analyses. Early Childhood Education Journal, 43(4), 257-267.

Jordan, N. C., Kaplan, D., Nabors Olah, L., & Locuniak, M. N. (2006). Number sense growth in kindergarten: A longitudinal investigation of children at risk for mathematics difficulties. Child Development, 77(1), 153175. Uchidiuno, J., Yarzebinski, E., Madaio, M., Maheshwari, N., Koedinger, K., & Ogan, A.  (2018). Designing Appropriate Learning Technologies for School vs Home Settings in  Tanzanian Rural Villages. In Proceedings of the 1st ACM SIGCAS Conference on Computing and Sustainable Societies.

## Acknowledgments

Thank the Robotutor team for providing the data, thank Carnegie Mellon's learnlab for t he opportunity.

