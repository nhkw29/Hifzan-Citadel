import gymnasium as gym
from gymnasium import spaces
import numpy as np 
import random

from environment.orderbook import OrderBook, Order, Tape
from environment.agents import KyleNoiseTrader, InventoryMarketMaker

class MarketEnvironment(gym.Env):
    def __init__(self):
        super(MarketEnvironment, self).__init__()
        
        self.action_space = spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32)

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float32)

        # Internal State
        self.order_book = None
        self.agents = []
        self.clock = 0
        self.max_steps = 1000
        
        self.insider_inventory = 0
        self.cash_balance = 100000
        self.tape_reader_index=0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.clock = 0
        self.order_book = OrderBook()
        self.insider_inventory = 0
        self.cash_balance = 100000
        self.agents = []

        # 1. Spawn Agents
        # 5 Market Makers (Providers)
        for i in range(5): 
            self.agents.append(InventoryMarketMaker(f"MM_{i}"))
        # 10 Noise Traders (Consumers)
        for i in range(10): 
            self.agents.append(KyleNoiseTrader(f"NT_{i}", sigma_n=3.0))
            
        # 2. Warm-up Period (Build Initial Liquidity)
        # Run 20 steps to fill the book before the RL agent starts
        for _ in range(20):
            self._background_agent_step()

        self.tape_reader_index=len(self.order_book.tape.trades)
        return self._get_obs(), {}

    def step(self, action):
        self.clock += 1
        
        side_val, agg_val, qty_val = action
        
        side = 'buy' if side_val > 0 else 'sell'
        qty = int((qty_val + 1) / 2 * 100) # Scale to 0-50 shares
        
        if qty > 0:
            snap = self.order_book.get_snapshot()
            mid = snap['mid_price']
            
            offset = agg_val * 2.0 # +/- $2.00 range
            if side == 'buy': price = mid + offset
            else: price = mid - offset
            
            self.order_book.add_order(Order("Insider", side, price, qty))
        
        self._background_agent_step()

        current_tape=self.order_book.tape.trades
        current_tape_length=len(current_tape)

        for i in range(self.tape_reader_index,current_tape_length):
            trade=current_tape[i]
            if trade['buyer'] == "Insider":
                self.insider_inventory += trade['qty']
                self.cash_balance -= trade['qty'] * trade['price']
            elif trade['seller'] == "Insider":
                self.insider_inventory -= trade['qty']
                self.cash_balance += trade['qty'] * trade['price']
        
        self.tape_reader_index=current_tape_length
        
        current_mid = self.order_book.get_snapshot()['mid_price']
        portfolio_value = self.cash_balance + (self.insider_inventory * current_mid)

        reward = (portfolio_value - 100000) / 100 # Scaled Reward

        terminated = self.cash_balance<=0
        truncated = self.clock >= self.max_steps
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        snap = self.order_book.get_snapshot()
        return np.array([
            snap['best_bid'],
            snap['best_ask'],
            snap['mid_price'],
            snap['spread'],
            self.insider_inventory,
            self.cash_balance
        ], dtype=np.float32)

    def _background_agent_step(self):
        random.shuffle(self.agents) # Shuffle to prevent order bias
        snap = self.order_book.get_snapshot()
        for agent in self.agents:
            agent.act(snap, self.order_book)