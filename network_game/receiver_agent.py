"""
Lewis Signalling Game — Receiver Agent
========================================
Connect your Receiver agent to the live game server over the network.

Your tasks
----------
  Task 1  Initialise your agent inside NetworkReceiver.__init__.
  Task 2  Implement choose_action — given a received signal, ask your agent
          which action to take.
  Task 3  Implement learn — update your agent after the reward arrives.

Optional
--------
  Task 4  Load pre-trained weights so your agent starts from a convention
          it already learned, rather than from scratch.

Usage
-----
    python receiver_agent.py
"""

import json

import numpy as np
import paho.mqtt.client as mqtt

# ── Configuration ─────────────────────────────────────────────────────────────
BROKER     = "broker.hivemq.com"
PORT       = 1883
N_MESSAGES = 4
N_STATES   = 4   # = number of possible actions

rng = np.random.default_rng()

# ─────────────────────────────────────────────────────────────────────────────
# Receiver — provided, no changes needed
#
# Maintains a weight matrix of shape (n_messages, n_actions).
# Row i holds the propensity scores for each action when the received signal
# is i.  Scores are converted to probabilities with softmax; the chosen
# (message, action) pair has its score updated by the reward (Roth–Erev rule).
# ─────────────────────────────────────────────────────────────────────────────

class Receiver:

    def __init__(self, n_messages: int, n_actions: int, eps: float = 1e-6):
        self.n_actions = n_actions
        # shape: (n_messages, n_actions) — row = message, column = action
        self.action_weights = np.full((n_messages, n_actions), eps)
        self._last = (0, 0)   # (message, action) chosen in the last round

    def act(self, message: int) -> int:
        """Sample an action for the given message using the current policy."""
        w = self.action_weights[message] - self.action_weights[message].max()
        probs = np.exp(w) / np.exp(w).sum()
        action = rng.choice(self.n_actions, p=probs)
        self._last = (message, action)
        return action

    def learn_from_feedback(self, reward: int) -> None:
        """Add reward to the weight of the last (message, action) pair."""
        self.action_weights[self._last] += reward


# ─────────────────────────────────────────────────────────────────────────────
# NetworkReceiver — wraps the Receiver and handles MQTT communication.
#
# Do NOT change the constructor signature or the run() method.
# Fill in the three tasks marked below.
# ─────────────────────────────────────────────────────────────────────────────

class NetworkReceiver:
    """Wraps a Lewis Receiver agent and connects it to the MQTT game."""

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.t = {
            "signal": f"lewis/{room_id}/signal",
            "action": f"lewis/{room_id}/action",
            "reward": f"lewis/{room_id}/reward",
        }

        # ── Task 1 — Initialise your agent ────────────────────────────────────
        # Create a Receiver instance and store it as self.agent so that the
        # choose_action and learn methods can use it.
        #
        # The Receiver constructor takes two arguments:
        #   n_messages — number of distinct signals it can receive  (use N_MESSAGES)
        #   n_actions  — number of distinct actions it can take     (use N_STATES)
        #
        # TODO: replace the line below with a real Receiver instance.
        self.agent = None
        # ──────────────────────────────────────────────────────────────────────

        self._last_signal = None
        self._last_action = None
        self._last_round  = None
        self.reward_history: list[int] = []

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self._on_connect
        self.client.on_message  = self._on_message

    # ── Task 2 — Choose an action ─────────────────────────────────────────────
    def choose_action(self, signal: int) -> int:
        """Return an action in {0, …, N_STATES-1} for the given signal.

        Called automatically each round, right after the Sender's signal
        arrives.  The returned value is published to the server, which checks
        whether it matches the hidden world state.

        What to do:
          - Ask self.agent to pick an action for this signal.
          - Return that action (an integer).

        Hint: Receiver.act(signal) does exactly this.
        """
        # TODO: implement this method
        raise NotImplementedError("Task 2: implement choose_action")
    # ─────────────────────────────────────────────────────────────────────────

    # ── Task 3 — Learn from the round outcome ────────────────────────────────
    def learn(self, signal: int, action: int, reward: int) -> None:
        """Update agent weights after each round.

        Called automatically once the reward for this round has arrived.
        The arguments describe everything that happened:
          signal — the signal the Sender sent
          action — the action you took  (same as the return value of choose_action)
          reward — 1 if your action matched the world state, 0 otherwise

        What to do:
          - Pass the reward to the agent's learning method so it can
            strengthen or leave unchanged the (signal → action) association.

        Hint: Receiver.learn_from_feedback(reward) does exactly this.
              The agent already remembers the last (signal, action) pair
              internally, so you only need to forward the reward.
        """
        # TODO: implement this method
        raise NotImplementedError("Task 3: implement learn")
    # ─────────────────────────────────────────────────────────────────────────

    # ── (Optional) Task 4 — Load pre-trained weights ─────────────────────────
    def load_weights(self, path: str) -> None:
        """Load action_weights saved from the notebook with np.save().

        After running the notebook simulation you can export the trained weights:
            np.save("receiver_weights.npy", receiver.action_weights)

        Call this method before receiver.run() so your agent starts from the
        convention it already learned rather than from a uniform distribution.

        What to do:
          - Load the .npy file with np.load(path).
          - Assign the loaded array to self.agent.action_weights.
          - Make sure the shape matches (N_MESSAGES, N_STATES) before assigning.
        """
        # TODO: implement this method (optional)
        pass
    # ─────────────────────────────────────────────────────────────────────────

    # ── Internal — do not edit below this line ────────────────────────────────

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Receiver connected to broker.")
        else:
            print(f"Connection failed (reason_code={reason_code}).")
        client.subscribe(self.t["signal"])
        client.subscribe(self.t["reward"])

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
        except json.JSONDecodeError:
            return

        if msg.topic == self.t["signal"]:
            signal = data["signal"]
            rnd    = data["round"]
            self._last_signal = signal
            self._last_round  = rnd

            action = self.choose_action(signal)
            self._last_action = action

            self.client.publish(
                self.t["action"],
                json.dumps({"round": rnd, "action": action}),
            )
            print(f"Round {rnd+1:3d} | signal={signal} → action={action}", flush=True)

        elif msg.topic == self.t["reward"]:
            reward = data["reward"]
            self.reward_history.append(reward)
            rolling = sum(self.reward_history[-10:]) / min(len(self.reward_history), 10)
            marker  = "✓" if reward else "✗"
            print(f"         {marker}  reward={reward}  (10-avg: {rolling:.2f})")

            if self._last_signal is not None and self._last_action is not None:
                self.learn(self._last_signal, self._last_action, reward)

    def run(self):
        if self.agent is None:
            raise RuntimeError(
                "Task 1: self.agent is None — initialise it before calling run()."
            )
        self.client.connect(BROKER, PORT)
        print(f"Receiver waiting for game in room '{self.room_id}' …")
        self.client.loop_forever()


if __name__ == "__main__":
    room     = input("Enter room ID (must match the game server): ").strip()
    receiver = NetworkReceiver(room)

    # Optional: load pre-trained weights
    # receiver.load_weights("receiver_weights.npy")

    receiver.run()
