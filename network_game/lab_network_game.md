# The Lewis Signalling Game — Network Experiment

## Overview

In the notebook you trained two agents — a Sender and a Receiver — to play the Lewis game against each other. They converged on a signalling convention.

Now you will connect **your agent to your partner's agent over the network**: one student runs the Sender, the other runs the Receiver. A third script (the game server) acts as the world — generating states and scoring actions.

The central question: **if two agents were each trained in isolation, can they coordinate when they meet for the first time?**

---

## Setup

### Install the MQTT library

```bash
pip install paho-mqtt
```

No account or server is needed. The scripts connect to a free public broker (`broker.hivemq.com`) that relays messages between your machines. Your pair picks a unique **room ID** (e.g. `alice-bob`) so your messages do not mix with other pairs.

### Roles

Each pair needs three terminals (they can be on different computers):

| Terminal | Script | Who runs it |
|----------|--------|-------------|
| Game server | `game_server.py` | one student (or the instructor) |
| Sender | `sender_agent.py` | the Sender student |
| Receiver | `receiver_agent.py` | the Receiver student |

---

## Your Tasks

### Task 0 — Paste your agent code

Open `sender_agent.py` and paste your `Sender` class from the notebook below the marked comment. Do the same for `Receiver` in `receiver_agent.py`.

Make sure the classes have these methods:
- `Sender`: `send_message(state) → int`, `learn_from_feedback(reward)`
- `Receiver`: `act(message) → int`, `learn_from_feedback(reward)`

### Task 1 — Initialise the agent

In each script, replace `self.agent = None` with a real instance:

```python
# sender_agent.py
self.agent = Sender(N_STATES, N_MESSAGES)

# receiver_agent.py
self.agent = Receiver(N_MESSAGES, N_STATES)
```

### Task 2 — Implement `choose_signal` / `choose_action`

Wire your agent's policy to the network. In `sender_agent.py`:

```python
def choose_signal(self, state: int) -> int:
    return self.agent.send_message(state)
```

In `receiver_agent.py`:

```python
def choose_action(self, signal: int) -> int:
    return self.agent.act(signal)
```

### Task 3 — Implement `learn`

Call the agent's learning method after each round. In both scripts:

```python
def learn(self, ..., reward: int) -> None:
    self.agent.learn_from_feedback(reward)
```

### Task 4 (optional) — Start from a pre-trained convention

You can save your notebook agent's weights and load them here, so the network agent starts from the convention it already learned rather than from scratch. In the notebook:

```python
np.save("sender_weights.npy",   sender.message_weights)
np.save("receiver_weights.npy", receiver.action_weights)
```

Then fill in `load_weights` in the agent script:

```python
def load_weights(self, path: str) -> None:
    self.agent.message_weights = np.load(path)   # sender
    # self.agent.action_weights = np.load(path)  # receiver
```

And uncomment the call in `__main__`.

---

## Running the experiment

### Experiment A — Agents trained in isolation (no pre-trained weights)

Start all three scripts with the **same room ID**. Start the game server last (it waits 3 seconds for agents to connect).

```bash
# Terminal 1 (Sender student's machine)
python sender_agent.py

# Terminal 2 (Receiver student's machine)
python receiver_agent.py

# Terminal 3 (game server — any machine)
python game_server.py
```

Play 50 rounds. Copy the printed reward log to a text file.

### Experiment B — Agents starting from pre-trained weights (Task 4)

Save your notebook weights, implement `load_weights`, and repeat the experiment. Does coordination happen faster when agents bring an existing convention?

---

## Analysis

Plot the learning curve for each experiment. Load the reward history (copy it from the terminal output, or add `self.reward_history` logging to the scripts) and plot a rolling average.

**Questions to answer:**

1. **Experiment A — cold start.** Did the two naive agents coordinate? How many rounds did it take before accuracy reliably exceeded 0.5? Why does coordination fail at first even though each agent learned successfully in the notebook?

2. **Experiment B — warm start.** Did pre-trained weights help or hurt? What happens when two agents that trained on *different* arbitrary conventions meet?

3. **Symmetry breaking.** Look at the final signalling system. Which agent had to "give up" its old convention and adopt the other's? Or did they meet in the middle with a new one?

4. **Implications for language.** In human language, new speakers do not start from scratch — they are immersed in an existing community with an established convention. How does this change the coordination problem compared to what you observed in Experiment A?
