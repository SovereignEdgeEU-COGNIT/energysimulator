Workload  Avg.Power [W]  Duration [s]  Deadline [s]   
1         100            100           60       
2         23             200           100           
3         26             30            10
4         300            300           200


Start:

Edge cluster  GPUs  CO2.Intensity
A             2     10
B             6     100


-> 1:A Emission 100 * 100 * 10 = 100000 CO2

Edge cluster  GPUs  CO2.Intensity
A             1     10
B             6     100

-> 1:A
-> 2:A
-> 3:B
-> 4:B

-> 1:B
-> 
