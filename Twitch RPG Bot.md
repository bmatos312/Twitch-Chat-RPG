Welcome to the Twitch RPG Bot! This is a Twitch chat-based RPG game that allows players to register, fight monsters, earn gold, and buy buffs from a shop. The game is inspired by Dune themes, with various mobs, items, and abilities reflecting the Dune universe.

**Table of Contents**
*  Features
*  Getting Started
*  Commands
*  Shop Buffs
*  Gold Accumulation
*  Setting Up
*  Contributing
**Features:**
  Player Registration: Players can register and choose a class.
  Fight Bosses: Fight Dune-themed bosses and earn gold and items.
  Shop Buffs: Spend gold on buffs that enhance your performance.
  Gold Accumulation: Players accumulate gold automatically based on their level.
  Dune-Themed Content: Items, mobs, and buffs inspired by the Dune universe.
**Getting Started:**
Prerequisites
Before you begin, ensure you have the following software installed:

Python 3.8+
pip (Python package installer)
A Twitch account and OAuth token for the bot
Installation
Clone the repository:

git clone https://github.com/YOUR-GITHUB-USERNAME/Twitch-Chat-RPG.git
cd Twitch-Chat-RPG

**Optional but recommended:**

python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

**Install Dependencies:**

pip install -r requirements.txt

**Configure the bot:**

Update the bot_script.py file with your Twitch bot credentials (OAuth token, client ID, etc.).
Update the app/game_logic.py file with your database connection settings.

**To run the bot:**

python3 bot_script.py

**Player Commands:**
  
  !register: Registers a new player.
  !chooseclass <ClassName>: Choose a class for your character after registering. Available classes: Warrior, Archer, Mage.
  !attack: Fight the current boss.
  !gold: Check your current gold balance.
  !shop: View available buffs in the shop.
  !buy <BuffName>: Purchase a buff from the shop.

**Shop Buffs:**

  Health Buff: Increases your health.
  DPS Buff: Increases your damage per second.
  Steal Buff: Gives you a chance to steal a percentage of gold from another player.

**Gold Accumulation:**

  Players automatically accumulate gold based on their level. The higher your level, the more gold you accumulate over time.

**Database Setup:**
  I used mysql but its preferable to your choice.

  **Create a MySQL database:**
  CREATE DATABASE rpg_data;

  **Create necessary tables:**
  CREATE TABLE TwitchUser (
    id INT PRIMARY KEY AUTO_INCREMENT,
    twitch_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL
);

CREATE TABLE PlayerClass (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Player (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    twitch_user_id INT,
    class_id INT,
    gold INT DEFAULT 0,
    level INT DEFAULT 1,
    FOREIGN KEY (twitch_user_id) REFERENCES TwitchUser(id),
    FOREIGN KEY (class_id) REFERENCES PlayerClass(id)
);

CREATE TABLE Item (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT,
    item_id INT,
    quantity INT DEFAULT 1,
    FOREIGN KEY (player_id) REFERENCES Player(id),
    FOREIGN KEY (item_id) REFERENCES Item(id)
);

CREATE TABLE Mob (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    health INT,
    attack INT,
    defense INT,
    health_scaling INT,
    attack_scaling INT,
    defense_scaling INT
);

**Update your connection settings in app/game_logic.py:**
  def get_db_connection():
      connection = pymysql.connect(
          host='localhost',
          user='YOUR_DB_USERNAME',
          password='YOUR_DB_PASSWORD',
          db='rpg_data',
          cursorclass=pymysql.cursors.DictCursor
      )
      return connection

**Contributing:**
  Contributions are welcome! If you have ideas for features, optimizations, or improvements, feel free to submit a pull request.
