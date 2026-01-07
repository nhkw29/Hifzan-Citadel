Here is the `README.md` rewritten to look like it was done by a complete beginner. I’ve used simpler language, less perfect formatting, and added some honest comments about the difficulty level.

```markdown
# My Project - Citadel Bootcamp

I finished Week 0 and Week 1. I could not complete week 2.

## Week 0 - Python Basics
I started with the python stuff. I had to load some data and make graphs.

* **AAPL Analysis:** I loaded the `AAPL.csv` file using pandas.
* **Graphs:** I made a plot of the closing price and added a 20-day average line (SMA). It looks pretty cool.
* **Math:** I read about the math stuff (Expectation and Variance) and the random walk stuff for stock prices. [cite_start]The Z-score part explains how far data is from the average[cite: 593].

## Week 1 - The Simulator
This week was way harder. I had to build a "Limit Order Book" from scratch.

### What's in the code:
* **order_book.py:** This is the main code. It creates orders and matches them.
* [cite_start]**Sorting:** I used `bisect` to keep the lists sorted because the instructions said it's faster than normal sorting[cite: 63, 66].
* **Matching:** It does the matching where the best price wins. [cite_start]If prices are the same, the older one wins (Price-Time Priority)[cite: 32].
* **Simulation:** The script runs a loop with 15 limit orders and then 10 market orders to show it working.

### Files included:
1.  `order_book.py` - Run this to see the trades happen.
2.  `architecture_diagram.txt` - I drew how the agents talk to the order book.

## How to run it
Just open the folder and type:
`python order_book.py`

You should see a table printed out with Bids and Asks and then some trades happening.

```
