# Lewis Signalling Lab

Lab materials for a computational/cognitive modelling course on the emergence of language as convention, based on David Lewis's signalling game (1969).

Students progress through three activities: a human experiment, a simulation notebook, and a live networked multi-agent game.

---

## Structure

### Root

| File | Description |
|---|---|
| `lewis_signalling.ipynb` | Main student notebook — implements tabular Roth–Erev agents, trains them in simulation, and visualises the emerging signalling system |
| `lab_human_experiment.md` | Lab sheet for the human version of the game (played in pairs before the coding session, to build intuition) |
| `_make_sheet.py` | Helper script used to generate printable lab sheets |

### `network_game/`

A live multiplayer version: three students in a group each run one script (game server, sender, receiver) and their agents play over MQTT.

| File | Description |
|---|---|
| `lab_network_game.md` | Lab sheet — explains the network setup and what students need to do |
| `lab_agent_implementation.md` | Coding instructions — walks students through Tasks 1–4 |
| `sender_agent.py` | Student template for the Sender — Tasks 1–3 are marked TODO |
| `receiver_agent.py` | Student template for the Receiver — Tasks 1–3 are marked TODO |
| `sender_agent_solved.py` | Reference solution for the Sender (instructor only) |
| `receiver_agent_solved.py` | Reference solution for the Receiver (instructor only) |
| `game_server.py` | World / referee process — draws states, broadcasts rewards, saves results to CSV |
| `results_visualisation.ipynb` | Notebook for visualising a saved CSV: learning curve + signalling system heatmaps |
| `lewis_signalling_filled.ipynb` | Filled-in version of the main notebook (instructor reference) |
| `lewis_signalling_game.xlsx` | Printable score sheet for the human experiment |
| `instructor_guide.md` | Session guide and timing notes for the instructor |
| `_test_integration.py` | Integration test — runs server + sender + receiver in threads and asserts rewards flow correctly |

---

## Flow

```
1. Human experiment (pairs, pen & paper)
        ↓
2. lewis_signalling.ipynb  (simulation, individual)
        ↓
3. network_game/  (live multi-agent, groups of 3)
   one student runs game_server.py
   one student runs sender_agent.py
   one student runs receiver_agent.py
        ↓
4. results_visualisation.ipynb  (debrief)
```

---

## Dependencies

```
numpy
matplotlib
seaborn
paho-mqtt
pandas        # results_visualisation.ipynb only
```