Install steps on ubuntu (TESTED Ubuntu 14.04):
	aptitude update
	aptitude install build-essential python2.7 python-pip python-dev libevent-dev python-matplotlib
	pip install scoop
	pip install numpy


This folder contains:
- chef.xml -> SPLA input model with chef example.
- costs.txt -> Cost table input.

- fsm.py -> SPLAcris state machine generator.
	This FSM script supports SCOOP to be computed in a distributed system
	This will run using 1 worker
    usage: sudo python -m scoop -n 1 fsm.py <input.xml> <costs.txt> 1
	This will run using 4 workers
    usage: sudo python -m scoop -n 4 fsm.py <input.xml> <costs.txt> 4
	This will run using 6 workers
    usage: sudo python -m scoop -n 6 fsm.py <input.xml> <costs.txt> 6 

To run this multiple times with different workers do this
This example will run with:
1,2,4,8,16 and 32 workers
using: term.xml as the XML input file
using: costs.txt as the cost input function

The default example
for((i=1;i<=32;i*=2)); do sudo python -m scoop -n $i fsm.py term.xml costs.txt $i; done

The chef example
for((i=1;i<=32;i*=2)); do sudo python -m scoop -n $i fsm.py chef.xml costs.txt $i; done


The output of the script will be:
output.txt
This file will content this information:
		The numbers of workers
		The total of products
		The total execution time
		The average product computing time

.eps graphic with the cumulative execution time
	This eps file will be named as:
	<term_file_name>_<cost_file_name>_<workers>.eps
  
    
- README.txt -> This file. :)
- splacris.py -> SPLAcris class.
- tester.py -> Class calls to test methods (All).
    usage: tester.py <input.xml> <costs.txt>
- term.xml -> SPLA input example.
- tests.xml -> Tested xml models.
- pdf/api.pdf -> Contains the API description.