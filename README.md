# ParkUT Senior Project

## The Problem:
- Parking lots are an inefficient and unaesthetic land use in an urban environment.
- As a university grows in size or prestige, parking lots can be replaced with buildings, green space, or other infrastructure.
- Extra time and emissions spent looking for a parking space have implications for both the individual and the environment.

![image](https://github.com/nathanielgreenna/ParkUTSeniorProject/assets/61034629/742c72b1-5978-4561-be25-6aa6f0d0c4b0)

### From Strong Towns, an urban planning non-profit: 
> “Ann Arbor, home to the University of Michigan, eliminated its parking minimums citywide … Council member Erica Briggs told WEMU that the move should allow new housing and commercial space to be more affordable, and, by filling in lightly used parking lots and reducing asphalt, it will make the city more walkable and environmentally sound.”

How do we make parking easier to find on campus, and therefore enable universities to reclaim some of their valuable land from parking lots without inconveniencing users?

## Our solution
- An app that shows you which parking lots will likely be available when you arrive.
- Many ways of collecting the necessary data were considered, from cameras at the entrance/exit points of lots to small IoT devices embedded in each parking space.
- Eventually, we settled on a camera with a good view of an entire parking lot to track occupancy statistics using computer vision.

![image](https://github.com/nathanielgreenna/ParkUTSeniorProject/assets/61034629/60080f86-9feb-4ae1-935f-080635851e4f)

## Design
our design contained four separate components:

### Camera / Pi
The data flow begins with a camera and Raspberry Pi which captures and processes occupancy data over a representative set of parking spaces. Processing at the source allows us to transmit less data over the air, which is an advantage as our units often had tenuous connections. The Pi was scheduled to run our CV algorithm every minute, though this could be raised or lowered arbitrarily. The setup below was achieved with help from UT Facilities- the Pi and camera are inside the small black box and overlook a parking lot.

![image](https://github.com/nathanielgreenna/ParkUTSeniorProject/assets/61034629/a4963918-36ef-4195-8f81-8867fc50e637)

### CV Algorithm
Our CV algorithm runs at an interval and updates our database with its detected occupancy. This CV algorithm determines the occupancy of each parking space separately, and sends the total to the database. This algorithm was implemented in Python using OpenCV, and includes uses Gaussian blur before applying an adaptive threshold and dilation to determine spot occupancy. The CV algorithm and its testing data can be found [here](./ParkingCV).

![image](https://github.com/nathanielgreenna/ParkUTSeniorProject/assets/61034629/de694694-961a-42b2-8eda-2ee4f8ece081)
![image](https://github.com/nathanielgreenna/ParkUTSeniorProject/assets/61034629/ed952b4c-d268-43af-802a-302c41bf8505)


### Database
Each document contains coordinates for the lot, capacity and occupancy data, and other important information, but most of the storage space is taken up by historical data, which stores historical data for each lot, each day of the week, every fifteen minutes. A suite of backend tools were also developed in Google Colaboratory in order to simplify adding new lots, closing or re-opening lots, and even creating simulation data for our frontend. These backend tools can be found [here](./BackendTools.ipynb). 

![image](https://github.com/nathanielgreenna/ParkUTSeniorProject/assets/61034629/2bf120a4-22a1-499b-bbff-0e73f8ae0378)

### Web/Mobile App
Our web and mobile serves the user with an organization's parking lot occupancy. For our frontend, we used Flutter, since it has good integration with the Google Maps API, which we used to display our parking data, both current and a prediction for an hour in the future, to the user, as well as valid permits for each lot. This data is displayed using pins on the map- when users tap or click a parking lot pin, we display the data, as well as displaying it on a carousel toward the top of the app. Users can then use a button to be shown a route to their selected lot in Google Maps. The mobile app can be found [here](./Mobile%20App).

![image](https://github.com/nathanielgreenna/ParkUTSeniorProject/assets/61034629/fb2e8140-e831-418a-b9bf-30c8d28e712b)

