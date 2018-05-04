# Remote-Fill-Control

Used for University of Washington's Society of Advanced Propulsion

## Version 3
- Changed from command line input to also incorporate switch input, as shown here.
- Modified GUI and improved multithreading.
- Final and tested. V3 is safe for rocket launch.
![](https://github.com/axemaneric/Remote-Fill-Control/blob/master/Images/IMG_9114.HEIC)

## Version 2
- Added GUI and partially functional data logging to csv. Uses potentially unsafe multithreading.

## Version 1
remotefill.py will be used with a Raspberry PI 3 situated on ground control to control the fill procedure of the rocket.

Current menu commands:
- v : show valve names
- open 'valve name': opens valve
- close 'valve name': closes valve
- status: show valves status
- menu: show all commands
- quit: exit program

## PROJECT CHARTER
AVIONICS – REMOTE FILL

## PURPOSE
### What does this part do? What are the roles of this part? High level detail of its components.
-	Develop the control scheme for remote fill procedures
-	Receive command from ground station to open nitrous oxide valves and vent valves
-	Send sensor data prevalent to fill
## SCOPE
### How does this project interact with other team projects? What level of integration is required?
-	Requires integration with ground station and other avionics teams with wireless communications to develop standard procedures
-	Some hardware will be chosen by the propulsion team with consideration to their mass flow requirements and space requirements
## PROJECT HISTORY
### How has this part been designed in the past? Did that work well?
-	Remote fill was introduced last year with a wire connection to send commands
-	Project was entirely within propulsion subteam
-	Had no graphic interface/used buttons
-	Sensors were a separate project that used optical infrared
-	The method was not as accurate as desired and had issues sending consistent signals
## REQUIREMENTS / RESTRICTIONS / RISK
### What happens if this part does not work? How will this affect the system it is a part of and the rocket? Are there any immediate restrictions or requirements? Is there anything that needs to be considered?
-	Remote fill is mission critical
## OBJECTVE
### When is this project defined as done? What are the deliverables? What level of testing is required?
-	Transmissions must broadcast over 5000 ft for the distance between ground control and launch rail
-	System will be tested with the propulsion system at static fires
## DESIGN STANDING
Rank 1-3. 1 is a totally new project, requires completely new design.
3 is something that needs minimal revisions.
-	Ranks 2: Add wireless communications
## RESOURCES
### Is there any documentation or CAD models for the member to reference?
-	Sabrina developed the electronics used for this system last year.
-	Resources have been added to the drive
