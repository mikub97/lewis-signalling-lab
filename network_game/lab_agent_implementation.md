# Implementing the Network Agent

## What you are building

You will implement two Python classes — `Sender` and `Receiver` — and connect them to a live game running on a remote server. Your agent will play the Lewis Signalling Game against your partner's agent over the internet.

Each class is a **Roth–Erev reinforcement learner**: it maintains a weight matrix and updates it based on reward signals received after each round.

---

## How the network protocol works

Three scripts run simultaneously, connected through a public MQTT message broker:

```
  game_server.py          sender_agent.py        receiver_agent.py
  ─────────────           ───────────────        ──────────────────
  publishes state    →    receives state
                          picks message
                          publishes message  →    receives message
                                                  picks action
                                                  publishes action
  receives action
  computes reward
  publishes reward   →    receives reward    →    receives reward
                          calls learn()           calls learn()
                          ↓                       ↓
                    (repeat for next round)
```

All messages are JSON. Each message carries a `"round"` field so agents can match rewards to the correct round.

You do not need to modify the network code. Your job is to implement the agent logic inside the marked tasks.

---

## Task 0 — Implement the agent classes

Implement `Sender` and `Receiver` at the top of their respective scripts.

**Do not copy from the notebook.** You have already studied how these agents work — implement them from your understanding. If you get stuck, re-read the Roth–Erev section of the notebook before looking at the solution.

### Sender

The `Sender` maps world states to messages.

- Maintains a weight matrix `W` of shape `(n_states, n_messages)`, initialised to a small constant `eps`.
- `send_message(state)`: applies **row-wise softmax** to row `state` of `W` to get a probability distribution, then **samples** a message from it. Stores `(state, message)` for learning.
- `learn_from_feedback(reward)`: adds `reward` to `W[state, message]` for the pair chosen in the last round.

### Receiver

The `Receiver` maps messages to actions.

- Maintains a weight matrix `W` of shape `(n_messages, n_actions)`, initialised to `eps`.
- `act(message)`: applies **row-wise softmax** to row `message` of `W`, samples an action. Stores `(message, action)`.
- `learn_from_feedback(reward)`: adds `reward` to `W[message, action]`.

### Numerical tip

Before computing `exp(W[i])`, subtract the row maximum for numerical stability:

```python
w = W[i] - W[i].max()
probs = np.exp(w) / np.exp(w).sum()
```

---

## Task 1 — Initialise the agent

In `NetworkSender.__init__`, replace:

```python
self.agent = None
```

with a real `Sender` instance:

```python
self.agent = Sender(N_STATES, N_MESSAGES)
```

Do the same in `NetworkReceiver.__init__` with `Receiver(N_MESSAGES, N_STATES)`.

---

## Task 2 — Connect the policy to the network

When the network layer receives a state (or message), it calls `choose_signal` (or `choose_action`). Wire this to your agent:

**sender_agent.py:**
```python
def choose_signal(self, state: int) -> int:
    return self.agent.send_message(state)
```

**receiver_agent.py:**
```python
def choose_action(self, signal: int) -> int:
    return self.agent.act(signal)
```

---

## Task 3 — Connect learning to the network

After each round the network layer receives the reward and calls `learn`. Update the agent's weights:

**Both scripts:**
```python
def learn(self, ..., reward: int) -> None:
    self.agent.learn_from_feedback(reward)
```

---

## Task 4 (optional) — Load pre-trained weights

If you want your agent to start from the convention it learned in the notebook rather than from scratch, save the weights at the end of notebook training:

```python
# In the notebook, after the training loop:
np.save("sender_weights.npy",   sender.message_weights)
np.save("receiver_weights.npy", receiver.action_weights)
```

Then implement `load_weights` in the script:

```python
# sender_agent.py
def load_weights(self, path: str) -> None:
    self.agent.message_weights = np.load(path)

# receiver_agent.py
def load_weights(self, path: str) -> None:
    self.agent.action_weights = np.load(path)
```

And uncomment the `load_weights` call in `__main__`.

---

## Running the experiment

Coordinate with your partner to agree on a **room ID** (e.g. `anna-jan`). Use only letters and hyphens — no spaces.

```bash
# Sender student:
python sender_agent.py
# Enter room ID when prompted

# Receiver student:
python receiver_agent.py
# Enter room ID when prompted

# Game server (one person in the pair, or the instructor):
python game_server.py
# Enter the same room ID
```

Start the sender and receiver first, then the game server last. The server waits 3 seconds before round 1 to give both agents time to connect.

---

## What to record

Copy the terminal output after the game ends. You will need the round-by-round reward log for the analysis questions in `lab_network_game.md`.
