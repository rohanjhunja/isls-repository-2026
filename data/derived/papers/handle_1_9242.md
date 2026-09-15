# What Can Automated Speech Recognition Add to Qualitative Video Observations of Small Groups’ Collaborative Interactions?

**Conference:** ISLS 2023

## Abstract & Introduction

### Abstract
This study explores engaged and disengaged collaborative learning (CL) by applying qualitative video coding and automated speech recognition to video and audio data. We present a case study of 2 groups (N=6) of students building a robot together. Their CL interactions were 1) qualitatively coded for on-task behavior; 2) analyzed with speech recognition methods for voice activity and speaker identification. The initial results visualize how conversation patterns differ between groups and discuss the value of automated speech recognition combined with qualitative video coding for investigating engaged and disengaged CL in group interactions.

CSCL 2023 Proceedings  © ISLS 382 What Can Automated Speech Recognition Add to Qualitative Video Observations of Small Groups’ Collaborative Interactions? Kateryna Zabolotna, University of Oulu, kateryna.zabolotna@oulu.fi Daniel Spikol, University of Copenhagen, ds@di.du.dk Jonna Malmberg, University of Oulu, jonna.malmberg@oulu.fi Abstract: This study explores engaged and disengaged collaborative learning (CL) by applying qualitative video coding and automated speech recognition to video and audio data. We present a case study of 2 groups (N=6) of students building a robot together. Their CL interactions were

1) qualitatively coded for on-task behavior; 2) analyzed with speech recognition meth ods for

voice activity and speaker identification. The initial results visualize how conversation patterns differ between groups and discuss the value of automated speech recognition combi ned with qualitative video coding for investigating engaged and disengaged CL in group interactions.

## Introduction

Current research on CL has been widely utilizing video recordings as the primary data channel to understand how students collaborate (e.g., Zabolotna et al., 2023). While video recordings are an invaluable source that can provide plenty of information abou t students’ interactions and CL, it is time intensive and laborious to analyze them despite using systematic approaches. In this regard, using automated speech analy sis has excellent potential to reveal the richness of CL interactions. Moreover, speech activity can sh ed light on the quality of collaboration (see, e.g., Praharaj et al., 2021). However, more fine-grained qualitative resea rch is needed to explore whether and to what extent it is possible to identify CL interactions to understand what engaged and disengaged CL looks like from automated speech analysis. Thus, this study aims to explore engaged and disengaged collaboration by combining automatic speech analysis focusing on non-verbal speech features (e.g., talk and silence duration; turntaking) and qualitative video coding. In the present study, we ask: to what extent is automated speech analysis useful for revealing engaged and disengaged CL?

## Methods

In this case study, we present two groups of students (N=6; 2 females; 15-16 ye ars old) who were the most and the least engaged in CL. Their task was to build a robotic arm together by following video instructions. Their CL interactions were video and audio recorded, resulting in 3 h 32 min of data use d for the current analysis. Video data were analyzed with the video coding scheme that was developed to capture  three elements of engaged CL:

1) on-task behavior (Beserra et al., 2019); 2) students’ joint meta cognitive monitoring (Sobocinski et al., 2022)

and 3) knowledge co-construction (Zabolotna et al., 2023). We show the results of the initial coding stage focusing on students’ on-task behavior. The unit of analysis was a meaningful episode, i.e., it would start when a criterion for a specific behavior began and end when the mentioned behavior ended. Audio rec ordings of the two groups were used for automated speech recognition analysis. For our initial explorations, we selected short audio clips of 1.5 minutes, including both on-task and off-task behavior from the two groups that were segmented into 30-sec windows. Using Pyannote (Bredin et al., 2020) and an open-source toolkit in Python for  speaker diarization and voice activity detection (VAD) and pre-trained models, we can quickly investi gate speech patterns between the engaged and the disengaged groups.

## Initial findings and discussion

The behavior differed significantly between the engaged and disengaged groups. The results of qualitative video coding display that for almost the whole session duration, the engaged group was focus ed on building the robot and task-related discussions. In contrast, the members of the disengaged gr oup barely interacted with each other or with the task. These results are supported by the automated speech analysis that visualizes the opposite speech patterns of the two groups. When comparing VAD between the two groups (see Figure 1), one can see the difference in the amount of talk and silence during this short window. Table 1 Behavior types of engaged and disengaged groups CSCL 2023 Proceedings  © ISLS 383 Figure 1 Voice Activity Detection comparison When we look at who speaks and whether their speech overlaps (speaker diar ization; Figure 2), we can see how conversation patterns differ between the participants, considering that th ese are 30-sec windows. In the Engaged group, we see an overlap and a pattern of more constant conversation between the group members than the Disengaged group, with little talk and no speech overlap. Figure 2 Speaker Diarization comparison

## Conclusions

Our initial exploration shows that automated speech analysis can help identify CL  patterns and visualize the differences between groups and speakers by capturing their voice activity, i.e., talk a nd silence time and speaker identification. Our case example also shows that it can be used for data tria ngulation, as it supports the findings of qualitative video coding.  Limitations to be considered in the above examples are that these are concise excerpts of 1.5 minutes of more than 2 hours of learning activities. Furthermore, we have  used pre-trained models to perform the audio analysis and have yet to examine the accuracy of the res ults. Most notably, we must consider the collaboration flow over the entire period. Our initial aim is to develop to ols that combine automated speech and, eventually, video analysis to identify key/critical incidents in group work that ena ble us to identify collaboration patterns better, building on Pea and colleagues' early work (2008).

## References

Beserra, V., Nussbaum, M., & Oteo, M. (2019). On-task and off-task behavior in the classroom: A study on Mathematics learning with educational video data. Journal of Educational Computing Research, 56(8), 1361-1383.

Bredin, H., Yin, R., Coria, J. M., Gelly, G., Korshunov, P., Lavechin, M.,... & Gill, M. P. (2020). Pyannote. audio: Neural building blocks for speaker diarization.  IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), 7124-7128.

Pea, R., & Lindgren, R. (2008). Video collaboratories for research and educati on: An analysis of collaboration design patterns. IEEE Transactions on Learning Technologies 1 (4), 235-247. Praharaj, S., Scheffel, M., Schmitz, M., Specht, M. & Drachsler, H. (2021). T owards automatic collaboration analytics for group speech data using learning analytics. Sensors, 21, 3156. Sobocinski, M., Malmberg, J., & Järvelä, S. (2022). Exploring adaptation in socially-shared regulation of learning using video and heart-rate data. Technology, Knowledge, and Learning, 27, 385-404. Zabolotna, K., Malmberg, J. & Järvenoja, H. (2023). Examining the interplay of knowledge c onstruction and group-level regulation in a computer-supported collaborative learning physics task. Computers in Human Behavior, 138, 107494.

