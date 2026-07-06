Period, NotPeriod, StartXfee, EndXFee, StartPark, EndPark  = map(int, input(" ").split())
total = 0
hours = EndPark - StartPark
for i in range(StartPark, EndPark, 1):
    if(i >= StartXfee and i < EndXFee):
        total += Period 
        hours -= 1
while(hours > 0):
    total += NotPeriod 
    hours -= 1
print(total)

