
# Updating the TOPCAT repository

* Take a look at the code, example, and instructions directories to form a picture of the current state

* As a first step, identify anything that is user-specific that needs to be changed if other people are going to use the repo, e.g. hard-wired directories. Fix that so they're no longer hard-wired. I still do want to be able to run this locally so if necessary create a README.local.md with information on how to do so.

* Pretend to be a fresh new user for the package. We are going to simulate the process, including creating a completely new environment.  At the end when we're sure it works we're going to delete the environment. During the simulation process I want to see exactly what commands the user would be running on the commandline and I want to be asked if I want to proceed for each one. Other notes:
  - Conda is already installed (locally I have: conda:   aliased to source /opt/anaconda3/etc/profile.d/conda.csh).
  - If there is anything you're uncertain of, ASK. Don't just proceed.
  
  
