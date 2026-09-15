# Introducing a New Approach for Investigating Learning Behavior

**Conference:** ISLS 2021

## Abstract & Introduction

### Abstract
The potential of learners’ video interactions to understand learning behavior has been recognized in previous research. However, little research has yet been conducted on enhanced video-based environments using behavior sequence analyses. Hence, we developed Logible, a sensitive, web-based tool to detect and analyze meaningful behavior sequences of learners interacting with such environments. The tool is based on an iterative method. With Logible we were able to visualize learning behavior and emphasize differences in experimental conditions.

Introducing a New Approach for Investigating Learning Behavior Mario Niederhauser, University of Applied Sciences and Arts Northwestern Switzerland (FH NW) mario.niederhauser@gmail.com Alessia Ruf, University of Basel, alessia.ruf@fhnw.ch Joscha Jäger, filmicweb, joscha.jaeger@filmicweb.org Carmen Zahn, University of Applied Sciences and Arts Northwestern Switzerland (FHNW) carmen.zahn@fhnw.ch Klaus Opwis, University of Basel, klaus.opwis@unibas.ch Abstract: The potential of learners’ video interactions to understand learning behavior has been recognized in previous research. However, little research has yet been conducted on enhanced video-based environments using behavior sequence anal yses. Hence, we developed Logible, a sensitive, web-based tool to detect and analyze meaningful behavior sequences of learners interacting with such environments. The tool is based on an iterative method. With Logible we were able to visualize learning behavior and emphasize differences in experimental conditions.

Keywords: learning behavior, method development, sequence analysis, video-based learning

## Introduction

Today, enhanced video-based environments are able to support conceptual understanding and deep processing as they provide – along with basic video control tools (e.g., play, pause, rewind) – new tools that allow to annotate, discuss, or edit videos alone or in groups (e.g., Zahn, 2017). Research on learning analytics emphasizes that much can be learned from learners’ interactions with such enhanced videos about their learning behavior by analyzing log files that contain logged (inter-)action data (Mirriahi & Vigentini, 2017). However, while previous research has mostly focused on analyses of frequencies of single actions (e.g., by summarizing play clicks)  (Mubarak et al., 2020), Sinha et al. (2014)  argued that such analyses make it difficult to trace results back to actual learning behavior as hidden information from behavior patterns get lost.  They thus recommended to encode meaningful sequences from log files by grouping single (inter-)actions. Yet, such behavior analyses are still rare in previous research on enhanced video-based environments – not least because of the huge effort that needs to be invested to detect and elaborate meaningful sequences from raw log  files (Mubarak et al., 2020). We thus developed an interactive web-based tool (Logible) that is based on an iterative method and automatically visualizes and analyzes meaningful behavior sequences from raw log files of students learning either individually or in groups of two (i.e., learning setting) and using either hyperlinks or self-written annotations (i.e., learning task). In the present work, we ask: candifferences in learning behavior be made visible by developing a new method and tool using raw log files? – and hypothesize that differences in learning settings (H1a) and learning tasks (H1b) can be found.

## Methods

Logible (making log files legible) was developed based on an exploratory and iterative method using 92 data sets of totally 134 Swiss university students (75% female, M = 24.18 years, SD = 6.78) who learned about synaptic plasticity with the e nhanced video-based environment FrameTrail (https://frametrail.org) either individually (N = 50) or collaboratively in dyads using one shared desktop computer (N = 84 individuals in 42 dyads). Participants could either add self-written annotations based on additional predefined informative texts (N = 65)  or hyperlinks including these texts (N = 69) directly at appropriate places into the video and change their display time on th e video timeline. FrameTrail automatically provided raw log file s for each individual or collaborative data set containing learners’ interactions in chronological array of occurrence. To find meanin gful behavior sequences, two experts manually built groups of actions performed in conjunction with each other and defined rules for each of the detected sequences (e.g., mandatory actions of a sequence). The method was continuously improved and finally resulted in 17 behavior sequences (see Figure 1). At the same time, a first prototype of Logible was developed that was able to read the log files (see Figure 2) and considered the factors priority, length (of sequence), and homogeneity to detect the most meaningful sequences to be used for further analyses  (see black framed sequence in Figure 2). The sequences were then assigned to five behavior patterns  based on (1) their intentional level (i.e., did learners search or find appropriate places in the video to add an annotation or hyperlink) and (2) their level of content creation (i.e., did learners add or modify annotations or hyperlinks). We used behavior patterns for further analyses as (1) they show a higher contrast capability than sequences and because (2) not all sequences appear in the hyperlink condition (see Figure 1).

Figure 1. Overview of behavior sequences and behavior patterns with prioritization

Figure 2. Example of detected sequences of a collaborative group (ID = 42) using annotations in Logible.

## Findings

A MANOVA with learning task and setting as between-subject factors and relative values of the five behavior patterns as dependent varia bles revealed a significant main effect for learning task (F(4, 85) = 4.650, p =.002; Pillai’s Trace =.180), as expected (H1b), indicating a difference in the frequen cies of behavior patterns between the annotation and hyperlink condition (i.e., 2. Search and modify (p =.010) and 4. Find and modify  (p =.023) occurred more often in the annotation  condition and 3. Find and add (p =.035) and 5. Search and navigate (p = 0.15) occurred more often in the hyperlink condition). No main effect was found for learning setting (p >.05).

## Conclusions and implications

This study aimed to develop a new method and tool (based on log files) for gaining insights into learners’ behavior when interacting and learning with an enhanced video-based environment. Our approach to detect and visualize meaningful behavior sequences from raw log files  was successful and resulted in interesting new insights. Therefore, we conclude that differences in learning behavior can be ma de visible by applying our me thod using the newly developed application Logible. Future research should increasingly consider sequence behavior analyses when investigating enhanced video-based learning. We encourage researchers to work with our tool.

## References

Mirriahi, N., & Vigentini, L. (2017). Analytics of learner video use. I n Handbook of learning analytics  (Vol. 1, pp. 251–267).

Mubarak, A. A., Cao, H., & Ahmed, S. A. M. (2020). Predictive learni ng analytics using deep learning model in MOOCs’ courses videos. Education and Information Technologies. https://doi.org/10.1007/s10639-02010273-6 Sinha, T., Jermann, P., Li, N., & Dillen bourg, P. (2014). Your click decides your fate: Inferring Infor mation Processing and Attrition Behavior from MOOC Video Clickstream Interac tions. Proceedings of the EMNLP’2014 Workshop, 3–14.

Zahn, C. (2017). Digital design and learning: Cognitive-constructivist perspectives. In S. Schwan & U. Cress (Eds.), The Psychology of Digital Learning: Constructing, Exchanging and Acquiring Knowledge with Digital Media. (pp. 147–170). Springer International Publishing A.

## Acknowledgements

This work was funded by the Swiss National Science Foundation (SNSF) under Grant 100014_176084.

