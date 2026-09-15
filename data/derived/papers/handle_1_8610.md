# Uplift Modeling for Educational Data

**Conference:** ISLS 2022

## Abstract & Introduction

### Abstract
Traditional learner model focuses on modeling students’ mastery level of a knowledge component based on their historical learning trajectories. Uplift modeling tries to predict the difference between the treatment group and the control group so that the model can predict the actual causal effect of the intervention. We found that the hint effectively increases the learning gain and learners’ prior probability is an important factor affecting the learning gain.

Uplift modeling for educational data Ting Zhang, East China Normal University,51204108032@stu.ecnu.edu.cn Abstract: Traditional learner model focuses on modeling stud ents’ mastery level of a knowledge component based on their historical learn ing trajectories. Uplift modeling tries to predict the difference between the treatment group and the control group so that the model can predict the actual causal effect of the intervention. We found that the hint effectively increases the learning gain and learners’ prior probability i s an important factor affecting the learning gain.

## 1 Introduction

Adaptive learning systems provide personalized learning supports for students. There are many factors affecting learning, and the mechanism of learning is not clea r. It is difficult to carry out research through tr aditional experimental research, so it is still difficult to track the learning gain of students. However, many student modeling studies only focus on modeling the change of studen ts' knowledge ability level over time, such as Baye sian knowledge tracing and deep knowledge tracing. In co ntrast, uplift modeling allows for the addition of control groups, designed to clarify the difference in outco me probabilities between the modeling control group  and the treatment group, and is therefore more suitable for educational data analysis. The Uplift Model is an incremental Model designed to predict the causal effects of an intervention on an individual's state or behavior. Uplift modeling is receiving increasing attention from the business  analytics research as an improved example of predi ctive analytics for data-driven operational decisions.In this paper, the effectiveness of hints in adaptive learning systems on learning gain will be explored by using uplift modeling. Measuring and predicting "incremental improvements" resulting from interventions (such as hints) in the  adaptive learning system reflects the effect of "i ntelligent tutoring".

2 Uplift Modeling The uplift modeling is an incremental model designe d to predict the causal effects of an intervention on an individual's state or behaviour. The calculation formula of user I's causal effect is as follows: !! " #!$%& ' #!$(&                        （1） The goal of the uplift model is to maximize !!, which is an increment, the gain of the intervention strategy versus the no-intervention strategy, which is simpl y the difference between the outcome before and aft er the intervention. In practice, the estimated value of the expected causal Effect of all users will be used to measure the Effect of the whole user group, which is called Conditional Average Treatment Effect (CATE). Mathematically, it can be expressed as the difference between two Conditional probabilities:)*+,- !$.!& " / $#!$%&0.!& ' /$#!$(&0.!&                （2）.! is the characteristic of user I.  !! represents the user's intervention measures, which is a binary variable (1 represents intervention, 0 represents no intervention). #! represents the user's results (e.g., whether the student got the answer right or not); !$.!& represents the causal effect of the treatment group relative to the control group. Conditional means based on user characteristics.

Formula (2) is the ideal uplift calculation. In fac t, it is not possible to observe the output of user  I with treatment and control at the same time, i.e. it is not possible to obtain #!$%& and #!$(&at the same time. Therefore, formula (2) can be modified to obtain:

#!

"#$ " +!#!$%& ' $% ' +!&#!$(&                           (3) Where #!

"#$is the output observed by user I. +!is a binary variable,+! " % if user intervention is used, +! " (otherwise. Thus, the expected estimate of the conditional mean causal effect is: !$.!& " / 1#!

"#$2.!3 +! " %4 ' /1#!

"#$2.!3 +! " (4           (4) However, it should be emphasized here that Uplift modeling has high requirements for samples and must be subject to the Conditional Independence Assumption (CIA) that X and T are mutually independent, that is, user characteristics and intervention strategies are mutually independent: 5#!$%&3 #!$(&6 7 +!0.!                              (5) 3 Experiments In this experiment, Python package Pylift was used for the experiment, and Class Transformation Method  was used for uplift modeling. The KDD CUP2010 data set we analyzed came from the research data of adaptive ICLS2022 Proceedings 1860 © ISLS learning system. The study was divided into two groups: the no-hints group (as the control group for this study) and the hint group (as the treatment group).Figure 1 shows the QINI curve. As you can see, overall, the treatment group got 0.8% more correct answers than the control group. The Adjusted Qini curve is shown in Figure 2. FIG. 3 shows the cumulative gain curve. The area between qini curve and random line AUUC= 0.29; The area between aqini curve and ideal curve AUUC=0.08; The Cumulative gain curve and the area between the best practice curve AUUC= 0.11. From the experimental results, it can b e seen that the hints in the adaptive learning syst em can improve the learning gain of students.

Figure 1 The Evaluation metrics for the KDD cup 2010 data Figure 1-a The Qini curve           Figure 1-b The Adjusted Qini curve Figure 1-c The Cumulative gain curve Information value (IV) provides a good framework for exploratory analysis and variable screening of binary classifiers. IV Consider the independent contributi on of each variable to the result. The net Informat ion Value (NIV) measures the strength of a given variable. The NET Information Value (NIV) figure obtained after uplift modeling (FIG. 2) shows that "Corrects" has the lar gest weight. Therefore, it can be seen that learner s' initial ability (i.e., prior probability) when entering the system is an important factor affecting learning gain. Figure 2 The net information value of partially variable

## 4 Conclusions and future research

This paper uses the uplift model to model the educational data in the adaptive learning system, and explores the influence of the personalized intervention in the a daptive learning system, hint, on the learning gain. The experiment shows that hint is effective, and the le arning gain of the treatment group is higher than t hat of the control group. In addition, we also found that the prior probability of learners entering the system is an important factor affecting learning gain. Future studies will add datasets to explore the applicability of the u plift model in the field of education.

Reference Ja´skowski, Maciej, & Jaroszewicz, S.. (2012). Uplift modeling for clinical trial data. Radcliffe, N.. (2007). Using control groups to target on predicted lift: building and assessing uplift model. ICLS2022 Proceedings 1861 © ISLS

