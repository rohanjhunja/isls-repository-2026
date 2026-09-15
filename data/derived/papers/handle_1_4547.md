# Identifying Learning Leaders in Collaborative Learning

**Conference:** CSCL 2019

## Abstract & Introduction

### Abstract
This study applies social network analysis to identify learning leaders in online collaborative learning. We used indegree, outdegree, and betweenness to categorize learners by their learner participation roles. Three learner roles (full facilitator, transactional facilitator, and attractive facilitator) fit the theories of learning leadership and were effective in identifying learning leaders. The findings pave the foundation for further research developing real-time instrument for instructors to identify learning leaders, and provide timely learning support.

Identifying Learning Leaders in Collaborative Learning Yinying Wang, Georgia State University, Ywang103@gsu.edu Min Kyu Kim, Georgia State University, mkim120@gsu.edu Abstract: This study applies social network analysis to identify learning leaders in online collaborative learning. We used indegree, outdegree, and betweenness to categorize learners by their learner participation roles. Three learner roles (full facilitator, transactional facilitator, and attractive facilitator) fit the theories of learning leadership and were effective in identifying learning leaders. The findings pave the foundation for further research develop ing real-time instrument for instructors to identify learning leaders, and provide timely learning support.

## Introduction

The purpose of this paper is to explore a computational approach to identifying learning leaders in online collaborative learning. Specifically,  we used three network metrics —indegree, outdegree, and betweenness— generated from social network analysis (SNA) to examine social dynamics in online discussions and thus identify learning leaders. Given the social nature of learning leader ship, learners’ social interactions can be tracked in online learning systems. The data on social interactions can thus enable us to identify learning leaders. However, the literature on leadership and online learning has been mostly running in parallel with little overlap. In this study, we first integrate the literature on leadership and online learning, a nd then applies social network analysis to develop and compare two leadership classification models to identif y learner leaders.  Specifically, we ask two research questions: x How do we use social network metrics to characterize different learner roles in online discussion? x How do we identify learning leaders from the learner participation model? Prior literature has proposed a computational approach to classify different learner roles in online learnin g by using three social network analysis metrics in combination: (1) indegree—the number of messages sent by a learner; (2) outdegree—the number of messages received by a learner; and (3) betweenness—the extent to which a learner controls the communication between two other students in a community (Kim et al., 2018, in press). The three metrics correspond to popularity, influence, and mediation, respectively. Drawing on prior literature, the current study defines different learner roles in online collaboration each of which is matched with a combination of the thresholds of the three metrics (see Table 1). In our previous studies (Kim et al., 2018), we introduced two models of leaner participation classification: three-level model (full participant, inbound participant, and and peripheral participant) and four-level model (full participant, engaging participant, peripheral participant, and marginal participant).  We hypothesize that full participants, given the social nature of leadership (Wang, 2018), can be identified as learning leaders but insufficient to detail various characterstics of learning leaders. Table 1: Learner roles Learner Role Thresholds for the Metrics Indegree Outdegree Betweenness Full Facilitator > 75 > 75 > 75 Transactional Facilitator <  75 > 75 > 75 Attractive Facilitator > 75 < 75 > 75 Topical leading discussant > 75 > 75 < 75 Issue Seeker < 75 < 75 > 75 Active Commenter <  75 > 75 < 75

## Methods

This exploratory study used 21 students (5 male and 16 female) enrolled in a graduate-level online course that taught foundations of instructional design and technology. For 12-weeks asynchronous discussions, Each student was assigned at least a week to serve as a peer-moderator. For the online discussion each week, w e extracted social network data on who communicated with whom, how often the learners communicated,  and what the content of their communication was. We used the Node XL software to calculate the indegree, out degree, and betweenness-centrality metrics. Using the filtering approach (i.e., the 75 th percentile) described earlier, we classified individuals’ participation profiles for each week, centerining on the three learner roles: full facilitator, transactional facilitator, and attractive facilitator.

## Results

As expected, the number of leaders varied across weeks, ra ning from 2 to 5 (not including topical discusssant s), which seemed reflecting dynamic and situatioinal learner interation in that community. Concern ing the topical discussant, at least one topical discussant per week was identified (see Table 2). We decided to take the first three roles as leadership in online discussion community, because those roles fited our theortical justification of learning leaders, and conseravative apporoach to identifying leaders seemed better for a small group discussion (N = 21). Table 2: The number of learning leaders in each week by corresponding learner roles WK2 WK3 WK4 WK5 WK6 WK7 WK9 WK10 WK11 WK12 WK13 WK15 Full Facilitator 2 1 3 1 4 1 1 1 2 2 1 2 Transactional Facilitator   1 1  2  2  1 2 Attractive Facilitator 2 3  1   1 2 3 1  1 Topical Discussant 2 1 1 2 1 1 1 1  2  1 We then further reviewed topical discussants. For example, as depiected in the network visualization of week 12 (see Figure 1), two topical discussants (i.e., 216 and 223) positione d around the leaders (i.e., 205, 208, 214, and 219), building their subgroups. We  viewed that as far as their participation level is concerned, topical discussants would be at the fully engaged level  (i.e., full participant), but still grow to becoming leaders. Therefore, we determined not to have the topical discussant in the leader classifications.

Figure 1. Network visualization of the learner roles

This study proposed how to use social network analysis  to identify learning leaders in collaborative learning. This approachpaves the foundation for further research that develops real-time instrument for instructors to identify and classify learning leaders, and provide learning intervention and support in a timely manner.

## References

Kim, M., & Ayer, T. (in press). Learner participation profiles in an asynchronous onl ine collaboration context. Internet and Higher Education.

Kim, M., Ayer, T., & Bakshi, S. (2018, April). Profiling learner engagement in asynchronous online discussions: Validity and associations with motivation and performance. Paper presented at the American Educational Research Association Annual Meeting, New York, NY.

Wang. Y. (2018). It all starts with social ties: Developing school leadership from the social network perspectives. NASSP Bulletin, 102(4), 323–340.

## Acknowledgments

The study reported in this paper is based on the work in “How people develop learning Leadership: Learner Characteristics, Leadership Style, and the Dynamics of Asynch ronous Online Learning” supported by Spencer Foundation (#201900017).

