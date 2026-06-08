"""
Lewis Signalling Game — Receiver Agent  [SOLVED]
=================================================
Reference implementation — do not distribute to students.

Usage
-----
    python receiver_agent_solved.py
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

        self.agent = Receiver(N_MESSAGES, N_STATES)

        self._last_signal = None
        self._last_action = None
        self._last_round  = None
        self.reward_history: list[int] = []

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self._on_connect
        self.client.on_message  = self._on_message

    def choose_action(self, signal: int) -> int:
        return self.agent.act(signal)

    def learn(self, signal: int, action: int, reward: int) -> None:
        self.agent.learn_from_feedback(reward)

    def load_weights(self, path: str) -> None:
        weights = np.load(path)
        assert weights.shape == (N_MESSAGES, N_STATES), (
            f"Expected shape ({N_MESSAGES}, {N_STATES}), got {weights.shape}"
        )
        self.agent.action_weights = weights

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
            raise RuntimeError("self.agent is None — initialise it before calling run().")
        self.client.connect(BROKER, PORT)
        print(f"Receiver waiting for game in room '{self.room_id}' …")
        self.client.loop_forever()


if __name__ == "__main__":
    room     = input("Enter room ID (must match the game server): ").strip()
    receiver = NetworkReceiver(room)

    # Optional: load pre-trained weights
    # receiver.load_weights("receiver_weights.npy")

    receiver.run()
