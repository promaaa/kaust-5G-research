5/5 : SkyCell: A Prototyping Platform for 5G Aerial Base Stations:  
Deployment of an UABS (Unmanned Aerial Base Station) with proper 5G Backhauling. They used an  Intel NUC 7i7DNKE Mini PC  (apparently not real 5G due to lack of software but 4G (LTE) instead) on a DJI M600Pro
https://ece.northeastern.edu/wineslab/papers/ferranti2020skycell.pdf


4/5 : SkyRAN : Deployement of a 4G (LTE) base station on a DJI M600Pro, this paper really focuses on how to position the drone, what is the impact of moving it etc. They were also using a mini Pc with an i7
https://cse.iitm.ac.in/~ayon/files/skyran-conext18.pdf

3/5 Flying Rebots : Prototype of Rebot (Relaying Robot) : focused on optimization of drone positionning near the UE to have efficient networking. Still using a x86 processor
https://www.eurecom.fr/en/publication/5492


IABEST: https://dl.acm.org/doi/10.1145/3495243.3558750

4/5 : Integrated Access and Backhaul in 5G : UAV CU/DU OAI separation :  Very interesting but not detailed paper on the implementation of a CU/DU separation on an UAV.
https://arxiv.org/abs/2305.05983

2/5 : Portable Embedded Deployment of 5G Standalone:  OAI Core Network deployment on Jetson Nano: Deployment of the entire Monolithic 5G RAN with the Jetson Nano.
https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10651594

2/5 :  5G Edge vision: Jetson Nano + OAI for video streaming (blind): Not completely related to the topic but uses a Jetson Nano connected to the UE.
https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10570607

1/5 : Comparison of 5G Wireless Backhaul Technologies : Wifi is not a good backhauling technique. Other than that, no particularly helpful information since OAI uses Emulated IAB.
https://ieeexplore.ieee.org/abstract/document/11366393

5G pico-cells (100-250m range) and femto-cells (10-50m range)

