"""
Lewis Signalling Game — Sender Agent  [SOLVED]
===============================================
Reference implementation — do not distribute to students.

Usage
-----
    python sender_agent_solved.py
"""

import json

import numpy as np
import paho.mqtt.client as mqtt

# ── Configuration ─────────────────────────────────────────────────────────────
BROKER     = "broker.hivemq.com"
PORT       = 1883
N_STATES   = 4
N_MESSAGES = 4

rng = np.random.default_rng()

# ─────────────────────────────────────────────────────────────────────────────
# Sender — provided, no changes needed
#
# Maintains a weight matrix of shape (n_states, n_messages).
# Row i holds the propensity scores for each message when the world state is i.
# Scores are converted to probabilities with softmax; the chosen (state, message)
# pair has its score updated by the reward (Roth–Erev rule).
# ─────────────────────────────────────────────────────────────────────────────

class Sender:

    def __init__(self, n_states: int, n_messages: int, eps: float = 1e-6):
        self.n_messages = n_messages
        # shape: (n_states, n_messages) — row = state, column = message
        self.message_weights = np.full((n_states, n_messages), eps)
        self._last = (0, 0)   # (state, message) chosen in the last round

    def send_message(self, state: int) -> int:
        """Sample a message for the given state using the current policy."""
        w = self.message_weights[state] - self.message_weights[state].max()
        probs = np.exp(w) / np.exp(w).sum()
        message = rng.choice(self.n_messages, p=probs)
        self._last = (state, message)
        return message

    def learn_from_feedback(self, reward: int) -> None:
        """Add reward to the weight of the last (state, message) pair."""
        self.message_weights[self._last] += reward


# ─────────────────────────────────────────────────────────────────────────────
# NetworkSender — wraps the Sender and handles MQTT communication.
#
# Do NOT change the constructor signature or the run() method.
# Fill in the three tasks marked below.
# ─────────────────────────────────────────────────────────────────────────────

class NetworkSender:
    """Wraps a Lewis Sender agent and connects it to the MQTT game."""

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.t = {
            "state":  f"lewis/{room_id}/state",
            "signal": f"lewis/{room_id}/signal",
            "reward": f"lewis/{room_id}/reward",
        }

        self.agent = Sender(N_STATES, N_MESSAGES)

        self._last_state  = None
        self._last_signal = None
        self.reward_history: list[int] = []

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self._on_connect
        self.client.on_message  = self._on_message

    def choose_signal(self, state: int) -> int:
        return self.agent.send_message(state)

    def learn(self, state: int, signal: int, reward: int) -> None:
        self.agent.learn_from_feedback(reward)

    def load_weights(self, path: str) -> None:
        weights = np.load(path)
        assert weights.shape == (N_STATES, N_MESSAGES), (
            f"Expected shape ({N_STATES}, {N_MESSAGES}), got {weights.shape}"
        )
        self.agent.message_weights = weights

    # ── Internal — do not edit below this line ────────────────────────────────

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Sender connected to broker.")
        else:
            print(f"Connection failed (reason_code={reason_code}).")
        client.subscribe(self.t["state"])
        client.subscribe(self.t["reward"])

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
        except json.JSONDecodeError:
            return

        if msg.topic == self.t["state"]:
            state  = data["state"]
            rnd    = data["round"]
            self._last_state = state

            signal = self.choose_signal(state)
            self._last_signal = signal

            self.client.publish(
                self.t["signal"],
                json.dumps({"round": rnd, "signal": signal}),
            )
            print(f"Round {rnd+1:3d} | state={state} → signal={signal}", flush=True)

        elif msg.topic == self.t["reward"]:
            reward = data["reward"]
            self.reward_history.append(reward)
            rolling = sum(self.reward_history[-10:]) / min(len(self.reward_history), 10)
            marker  = "✓" if reward else "✗"
            print(f"         {marker}  reward={reward}  (10-avg: {rolling:.2f})")

            if self._last_state is not None and self._last_signal is not None:
                self.learn(self._last_state, self._last_signal, reward)

    def run(self):
        if self.agent is None:
            raise RuntimeError("self.agent is None — initialise it before calling run().")
        self.client.connect(BROKER, PORT)
        print(f"Sender waiting for game in room '{self.room_id}' …")
        self.client.loop_forever()


if __name__ == "__main__":
    room   = input("Enter room ID (must match the game server): ").strip()
    sender = NetworkSender(room)

    # Optional: load pre-trained weights
    # sender.load_weights("sender_weights.npy")

    sender.run()
