# Steak Co. by KungFuPandaSquad
## Roster
* Alex Luo - PM, flask routing, front end framework, db creation, will help with games 
* Evan Chan - API handling and styling
* Leon Huang - Implementing games and will help with db creation 
* Stanley Hoo - HTML Templates and styling

## App Description
Our website will be an online gaming site where users can:
 * Acquire and use a universal virtual currency 
 * Play games including 
    * Plinko: Users drop a chip, and it lands in a slot that either awards or decrements currency 
    * Poker: Texas Hold’em and Chinese Poker (Rules will be incorporated on the site)
    * Blackjack: Users try to get closer to 21, but not exceed it

We aim to create an engaging experience that utilizes Flask, a simple user account system, Bootstrap for our front end framework, and RESTful APIS. 

# Install Guide

**Prerequisites**

Ensure that **Git** and **Python** are installed on your machine. It is recommended that you use a virtual machine when running this project to avoid any possible conflicts. For help, refer to the following documentation:
   1. Installing Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git 
   2. Installing Python: https://www.python.org/downloads/ 

   3. (Optional) Setting up Git with SSH (Ms. Novillo's APCSA Guide): https://novillo-cs.github.io/apcsa/tools/ 
         

**Cloning the Project**
1. Create Python virtual environment:

```
$ python3 -m PATH/TO/venv_name
```

2. Activate virtual environment 

   - Linux: `$ . PATH/TO/venv_name/bin/activate`
   - Windows (PowerShell): `> . .\PATH\TO\venv_name\Scripts\activate`
   - Windows (Command Prompt): `>PATH\TO\venv_name\Scripts\activate`
   - macOS: `$ source PATH/TO/venv_name/bin/activate`

   *Notes*

   - If successful, command line will display name of virtual environment: `(venv_name) $ `

   - To close a virtual environment, simply type `$ deactivate` in the terminal


3. In terminal, clone the repository to your local machine: 

HTTPS METHOD (Recommended)

```
$ git clone https://github.com/aluo50/KungFuPandaSquad__alexl175_evanc107_leonh15_stanleyh28.git     
```

SSH METHOD (Requires SSH Key to be set up):

```
$ git clone git@github.com:aluo50/KungFuPandaSquad__alexl175_evanc107_leonh15_stanleyh28.git
```

4. Navigate to project directory

```
$ cd PATH/TO/KungFuPandaSquad__alexl175_evanc107_leonh15_stanleyh28/
```

5. Install dependencies

```
$ pip install -r requirements.txt
```
        
# Launch Codes

1. Navigate to project directory:

```
$ cd PATH/TO/KungFuPandaSquad__alexl175_evanc107_leonh15_stanleyh28/
```
 
2. Navigate to 'app' directory

```
 $ cd app/
```

3. Run App

```
 $ python3 __init__.py
```
4. Open the link that appears in the terminal to be brought to the website
    - You can visit the link via several methods:
        - Control + Clicking on the link
        - Typing/Pasting http://127.0.0.1:5000 in any browser
    - To close the app, press control + C when in the terminal

```    
* Running on http://127.0.0.1:5000
``` 

# NO API KEYS NEEDED
