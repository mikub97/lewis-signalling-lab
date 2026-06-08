"""
Lewis Signalling Game — Game Server
====================================
Run this script to act as the "world":
  - generates a random state each round
  - waits for the Receiver's action
  - computes and broadcasts the reward

One student in each pair runs this. The other two run sender_agent.py
and receiver_agent.py respectively.

Usage:
    python game_server.py
"""

import csv
import json
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import paho.mqtt.client as mqtt

# ── Configuration ─────────────────────────────────────────────────────────────
BROKER        = "broker.hivemq.com"
PORT          = 1883
N_STATES      = 4
N_ROUNDS      = 50
ROUND_TIMEOUT = 30   # seconds to wait for the Receiver's action per round
ROUND_DELAY   = 0.4  # seconds between rounds
STARTUP_DELAY = 3    # seconds to wait after connecting before starting


class GameServer:

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.t = {
            "state":  f"lewis/{room_id}/state",
            "signal": f"lewis/{room_id}/signal",
            "action": f"lewis/{room_id}/action",
            "reward": f"lewis/{room_id}/reward",
        }
        self.rng = np.random.default_rng()

        self._action_ready   = threading.Event()
        self._current_action = None
        self._current_signal = None
        self._rows: list[dict] = []

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message  = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Server connected to broker.")
        else:
            print(f"Connection failed (reason_code={reason_code}).")
        client.subscribe(self.t["action"])
        client.subscribe(self.t["signal"])

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
        except json.JSONDecodeError:
            return
        if msg.topic == self.t["signal"]:
            self._current_signal = data.get("signal")
        elif msg.topic == self.t["action"]:
            self._current_action = data.get("action")
            self._action_ready.set()

    def run(self):
        self.client.connect(BROKER, PORT)
        self.client.loop_start()

        print(f"\nWaiting {STARTUP_DELAY}s for agents to connect …")
        time.sleep(STARTUP_DELAY)
        print(f"Starting game — room '{self.room_id}', {N_ROUNDS} rounds.\n")

        rewards  = []
        skipped  = 0

        for rnd in range(N_ROUNDS):
            state = int(self.rng.integers(N_STATES))

            self._action_ready.clear()
            self._current_action = None
            self._current_signal = None

            self.client.publish(
                self.t["state"],
                json.dumps({"round": rnd, "state": state}),
            )

            got_action = self._action_ready.wait(timeout=ROUND_TIMEOUT)

            if not got_action:
                print(f"Round {rnd+1:3d}/{N_ROUNDS} | state={state} | TIMEOUT")
                skipped += 1
                continue

            action = self._current_action
            signal = self._current_signal
            reward = int(action == state)
            rewards.append(reward)
            self._rows.append({"round": rnd, "state": state,
                                "signal": signal, "action": action,
                                "reward": reward})

            rolling = sum(rewards[-10:]) / min(len(rewards), 10)
            marker  = "✓" if reward else "✗"
            print(
                f"Round {rnd+1:3d}/{N_ROUNDS} | state={state}"
                f" | signal={signal} | action={action}"
                f" | {marker}  (10-avg: {rolling:.2f})"
            )

            self.client.publish(
                self.t["reward"],
                json.dumps({
                    "round": rnd, "state": state,
                    "signal": signal, "action": action,
                    "reward": reward,
                }),
            )
            time.sleep(ROUND_DELAY)

        self.client.loop_stop()
        self.client.disconnect()

        print("\n─── Game over ───────────────────────────────")
        if rewards:
            print(f"Rounds played : {len(rewards)}  (skipped: {skipped})")
            print(f"Total reward  : {sum(rewards)} / {len(rewards)}")
            print(f"Accuracy      : {sum(rewards)/len(rewards):.1%}")
        else:
            print("No rounds completed.")

        if self._rows:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = Path(__file__).parent / f"results_{self.room_id}_{ts}.csv"
            with csv_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["round", "state", "signal", "action", "reward"])
                writer.writeheader()
                writer.writerows(self._rows)
            print(f"Results saved : {csv_path.resolve()}")


if __name__ == "__main__":
    room = input("Enter room ID (share this with your partner): ").strip()
    GameServer(room).run()
