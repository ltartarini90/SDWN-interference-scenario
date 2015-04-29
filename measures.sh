#!/bin/bash

i=0.54
counter=0
while [ $counter -le 46 ] 
do 
	python ./interference.py --udp --distance=$i
	#echo "$i"
	counter=$(( $counter + 1 ))
	i=$(echo $i + 0.01 | bc -l | sed -e 's/^\./0./' -e 's/^-\./-0./')
done
	
