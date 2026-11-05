* CCSA Bus-2 cascade W=64 (m=4), corner TT, 2 consecutive additions
.include "asap7_models.sp"
.temp 25
.option post=2 runlvl=6
Vdd vdd 0 0.7
Vss vss 0 0
Vbus1 bus1 0 0.7
* --- devices: fin counts from Supp.E Listing 1 ---
.subckt VSW bus1 bus2 R Rb vdd vss
MN bus2 R bus1 vss nmos_rvt nfin=4
MP bus2 Rb bus1 vdd pmos_rvt nfin=4
.ends
.subckt HSW up dn Hb H vdd vss
MN dn H up vss nmos_rvt nfin=4
MP dn Hb up vdd pmos_rvt nfin=4
.ends
.subckt RCV in out vdd vss
MN out in vss vss nmos_rvt nfin=2
MP out in vdd vdd pmos_rvt nfin=2
.ends
.subckt PD bus vdd vss
MN bus vdd vss vss nmos_rvt nfin=1 $ edit: weakest device of your PDK (target R_pd >= 10 MOhm)
.ends
* corrected keeper: two inverters, so the feedback reinforces the held level
.subckt KEEP bus vdd vss
MN1 kb bus vss vss nmos_rvt nfin=1
MP1 kb bus vdd vdd pmos_rvt nfin=1
Rk kb kbw 200k $ edit: weak feedback; replace by long-L or stacked devices in your PDK
MN2 bus kbw vss vss nmos_rvt nfin=1
MP2 bus kbw vdd vdd pmos_rvt nfin=1
.ends
* rise-only repeater (Rule R1): pull-down stage enabled only during the Step-1 reset
.subckt REP_RO in out en vdd vss
MN6 n1 in vss vss nmos_rvt nfin=4
MP6 n1 in vdd vdd pmos_rvt nfin=4
MP7 out n1 vdd vdd pmos_rvt nfin=8
MN7 out n1 x vss nmos_rvt nfin=16
MN8 x en vss vss nmos_rvt nfin=16
.ends
.subckt SLICE bus1 up dn R Rb Hb H E vdd vss
XV bus1 dn R Rb vdd vss VSW
XH up dn Hb H vdd vss HSW
XR dn E vdd vss RCV
XP dn vdd vss PD
.ends
Ven en 0 PWL(0.0000e+00 0.700 1.2200e-09 0.700 1.2400e-09 0.000 4.8800e-09 0.000 4.9000e-09 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VR0 R0 0 PWL(0.0000e+00 0.000 1.2200e-09 0.000 1.2400e-09 0.700 4.8800e-09 0.700 4.9000e-09 0.000)
VRb0 Rb0 0 PWL(0.0000e+00 0.700 1.2200e-09 0.700 1.2400e-09 0.000 4.8800e-09 0.000 4.9000e-09 0.700)
VH0 H0 0 PWL(0.0000e+00 0.700)
VHb0 Hb0 0 PWL(0.0000e+00 0.000)
VR1 R1 0 PWL(0.0000e+00 0.000)
VRb1 Rb1 0 PWL(0.0000e+00 0.700)
VH1 H1 0 PWL(0.0000e+00 0.700)
VHb1 Hb1 0 PWL(0.0000e+00 0.000)
VR2 R2 0 PWL(0.0000e+00 0.000)
VRb2 Rb2 0 PWL(0.0000e+00 0.700)
VH2 H2 0 PWL(0.0000e+00 0.700)
VHb2 Hb2 0 PWL(0.0000e+00 0.000)
VR3 R3 0 PWL(0.0000e+00 0.000)
VRb3 Rb3 0 PWL(0.0000e+00 0.700)
VH3 H3 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb3 Hb3 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR4 R4 0 PWL(0.0000e+00 0.000)
VRb4 Rb4 0 PWL(0.0000e+00 0.700)
VH4 H4 0 PWL(0.0000e+00 0.700)
VHb4 Hb4 0 PWL(0.0000e+00 0.000)
VR5 R5 0 PWL(0.0000e+00 0.000)
VRb5 Rb5 0 PWL(0.0000e+00 0.700)
VH5 H5 0 PWL(0.0000e+00 0.700)
VHb5 Hb5 0 PWL(0.0000e+00 0.000)
VR6 R6 0 PWL(0.0000e+00 0.000)
VRb6 Rb6 0 PWL(0.0000e+00 0.700)
VH6 H6 0 PWL(0.0000e+00 0.700)
VHb6 Hb6 0 PWL(0.0000e+00 0.000)
VR7 R7 0 PWL(0.0000e+00 0.000)
VRb7 Rb7 0 PWL(0.0000e+00 0.700)
VH7 H7 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb7 Hb7 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR8 R8 0 PWL(0.0000e+00 0.000)
VRb8 Rb8 0 PWL(0.0000e+00 0.700)
VH8 H8 0 PWL(0.0000e+00 0.700)
VHb8 Hb8 0 PWL(0.0000e+00 0.000)
VR9 R9 0 PWL(0.0000e+00 0.000)
VRb9 Rb9 0 PWL(0.0000e+00 0.700)
VH9 H9 0 PWL(0.0000e+00 0.700)
VHb9 Hb9 0 PWL(0.0000e+00 0.000)
VR10 R10 0 PWL(0.0000e+00 0.000)
VRb10 Rb10 0 PWL(0.0000e+00 0.700)
VH10 H10 0 PWL(0.0000e+00 0.700)
VHb10 Hb10 0 PWL(0.0000e+00 0.000)
VR11 R11 0 PWL(0.0000e+00 0.000)
VRb11 Rb11 0 PWL(0.0000e+00 0.700)
VH11 H11 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb11 Hb11 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR12 R12 0 PWL(0.0000e+00 0.000)
VRb12 Rb12 0 PWL(0.0000e+00 0.700)
VH12 H12 0 PWL(0.0000e+00 0.700)
VHb12 Hb12 0 PWL(0.0000e+00 0.000)
VR13 R13 0 PWL(0.0000e+00 0.000)
VRb13 Rb13 0 PWL(0.0000e+00 0.700)
VH13 H13 0 PWL(0.0000e+00 0.700)
VHb13 Hb13 0 PWL(0.0000e+00 0.000)
VR14 R14 0 PWL(0.0000e+00 0.000)
VRb14 Rb14 0 PWL(0.0000e+00 0.700)
VH14 H14 0 PWL(0.0000e+00 0.700)
VHb14 Hb14 0 PWL(0.0000e+00 0.000)
VR15 R15 0 PWL(0.0000e+00 0.000)
VRb15 Rb15 0 PWL(0.0000e+00 0.700)
VH15 H15 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb15 Hb15 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR16 R16 0 PWL(0.0000e+00 0.000)
VRb16 Rb16 0 PWL(0.0000e+00 0.700)
VH16 H16 0 PWL(0.0000e+00 0.700)
VHb16 Hb16 0 PWL(0.0000e+00 0.000)
VR17 R17 0 PWL(0.0000e+00 0.000)
VRb17 Rb17 0 PWL(0.0000e+00 0.700)
VH17 H17 0 PWL(0.0000e+00 0.700)
VHb17 Hb17 0 PWL(0.0000e+00 0.000)
VR18 R18 0 PWL(0.0000e+00 0.000)
VRb18 Rb18 0 PWL(0.0000e+00 0.700)
VH18 H18 0 PWL(0.0000e+00 0.700)
VHb18 Hb18 0 PWL(0.0000e+00 0.000)
VR19 R19 0 PWL(0.0000e+00 0.000)
VRb19 Rb19 0 PWL(0.0000e+00 0.700)
VH19 H19 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb19 Hb19 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR20 R20 0 PWL(0.0000e+00 0.000)
VRb20 Rb20 0 PWL(0.0000e+00 0.700)
VH20 H20 0 PWL(0.0000e+00 0.700)
VHb20 Hb20 0 PWL(0.0000e+00 0.000)
VR21 R21 0 PWL(0.0000e+00 0.000)
VRb21 Rb21 0 PWL(0.0000e+00 0.700)
VH21 H21 0 PWL(0.0000e+00 0.700)
VHb21 Hb21 0 PWL(0.0000e+00 0.000)
VR22 R22 0 PWL(0.0000e+00 0.000)
VRb22 Rb22 0 PWL(0.0000e+00 0.700)
VH22 H22 0 PWL(0.0000e+00 0.700)
VHb22 Hb22 0 PWL(0.0000e+00 0.000)
VR23 R23 0 PWL(0.0000e+00 0.000)
VRb23 Rb23 0 PWL(0.0000e+00 0.700)
VH23 H23 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb23 Hb23 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR24 R24 0 PWL(0.0000e+00 0.000)
VRb24 Rb24 0 PWL(0.0000e+00 0.700)
VH24 H24 0 PWL(0.0000e+00 0.700)
VHb24 Hb24 0 PWL(0.0000e+00 0.000)
VR25 R25 0 PWL(0.0000e+00 0.000)
VRb25 Rb25 0 PWL(0.0000e+00 0.700)
VH25 H25 0 PWL(0.0000e+00 0.700)
VHb25 Hb25 0 PWL(0.0000e+00 0.000)
VR26 R26 0 PWL(0.0000e+00 0.000)
VRb26 Rb26 0 PWL(0.0000e+00 0.700)
VH26 H26 0 PWL(0.0000e+00 0.700)
VHb26 Hb26 0 PWL(0.0000e+00 0.000)
VR27 R27 0 PWL(0.0000e+00 0.000)
VRb27 Rb27 0 PWL(0.0000e+00 0.700)
VH27 H27 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb27 Hb27 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR28 R28 0 PWL(0.0000e+00 0.000)
VRb28 Rb28 0 PWL(0.0000e+00 0.700)
VH28 H28 0 PWL(0.0000e+00 0.700)
VHb28 Hb28 0 PWL(0.0000e+00 0.000)
VR29 R29 0 PWL(0.0000e+00 0.000)
VRb29 Rb29 0 PWL(0.0000e+00 0.700)
VH29 H29 0 PWL(0.0000e+00 0.700)
VHb29 Hb29 0 PWL(0.0000e+00 0.000)
VR30 R30 0 PWL(0.0000e+00 0.000)
VRb30 Rb30 0 PWL(0.0000e+00 0.700)
VH30 H30 0 PWL(0.0000e+00 0.700)
VHb30 Hb30 0 PWL(0.0000e+00 0.000)
VR31 R31 0 PWL(0.0000e+00 0.000)
VRb31 Rb31 0 PWL(0.0000e+00 0.700)
VH31 H31 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb31 Hb31 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR32 R32 0 PWL(0.0000e+00 0.000)
VRb32 Rb32 0 PWL(0.0000e+00 0.700)
VH32 H32 0 PWL(0.0000e+00 0.700)
VHb32 Hb32 0 PWL(0.0000e+00 0.000)
VR33 R33 0 PWL(0.0000e+00 0.000)
VRb33 Rb33 0 PWL(0.0000e+00 0.700)
VH33 H33 0 PWL(0.0000e+00 0.700)
VHb33 Hb33 0 PWL(0.0000e+00 0.000)
VR34 R34 0 PWL(0.0000e+00 0.000)
VRb34 Rb34 0 PWL(0.0000e+00 0.700)
VH34 H34 0 PWL(0.0000e+00 0.700)
VHb34 Hb34 0 PWL(0.0000e+00 0.000)
VR35 R35 0 PWL(0.0000e+00 0.000)
VRb35 Rb35 0 PWL(0.0000e+00 0.700)
VH35 H35 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb35 Hb35 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR36 R36 0 PWL(0.0000e+00 0.000)
VRb36 Rb36 0 PWL(0.0000e+00 0.700)
VH36 H36 0 PWL(0.0000e+00 0.700)
VHb36 Hb36 0 PWL(0.0000e+00 0.000)
VR37 R37 0 PWL(0.0000e+00 0.000)
VRb37 Rb37 0 PWL(0.0000e+00 0.700)
VH37 H37 0 PWL(0.0000e+00 0.700)
VHb37 Hb37 0 PWL(0.0000e+00 0.000)
VR38 R38 0 PWL(0.0000e+00 0.000)
VRb38 Rb38 0 PWL(0.0000e+00 0.700)
VH38 H38 0 PWL(0.0000e+00 0.700)
VHb38 Hb38 0 PWL(0.0000e+00 0.000)
VR39 R39 0 PWL(0.0000e+00 0.000)
VRb39 Rb39 0 PWL(0.0000e+00 0.700)
VH39 H39 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb39 Hb39 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR40 R40 0 PWL(0.0000e+00 0.000)
VRb40 Rb40 0 PWL(0.0000e+00 0.700)
VH40 H40 0 PWL(0.0000e+00 0.700)
VHb40 Hb40 0 PWL(0.0000e+00 0.000)
VR41 R41 0 PWL(0.0000e+00 0.000)
VRb41 Rb41 0 PWL(0.0000e+00 0.700)
VH41 H41 0 PWL(0.0000e+00 0.700)
VHb41 Hb41 0 PWL(0.0000e+00 0.000)
VR42 R42 0 PWL(0.0000e+00 0.000)
VRb42 Rb42 0 PWL(0.0000e+00 0.700)
VH42 H42 0 PWL(0.0000e+00 0.700)
VHb42 Hb42 0 PWL(0.0000e+00 0.000)
VR43 R43 0 PWL(0.0000e+00 0.000)
VRb43 Rb43 0 PWL(0.0000e+00 0.700)
VH43 H43 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb43 Hb43 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR44 R44 0 PWL(0.0000e+00 0.000)
VRb44 Rb44 0 PWL(0.0000e+00 0.700)
VH44 H44 0 PWL(0.0000e+00 0.700)
VHb44 Hb44 0 PWL(0.0000e+00 0.000)
VR45 R45 0 PWL(0.0000e+00 0.000)
VRb45 Rb45 0 PWL(0.0000e+00 0.700)
VH45 H45 0 PWL(0.0000e+00 0.700)
VHb45 Hb45 0 PWL(0.0000e+00 0.000)
VR46 R46 0 PWL(0.0000e+00 0.000)
VRb46 Rb46 0 PWL(0.0000e+00 0.700)
VH46 H46 0 PWL(0.0000e+00 0.700)
VHb46 Hb46 0 PWL(0.0000e+00 0.000)
VR47 R47 0 PWL(0.0000e+00 0.000)
VRb47 Rb47 0 PWL(0.0000e+00 0.700)
VH47 H47 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb47 Hb47 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR48 R48 0 PWL(0.0000e+00 0.000)
VRb48 Rb48 0 PWL(0.0000e+00 0.700)
VH48 H48 0 PWL(0.0000e+00 0.700)
VHb48 Hb48 0 PWL(0.0000e+00 0.000)
VR49 R49 0 PWL(0.0000e+00 0.000)
VRb49 Rb49 0 PWL(0.0000e+00 0.700)
VH49 H49 0 PWL(0.0000e+00 0.700)
VHb49 Hb49 0 PWL(0.0000e+00 0.000)
VR50 R50 0 PWL(0.0000e+00 0.000)
VRb50 Rb50 0 PWL(0.0000e+00 0.700)
VH50 H50 0 PWL(0.0000e+00 0.700)
VHb50 Hb50 0 PWL(0.0000e+00 0.000)
VR51 R51 0 PWL(0.0000e+00 0.000)
VRb51 Rb51 0 PWL(0.0000e+00 0.700)
VH51 H51 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb51 Hb51 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR52 R52 0 PWL(0.0000e+00 0.000)
VRb52 Rb52 0 PWL(0.0000e+00 0.700)
VH52 H52 0 PWL(0.0000e+00 0.700)
VHb52 Hb52 0 PWL(0.0000e+00 0.000)
VR53 R53 0 PWL(0.0000e+00 0.000)
VRb53 Rb53 0 PWL(0.0000e+00 0.700)
VH53 H53 0 PWL(0.0000e+00 0.700)
VHb53 Hb53 0 PWL(0.0000e+00 0.000)
VR54 R54 0 PWL(0.0000e+00 0.000)
VRb54 Rb54 0 PWL(0.0000e+00 0.700)
VH54 H54 0 PWL(0.0000e+00 0.700)
VHb54 Hb54 0 PWL(0.0000e+00 0.000)
VR55 R55 0 PWL(0.0000e+00 0.000)
VRb55 Rb55 0 PWL(0.0000e+00 0.700)
VH55 H55 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb55 Hb55 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR56 R56 0 PWL(0.0000e+00 0.000)
VRb56 Rb56 0 PWL(0.0000e+00 0.700)
VH56 H56 0 PWL(0.0000e+00 0.700)
VHb56 Hb56 0 PWL(0.0000e+00 0.000)
VR57 R57 0 PWL(0.0000e+00 0.000)
VRb57 Rb57 0 PWL(0.0000e+00 0.700)
VH57 H57 0 PWL(0.0000e+00 0.700)
VHb57 Hb57 0 PWL(0.0000e+00 0.000)
VR58 R58 0 PWL(0.0000e+00 0.000)
VRb58 Rb58 0 PWL(0.0000e+00 0.700)
VH58 H58 0 PWL(0.0000e+00 0.700)
VHb58 Hb58 0 PWL(0.0000e+00 0.000)
VR59 R59 0 PWL(0.0000e+00 0.000)
VRb59 Rb59 0 PWL(0.0000e+00 0.700)
VH59 H59 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb59 Hb59 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
VR60 R60 0 PWL(0.0000e+00 0.000)
VRb60 Rb60 0 PWL(0.0000e+00 0.700)
VH60 H60 0 PWL(0.0000e+00 0.700)
VHb60 Hb60 0 PWL(0.0000e+00 0.000)
VR61 R61 0 PWL(0.0000e+00 0.000)
VRb61 Rb61 0 PWL(0.0000e+00 0.700)
VH61 H61 0 PWL(0.0000e+00 0.700)
VHb61 Hb61 0 PWL(0.0000e+00 0.000)
VR62 R62 0 PWL(0.0000e+00 0.000)
VRb62 Rb62 0 PWL(0.0000e+00 0.700)
VH62 H62 0 PWL(0.0000e+00 0.700)
VHb62 Hb62 0 PWL(0.0000e+00 0.000)
VR63 R63 0 PWL(0.0000e+00 0.000)
VRb63 Rb63 0 PWL(0.0000e+00 0.700)
VH63 H63 0 PWL(0.0000e+00 0.700 6.1000e-09 0.700 6.1200e-09 0.000)
VHb63 Hb63 0 PWL(0.0000e+00 0.000 6.1000e-09 0.000 6.1200e-09 0.700)
Vin nin 0 0 $ B2[-1] = 0 at the first repeater input
Xrep0 nin s0_0 en vdd vss REP_RO
Xkp0 nin vdd vss KEEP
Xbs0 bus1 s0_0 s0_1 R0 Rb0 Hb0 H0 E0 vdd vss SLICE
Xbs1 bus1 s0_1 s0_2 R1 Rb1 Hb1 H1 E1 vdd vss SLICE
Xbs2 bus1 s0_2 s0_3 R2 Rb2 Hb2 H2 E2 vdd vss SLICE
Xbs3 bus1 s0_3 s0_4 R3 Rb3 Hb3 H3 E3 vdd vss SLICE
Xbs4 bus1 s0_4 s0_5 R4 Rb4 Hb4 H4 E4 vdd vss SLICE
Xbs5 bus1 s0_5 s0_6 R5 Rb5 Hb5 H5 E5 vdd vss SLICE
Xbs6 bus1 s0_6 s0_7 R6 Rb6 Hb6 H6 E6 vdd vss SLICE
Xbs7 bus1 s0_7 s0_8 R7 Rb7 Hb7 H7 E7 vdd vss SLICE
Xbs8 bus1 s0_8 s0_9 R8 Rb8 Hb8 H8 E8 vdd vss SLICE
Xbs9 bus1 s0_9 s0_10 R9 Rb9 Hb9 H9 E9 vdd vss SLICE
Xbs10 bus1 s0_10 s0_11 R10 Rb10 Hb10 H10 E10 vdd vss SLICE
Xbs11 bus1 s0_11 s0_12 R11 Rb11 Hb11 H11 E11 vdd vss SLICE
Xbs12 bus1 s0_12 s0_13 R12 Rb12 Hb12 H12 E12 vdd vss SLICE
Xbs13 bus1 s0_13 s0_14 R13 Rb13 Hb13 H13 E13 vdd vss SLICE
Xbs14 bus1 s0_14 s0_15 R14 Rb14 Hb14 H14 E14 vdd vss SLICE
Xbs15 bus1 s0_15 s0_16 R15 Rb15 Hb15 H15 E15 vdd vss SLICE
Xrep1 s0_16 s1_0 en vdd vss REP_RO
Xkp1 s0_16 vdd vss KEEP
Xbs16 bus1 s1_0 s1_1 R16 Rb16 Hb16 H16 E16 vdd vss SLICE
Xbs17 bus1 s1_1 s1_2 R17 Rb17 Hb17 H17 E17 vdd vss SLICE
Xbs18 bus1 s1_2 s1_3 R18 Rb18 Hb18 H18 E18 vdd vss SLICE
Xbs19 bus1 s1_3 s1_4 R19 Rb19 Hb19 H19 E19 vdd vss SLICE
Xbs20 bus1 s1_4 s1_5 R20 Rb20 Hb20 H20 E20 vdd vss SLICE
Xbs21 bus1 s1_5 s1_6 R21 Rb21 Hb21 H21 E21 vdd vss SLICE
Xbs22 bus1 s1_6 s1_7 R22 Rb22 Hb22 H22 E22 vdd vss SLICE
Xbs23 bus1 s1_7 s1_8 R23 Rb23 Hb23 H23 E23 vdd vss SLICE
Xbs24 bus1 s1_8 s1_9 R24 Rb24 Hb24 H24 E24 vdd vss SLICE
Xbs25 bus1 s1_9 s1_10 R25 Rb25 Hb25 H25 E25 vdd vss SLICE
Xbs26 bus1 s1_10 s1_11 R26 Rb26 Hb26 H26 E26 vdd vss SLICE
Xbs27 bus1 s1_11 s1_12 R27 Rb27 Hb27 H27 E27 vdd vss SLICE
Xbs28 bus1 s1_12 s1_13 R28 Rb28 Hb28 H28 E28 vdd vss SLICE
Xbs29 bus1 s1_13 s1_14 R29 Rb29 Hb29 H29 E29 vdd vss SLICE
Xbs30 bus1 s1_14 s1_15 R30 Rb30 Hb30 H30 E30 vdd vss SLICE
Xbs31 bus1 s1_15 s1_16 R31 Rb31 Hb31 H31 E31 vdd vss SLICE
Xrep2 s1_16 s2_0 en vdd vss REP_RO
Xkp2 s1_16 vdd vss KEEP
Xbs32 bus1 s2_0 s2_1 R32 Rb32 Hb32 H32 E32 vdd vss SLICE
Xbs33 bus1 s2_1 s2_2 R33 Rb33 Hb33 H33 E33 vdd vss SLICE
Xbs34 bus1 s2_2 s2_3 R34 Rb34 Hb34 H34 E34 vdd vss SLICE
Xbs35 bus1 s2_3 s2_4 R35 Rb35 Hb35 H35 E35 vdd vss SLICE
Xbs36 bus1 s2_4 s2_5 R36 Rb36 Hb36 H36 E36 vdd vss SLICE
Xbs37 bus1 s2_5 s2_6 R37 Rb37 Hb37 H37 E37 vdd vss SLICE
Xbs38 bus1 s2_6 s2_7 R38 Rb38 Hb38 H38 E38 vdd vss SLICE
Xbs39 bus1 s2_7 s2_8 R39 Rb39 Hb39 H39 E39 vdd vss SLICE
Xbs40 bus1 s2_8 s2_9 R40 Rb40 Hb40 H40 E40 vdd vss SLICE
Xbs41 bus1 s2_9 s2_10 R41 Rb41 Hb41 H41 E41 vdd vss SLICE
Xbs42 bus1 s2_10 s2_11 R42 Rb42 Hb42 H42 E42 vdd vss SLICE
Xbs43 bus1 s2_11 s2_12 R43 Rb43 Hb43 H43 E43 vdd vss SLICE
Xbs44 bus1 s2_12 s2_13 R44 Rb44 Hb44 H44 E44 vdd vss SLICE
Xbs45 bus1 s2_13 s2_14 R45 Rb45 Hb45 H45 E45 vdd vss SLICE
Xbs46 bus1 s2_14 s2_15 R46 Rb46 Hb46 H46 E46 vdd vss SLICE
Xbs47 bus1 s2_15 s2_16 R47 Rb47 Hb47 H47 E47 vdd vss SLICE
Xrep3 s2_16 s3_0 en vdd vss REP_RO
Xkp3 s2_16 vdd vss KEEP
Xbs48 bus1 s3_0 s3_1 R48 Rb48 Hb48 H48 E48 vdd vss SLICE
Xbs49 bus1 s3_1 s3_2 R49 Rb49 Hb49 H49 E49 vdd vss SLICE
Xbs50 bus1 s3_2 s3_3 R50 Rb50 Hb50 H50 E50 vdd vss SLICE
Xbs51 bus1 s3_3 s3_4 R51 Rb51 Hb51 H51 E51 vdd vss SLICE
Xbs52 bus1 s3_4 s3_5 R52 Rb52 Hb52 H52 E52 vdd vss SLICE
Xbs53 bus1 s3_5 s3_6 R53 Rb53 Hb53 H53 E53 vdd vss SLICE
Xbs54 bus1 s3_6 s3_7 R54 Rb54 Hb54 H54 E54 vdd vss SLICE
Xbs55 bus1 s3_7 s3_8 R55 Rb55 Hb55 H55 E55 vdd vss SLICE
Xbs56 bus1 s3_8 s3_9 R56 Rb56 Hb56 H56 E56 vdd vss SLICE
Xbs57 bus1 s3_9 s3_10 R57 Rb57 Hb57 H57 E57 vdd vss SLICE
Xbs58 bus1 s3_10 s3_11 R58 Rb58 Hb58 H58 E58 vdd vss SLICE
Xbs59 bus1 s3_11 s3_12 R59 Rb59 Hb59 H59 E59 vdd vss SLICE
Xbs60 bus1 s3_12 s3_13 R60 Rb60 Hb60 H60 E60 vdd vss SLICE
Xbs61 bus1 s3_13 s3_14 R61 Rb61 Hb61 H61 E61 vdd vss SLICE
Xbs62 bus1 s3_14 s3_15 R62 Rb62 Hb62 H62 E62 vdd vss SLICE
Xbs63 bus1 s3_15 s3_16 R63 Rb63 Hb63 H63 E63 vdd vss SLICE
.tran 1p 9.7600e-09
.meas tran treset0 trig v(en) val=0.35 rise=1 td=0.0000e+00 targ v(s3_16) val=0.35 fall=1 td=0.0000e+00
.meas tran tbus0 trig v(R0) val=0.35 rise=1 td=1.2200e-09 targ v(s3_16) val=0.35 rise=1 td=1.2200e-09
.meas tran vE0_0 find v(s0_1) at=2.3900e-09
.meas tran vE1_0 find v(s0_2) at=2.3900e-09
.meas tran vE2_0 find v(s0_3) at=2.3900e-09
.meas tran vE3_0 find v(s0_4) at=2.3900e-09
.meas tran vE4_0 find v(s0_5) at=2.3900e-09
.meas tran vE5_0 find v(s0_6) at=2.3900e-09
.meas tran vE6_0 find v(s0_7) at=2.3900e-09
.meas tran vE7_0 find v(s0_8) at=2.3900e-09
.meas tran vE8_0 find v(s0_9) at=2.3900e-09
.meas tran vE9_0 find v(s0_10) at=2.3900e-09
.meas tran vE10_0 find v(s0_11) at=2.3900e-09
.meas tran vE11_0 find v(s0_12) at=2.3900e-09
.meas tran vE12_0 find v(s0_13) at=2.3900e-09
.meas tran vE13_0 find v(s0_14) at=2.3900e-09
.meas tran vE14_0 find v(s0_15) at=2.3900e-09
.meas tran vE15_0 find v(s0_16) at=2.3900e-09
.meas tran vE16_0 find v(s1_1) at=2.3900e-09
.meas tran vE17_0 find v(s1_2) at=2.3900e-09
.meas tran vE18_0 find v(s1_3) at=2.3900e-09
.meas tran vE19_0 find v(s1_4) at=2.3900e-09
.meas tran vE20_0 find v(s1_5) at=2.3900e-09
.meas tran vE21_0 find v(s1_6) at=2.3900e-09
.meas tran vE22_0 find v(s1_7) at=2.3900e-09
.meas tran vE23_0 find v(s1_8) at=2.3900e-09
.meas tran vE24_0 find v(s1_9) at=2.3900e-09
.meas tran vE25_0 find v(s1_10) at=2.3900e-09
.meas tran vE26_0 find v(s1_11) at=2.3900e-09
.meas tran vE27_0 find v(s1_12) at=2.3900e-09
.meas tran vE28_0 find v(s1_13) at=2.3900e-09
.meas tran vE29_0 find v(s1_14) at=2.3900e-09
.meas tran vE30_0 find v(s1_15) at=2.3900e-09
.meas tran vE31_0 find v(s1_16) at=2.3900e-09
.meas tran vE32_0 find v(s2_1) at=2.3900e-09
.meas tran vE33_0 find v(s2_2) at=2.3900e-09
.meas tran vE34_0 find v(s2_3) at=2.3900e-09
.meas tran vE35_0 find v(s2_4) at=2.3900e-09
.meas tran vE36_0 find v(s2_5) at=2.3900e-09
.meas tran vE37_0 find v(s2_6) at=2.3900e-09
.meas tran vE38_0 find v(s2_7) at=2.3900e-09
.meas tran vE39_0 find v(s2_8) at=2.3900e-09
.meas tran vE40_0 find v(s2_9) at=2.3900e-09
.meas tran vE41_0 find v(s2_10) at=2.3900e-09
.meas tran vE42_0 find v(s2_11) at=2.3900e-09
.meas tran vE43_0 find v(s2_12) at=2.3900e-09
.meas tran vE44_0 find v(s2_13) at=2.3900e-09
.meas tran vE45_0 find v(s2_14) at=2.3900e-09
.meas tran vE46_0 find v(s2_15) at=2.3900e-09
.meas tran vE47_0 find v(s2_16) at=2.3900e-09
.meas tran vE48_0 find v(s3_1) at=2.3900e-09
.meas tran vE49_0 find v(s3_2) at=2.3900e-09
.meas tran vE50_0 find v(s3_3) at=2.3900e-09
.meas tran vE51_0 find v(s3_4) at=2.3900e-09
.meas tran vE52_0 find v(s3_5) at=2.3900e-09
.meas tran vE53_0 find v(s3_6) at=2.3900e-09
.meas tran vE54_0 find v(s3_7) at=2.3900e-09
.meas tran vE55_0 find v(s3_8) at=2.3900e-09
.meas tran vE56_0 find v(s3_9) at=2.3900e-09
.meas tran vE57_0 find v(s3_10) at=2.3900e-09
.meas tran vE58_0 find v(s3_11) at=2.3900e-09
.meas tran vE59_0 find v(s3_12) at=2.3900e-09
.meas tran vE60_0 find v(s3_13) at=2.3900e-09
.meas tran vE61_0 find v(s3_14) at=2.3900e-09
.meas tran vE62_0 find v(s3_15) at=2.3900e-09
.meas tran vE63_0 find v(s3_16) at=2.3900e-09
.meas tran treset1 trig v(en) val=0.35 rise=1 td=4.8800e-09 targ v(s3_16) val=0.35 fall=1 td=4.8800e-09
.meas tran tbus1 trig v(R0) val=0.35 rise=1 td=6.1000e-09 targ v(s3_16) val=0.35 rise=1 td=6.1000e-09
.meas tran vE0_1 find v(s0_1) at=7.2700e-09
.meas tran vE1_1 find v(s0_2) at=7.2700e-09
.meas tran vE2_1 find v(s0_3) at=7.2700e-09
.meas tran vE3_1 find v(s0_4) at=7.2700e-09
.meas tran vE4_1 find v(s0_5) at=7.2700e-09
.meas tran vE5_1 find v(s0_6) at=7.2700e-09
.meas tran vE6_1 find v(s0_7) at=7.2700e-09
.meas tran vE7_1 find v(s0_8) at=7.2700e-09
.meas tran vE8_1 find v(s0_9) at=7.2700e-09
.meas tran vE9_1 find v(s0_10) at=7.2700e-09
.meas tran vE10_1 find v(s0_11) at=7.2700e-09
.meas tran vE11_1 find v(s0_12) at=7.2700e-09
.meas tran vE12_1 find v(s0_13) at=7.2700e-09
.meas tran vE13_1 find v(s0_14) at=7.2700e-09
.meas tran vE14_1 find v(s0_15) at=7.2700e-09
.meas tran vE15_1 find v(s0_16) at=7.2700e-09
.meas tran vE16_1 find v(s1_1) at=7.2700e-09
.meas tran vE17_1 find v(s1_2) at=7.2700e-09
.meas tran vE18_1 find v(s1_3) at=7.2700e-09
.meas tran vE19_1 find v(s1_4) at=7.2700e-09
.meas tran vE20_1 find v(s1_5) at=7.2700e-09
.meas tran vE21_1 find v(s1_6) at=7.2700e-09
.meas tran vE22_1 find v(s1_7) at=7.2700e-09
.meas tran vE23_1 find v(s1_8) at=7.2700e-09
.meas tran vE24_1 find v(s1_9) at=7.2700e-09
.meas tran vE25_1 find v(s1_10) at=7.2700e-09
.meas tran vE26_1 find v(s1_11) at=7.2700e-09
.meas tran vE27_1 find v(s1_12) at=7.2700e-09
.meas tran vE28_1 find v(s1_13) at=7.2700e-09
.meas tran vE29_1 find v(s1_14) at=7.2700e-09
.meas tran vE30_1 find v(s1_15) at=7.2700e-09
.meas tran vE31_1 find v(s1_16) at=7.2700e-09
.meas tran vE32_1 find v(s2_1) at=7.2700e-09
.meas tran vE33_1 find v(s2_2) at=7.2700e-09
.meas tran vE34_1 find v(s2_3) at=7.2700e-09
.meas tran vE35_1 find v(s2_4) at=7.2700e-09
.meas tran vE36_1 find v(s2_5) at=7.2700e-09
.meas tran vE37_1 find v(s2_6) at=7.2700e-09
.meas tran vE38_1 find v(s2_7) at=7.2700e-09
.meas tran vE39_1 find v(s2_8) at=7.2700e-09
.meas tran vE40_1 find v(s2_9) at=7.2700e-09
.meas tran vE41_1 find v(s2_10) at=7.2700e-09
.meas tran vE42_1 find v(s2_11) at=7.2700e-09
.meas tran vE43_1 find v(s2_12) at=7.2700e-09
.meas tran vE44_1 find v(s2_13) at=7.2700e-09
.meas tran vE45_1 find v(s2_14) at=7.2700e-09
.meas tran vE46_1 find v(s2_15) at=7.2700e-09
.meas tran vE47_1 find v(s2_16) at=7.2700e-09
.meas tran vE48_1 find v(s3_1) at=7.2700e-09
.meas tran vE49_1 find v(s3_2) at=7.2700e-09
.meas tran vE50_1 find v(s3_3) at=7.2700e-09
.meas tran vE51_1 find v(s3_4) at=7.2700e-09
.meas tran vE52_1 find v(s3_5) at=7.2700e-09
.meas tran vE53_1 find v(s3_6) at=7.2700e-09
.meas tran vE54_1 find v(s3_7) at=7.2700e-09
.meas tran vE55_1 find v(s3_8) at=7.2700e-09
.meas tran vE56_1 find v(s3_9) at=7.2700e-09
.meas tran vE57_1 find v(s3_10) at=7.2700e-09
.meas tran vE58_1 find v(s3_11) at=7.2700e-09
.meas tran vE59_1 find v(s3_12) at=7.2700e-09
.meas tran vE60_1 find v(s3_13) at=7.2700e-09
.meas tran vE61_1 find v(s3_14) at=7.2700e-09
.meas tran vE62_1 find v(s3_15) at=7.2700e-09
.meas tran vE63_1 find v(s3_16) at=7.2700e-09
.end
