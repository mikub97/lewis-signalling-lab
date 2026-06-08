"""
Integration test — runs GameServer, NetworkSender, NetworkReceiver in threads
within a single process, using a unique test room ID to avoid collisions.
Plays 10 rounds and asserts that both agents received rewards.
"""

import json
import sys
import threading
import time
import numpy as np
import paho.mqtt.client as mqtt

sys.path.insert(0, ".")

# ── Paste agent classes inline (as students would) ────────────────────────────

rng = np.random.default_rng(0)

class Sender:
    def __init__(self, n_states, n_messages, eps=1e-6):
        self.n_messages = n_messages
        self.message_weights = np.full((n_states, n_messages), eps)
        self._last = (0, 0)

    def send_message(self, state):
        w = self.message_weights[state]
        w = w - w.max()
        probs = np.exp(w) / np.exp(w).sum()
        message = int(rng.choice(self.n_messages, p=probs))
        self._last = (state, message)
        return message

    def learn_from_feedback(self, reward):
        self.message_weights[self._last] += reward


class Receiver:
    def __init__(self, n_messages, n_actions, eps=1e-6):
        self.n_actions = n_actions
        self.action_weights = np.full((n_messages, n_actions), eps)
        self._last = (0, 0)

    def act(self, message):
        w = self.action_weights[message]
        w = w - w.max()
        probs = np.exp(w) / np.exp(w).sum()
        action = int(rng.choice(self.n_actions, p=probs))
        self._last = (message, action)
        return action

    def learn_from_feedback(self, reward):
        self.action_weights[self._last] += reward


# ── Import the scaffolded classes ─────────────────────────────────────────────

from game_server import GameServer
from signalling.network_game._sender_agent_solved import NetworkSender
from signalling.network_game._receiver_agent_solved import NetworkReceiver

# ── Patch the task methods (simulating a completed student submission) ─────────

ROOM = f"test-{int(time.time())}"
N_ROUNDS_TEST = 10

# Override N_ROUNDS in GameServer for the test
import game_server as gs_mod
gs_mod.N_ROUNDS = N_ROUNDS_TEST
gs_mod.STARTUP_DELAY = 2
gs_mod.ROUND_DELAY = 0.1

def make_sender():
    s = NetworkSender.__new__(NetworkSender)
    s.room_id = ROOM
    s.t = {
        "state":  f"lewis/{ROOM}/state",
        "signal": f"lewis/{ROOM}/signal",
        "reward": f"lewis/{ROOM}/reward",
    }
    s.agent = Sender(4, 4)
    s._last_state  = None
    s._last_signal = None
    s.reward_history = []
    s.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    s.client.on_connect = s._on_connect
    s.client.on_message  = s._on_message

    def choose_signal(state):
        return s.agent.send_message(state)
    def learn(state, signal, reward):
        s.agent.learn_from_feedback(reward)

    s.choose_signal = choose_signal
    s.learn = learn
    return s


def make_receiver():
    r = NetworkReceiver.__new__(NetworkReceiver)
    r.room_id = ROOM
    r.t = {
        "signal": f"lewis/{ROOM}/signal",
        "action": f"lewis/{ROOM}/action",
        "reward": f"lewis/{ROOM}/reward",
    }
    r.agent = Receiver(4, 4)
    r._last_signal = None
    r._last_action = None
    r._last_round  = None
    r.reward_history = []
    r.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    r.client.on_connect = r._on_connect
    r.client.on_message  = r._on_message

    def choose_action(signal):
        return r.agent.act(signal)
    def learn(signal, action, reward):
        r.agent.learn_from_feedback(reward)

    r.choose_action = choose_action
    r.learn = learn
    return r


# ── Run ───────────────────────────────────────────────────────────────────────

sender   = make_sender()
receiver = make_receiver()
server   = GameServer(ROOM)

errors = []

def run_sender():
    try:
        sender.client.connect(gs_mod.BROKER, gs_mod.PORT)
        sender.client.loop_forever()
    except Exception as e:
        errors.append(f"sender: {e}")

def run_receiver():
    try:
        receiver.client.connect(gs_mod.BROKER, gs_mod.PORT)
        receiver.client.loop_forever()
    except Exception as e:
        errors.append(f"receiver: {e}")

def run_server():
    try:
        server.run()
    except Exception as e:
        errors.append(f"server: {e}")
    finally:
        sender.client.disconnect()
        receiver.client.disconnect()

t_sender   = threading.Thread(target=run_sender,   daemon=True)
t_receiver = threading.Thread(target=run_receiver, daemon=True)
t_server   = threading.Thread(target=run_server,   daemon=True)

print(f"\nStarting integration test (room={ROOM}, {N_ROUNDS_TEST} rounds) …\n")

t_sender.start()
t_receiver.start()
time.sleep(0.5)
t_server.start()

t_server.join(timeout=60)

# ── Assert ────────────────────────────────────────────────────────────────────

print("\n─── Test results ────────────────────────────────────")

if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)

assert len(sender.reward_history)   > 0, "Sender received no rewards"
assert len(receiver.reward_history) > 0, "Receiver received no rewards"
assert len(sender.reward_history)   == len(receiver.reward_history), \
    f"Reward count mismatch: sender={len(sender.reward_history)} receiver={len(receiver.reward_history)}"

n = len(sender.reward_history)
total = sum(sender.reward_history)
print(f"  Rounds completed : {n}")
print(f"  Total reward     : {total} / {n}")
print(f"  Accuracy         : {total/n:.1%}")
print(f"  Sender weights   : OK (shape {sender.agent.message_weights.shape})")
print(f"  Receiver weights : OK (shape {receiver.agent.action_weights.shape})")
print("\n  ALL ASSERTIONS PASSED")
