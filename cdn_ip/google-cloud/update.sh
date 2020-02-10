myarray=()
for LINE in `dig txt _cloud-netblocks.googleusercontent.com +short | tr " " "\n" | grep include | cut -f 2 -d :`
do
	myarray+=($LINE)
	for LINE2 in `dig txt $LINE +short | tr " " "\n" | grep include | cut -f 2 -d :`
	do
		myarray+=($LINE2)
	done
done 

for LINE in ${myarray[@]}
do
	dig txt $LINE +short | tr " " "\n" 
done | grep ip4 | cut -f 2 -d : | sort -n +0 +1 +2 +3 -t .
