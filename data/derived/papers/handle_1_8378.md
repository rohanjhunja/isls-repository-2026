# “What Should We Do With All These Webcams?” a Low-Cost Motion Capture System for Embodied, Ensemble Learning in Mixed-Reality Mathematics Activities

**Conference:** ISLS 2022

## Abstract & Introduction

### Abstract
As schools in the United States begin to reopen, mathematics teachers are presented with renewed opportunities to design activities rooted in embodied cognition. This project repurposes webcams bought for emergency remote teaching to create a low-cost, motion capture system to 1.) support embodied play for teaching mathematics in K-12 classrooms, and 2.) build on theories of embodied cognition (Núñez et al., 1999), collaborative ensembles (Ma, 2016), and gestures and viewpoints (DeLiema et al., 2021).

“What Should We Do with All These Webcams?” A Low-Cost Motion Capture System for Embodied, Ensemble Learning in Mixed-Reality Mathematics Activities Mighty Chen, California State University Fresno, mchen37@mail.fresnostate.edu Abstract: As schools in the United States begin to reopen, mathematics teachers are presented with renewed opportunities to design activities roote d in embodied cognition. This project repurposes webcams bought for emergency remote teaching to create a low-cost, motion capture system to 1.) support embodied play for teaching mathematics in K-12 classrooms, and 2.) build on theories of embodied cognition (Núñez et al., 1999), collaborative ense mbles (Ma, 2016), and gestures and viewpoints (DeLiema et al., 2021).

Objective This poster showcases a motion-capture technology to invite teachers to design activities which make embodiment accessible to more learners. By using embodiment as a resource, students can make meaningful actions which represent their learning and their understanding of a mathematical concept (Gerofsky, 2011). To help students construct meaning out of their actions, this technology provides live feedback of students’ locations as they move. This project contributes to the knowledge base about how high school students can be supported to learn by participating in whole-bodied and goal-oriented sensorimotor enactments to construct conceptual meaning— while factoring the limitation of cost, which many public K-12 school districts have.

## Background

This technology draws from the literature around the Science through Technology Enhanced Play (STEP) project (Enyedy et al., 2012)—drawing on principles of Gesture, Body Movement, and Viewpoints—and the work of Ma

(2012) in ensemble, whole-body interactions. The learning sciences offers a range of worked examples of built

technologies for mathematics education: Mathematical Imagery Trainer for Proportion (Abrahamson & Howison, 2010), STEP (Enyedy et al., 2012), Graspable Math (Weitnauer et al., 2016), among many others. Yet, we often lack opportunities to shape each other’s designs. As a work in progress, I propose this system for the community to extend feedback on how to further guide the project. Design The current iteration of the system1 is built on four low-cost webcams purchased by the author’s school district for distance learning. The use of ArUco markers allows for minimal computational power (Garrido-Juardo et al.,

2014) and provides detected camera extrinsic values which can be transformed into real world coordinates (Zhang

& Chen, 2021). The system candetect multiple markers simultaneously, allowing for an ensemble of students to participate and play collaboratively within a given activity. Figure 1 Two participants enact physical movements to make a goal parabola. CSCL2022 Proceedings 597 © ISLS The two participants shown in Figure 1 hold ArUco markers, which are detected by the motion-capture system to send position data to a Desmos2 graph over a web socket. Several expressions power the graph displayed in Figure 1, tasking  participants to match the equat ion provided. As participants move around the room, their positions are displayed in the Desmos graph and update the parabola created between them.

Using the Desmos Graphing Calculator as the front-end platform is advantageous to reach more classrooms. It allows teachers who are familiar with the software to design and create activities based on any mathematical concept, or to import a previously created activity into the graph. For e xample, a teacher might design an activity where students could embody the  points of a polygon while making rotations, data points to create a linear regression, or the points of a function as it shifts vertically or horizontally. There are still many design decisions which can provide affordances and constraints for participants to make meaningful actions: Should multiple camera angles be included, or should all cameras (and, students) face one direction? Should participants be wearing or holding the detection markers? Should or when should students be provided a projected graph on the ground they move on as well? While these questions should be addressed by educators with knowledge of their context, this project offers one experiential lens for informing such decisions.

## Conclusion

This poster features a motion capture system, in  early stages, to showcase a digital technology which affords social learning through goal-oriented embodied play, allowing students to think about and represent their understanding of mathematical concepts. By using low-cost hardware, non-intensive software, and a popular graphing application, this system allow s teachers to design and create activities for their students to use embodiment as a resource. As this project unfolds, I seek to extend on theories surrounding the work of Enyedy (2012), DeLiema (2021), and Ma (2017) to further understand how students respond to a pedagogical design that invites them to use their whole selves to enact and explore mathematical concepts across mixed-reality spaces.

## Endnotes

(1) The software, created by the author, is accessible at http://www.github.com/mchen0037/whole-bodied-mathematics

(2) Desmos Graphing Calculator is a free, online software which can plot, graph, or use a  JavaScript API to

programmatically update expressions on the graph. The author uses the API to host a website which plots the AruCo marker p ositions, after it is detected by the cameras. The site is hos ted at http://adjchen.com/whole-bodiedmathematics

## References

Abrahamson, D., & Howinson, M. L.  (2010, May). Embodied artifacts: Coordinated action as an object-to-thinkwith. In D.L. Holton (Chair) & J.P. Gee (Discussant), Embodied and enactive approaches to instruction: implications and innovations.  Paper presented at the annual meeting of the American Educational Research Association, April 30 – May 4.

DeLiema, D., Enyedy, N., Steen, F., & Danish, J.A. (2021). Integrating Viewpoint and Space: How Lamination across Gesture, Body Movement, Language, and Material Resources Shapes Learning. Cognition and Instruction, 39, 328-365.

Enyedy, N., Danish, J.A., Delacruz, G., & Kumar, M. (2012). Learning physics through play in an augmented reality environment. Computer Supported Learning, 7, 347-378. Gerofsky, S. (2011). Seeing the graph vs. being the graph: Gesture, engagement and awareness in school mathematics. In Stam, G. & Ishino, M. (Eds.), Integrating Gestures: The interdisciplinary nature of gesture (pp. 245-257).

Ma, J.Y. (2016) Ensemble learning and knowing: Devel oping a walking scale geometry dilation strategy. I n A. A. diSessa, M. Levin, & N. J. S. Brown (Eds.) Knowing and learning in interaction: A synthetic agenda for the learning sciences. New York, NY: Routledge.

Ma, J.Y. (2017) Multi-Party, Whole-Body Interactions in Mathematical Activity. Cognition and Instruction, 35, 141-165.

Núñez, R.E., Edwards, L.D., & Filipe Matos, J. (1999). Embodied cognition a s grounding for situatedness and context in mathematics education. Educational Studies in Mathematics, 39, 45-65. Garrido-Jurado, S., Muñoz-Salinas, R., Madrid-Cuevas, F.J., Marín-Jiménez, M.J. (2014). Automatic generation and detection of highly reliable fiducial markers under occlusion. Pattern Recognition. 47, 6, 2280-2292. Weitnauer, E., Landy, D., & Ottmar, E. (2016). Graspable math: Towards dynamic algebra notations that support learners better than paper. Future Technologies Conference. San Francisco, CA. Zhang, G., Chen, Y. (2021). "A Metric For Evaluating 3 d Reconstruction And Mapping Performance With No Ground Truthing," 2021 IEEE International Conference on Image Processing (ICIP) pp. 3178-3182. CSCL2022 Proceedings 598 © ISLS

