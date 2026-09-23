.SUBCKT CCSA_BITSLICE bus1 bus2_up bus2_dn R Rbar Lambdabar Lambda E vdd vss
XVSW bus1 bus2_dn R Rbar vdd vss CCSA_VSW
XHSW bus2_up bus2_dn Lambdabar Lambda vdd vss CCSA_HSW
XRCV bus2_dn E vdd vss CCSA_RECEIVER
XPD bus2_dn vdd vss CCSA_PULLDOWN
XKP bus2_dn vdd vss CCSA_KEEPER
.ENDS CCSA_BITSLICEbar L15bar L15 E15 vdd vss CCSA_BITSLICE
.ENDS CCSA_SEGMENT_K16
