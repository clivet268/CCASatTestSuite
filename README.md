## CCASatTestSuite


The test suite for the conditions evaluated in the satellite congestion control algorithms MQP at WPI


***
#### Security notes

In order to achive the ssh automation that is used in this test suite, test devices should have **minimal or no outside access**, and ideally a firewall that only permits communication accross test systems and their ips. Having as much of the hardware be your own, so the test systems and routers between them, will minimize security issues as well as provide a more controllable test environment and cleaner results. For sender and reciever systems this is especially important, for the trigger system less so as it does not require auto ssh into it to perform tests.

***

#### Setting up a sender system:

Git clone this repo into the home dir of the user you will be using

To install the kernel version needed for the kernel logging modules run the below script. It will install all dependencies, build the kernel and then reboot on its own. 

> ./kernelsetup.sh

On next reboot you will need to select the new kernel in the gnome menu or for convenience change the default kernel. See https://unix.stackexchange.com/questions/198003/set-the-default-kernel-in-grub

then run the below to ensure you have everything needed for other scripts used in the test suite

> ./dependencies.sh

After that run the below script to make the kernel logging modules, note that if any kernel module is installed a restart will likely be required before an updated version can be installed.

> ./makemodules.sh

...set up auto ssh...


***

#### Setting up a reciever system:

Git clone this repo into the home dir of the user you will be using

...set up auto ssh...





***


#### Setting up auto ssh:

Sudo permissions: sudo timestamp durations should be set to be as long as a round of your tests will need. This can be less secure but assuming you control your test environment, is acceptable. 

SSH keys: your sender and reciever systems will need to have 

***


triggerremotetests.sh :

-a [default cubic_hspp] :

the name of the CA that appears in your sender's kernelmodules folder.
(should be .../CCASatTestSuite/kernelmodules/[CA name]/[CA name].ko)
-i [run id name]

The name for this run, will put the test results in .../CCASatTestSuite/kernelmodules/[run id name]/
rather than .../CCASatTestSuite/kernelmodules/noid/
-n [default 1] :

number of runs to do per test **\***

* -t [default 10] : 

Seconds to run test for, will override any size settings

* -x [default 0.0.0.0]
* -y [default 0.0.0.0]

The sender/receiver ip address to bind to to use as your sender ip, useful for when you have multiple network interfaces
${finalrange} -s ${senderip}${recieverbind}${finalextract} >> /home/${recieveruser}/CCASatTestSuite/reciever.out 2>&1 < /dev/null & exit"'


TODO:
Fix ~0 in framework output for a few values sometimes
Fix apparent control flow in logs
Generate comparison graphs
Shared graphing states for graphing to aid in adding more algos
