# Instructor Guide — Lewis Signalling Game Lab

## Overview

The lab has two phases:

| Phase | Activity | Document |
|-------|----------|----------|
| 1 | Human experiment (Google Sheets) | `lab_human_experiment.md` |
| 2 | Agent implementation + network game | `lab_agent_implementation.md`, `lab_network_game.md` |

Suggested total time: **~3 hours** (can be split across two sessions).

---

## Before the lab

### Software
Students need:
```bash
pip install paho-mqtt numpy
```
Check this works on lab machines or ask students to do it before the session.

### Pairing
Pair students before the session starts. Each pair needs:
- A shared room ID (agree beforehand or let them choose on the day)
- One student as **Sender**, one as **Receiver**
- One of them (or you) to run `game_server.py` — see "Who runs the server" below

### Google Sheets
Prepare one template sheet and share the link. Pre-fill:
- Column A: round numbers 1–40
- Column B: the state sequence (given in `lab_human_experiment.md`)
- Cell E2: `=IF(B2=D2,"✓","✗")`, dragged to E41

Students make a copy of the template for their pair.

### Who runs the server?
Three options — choose based on class size and comfort:

1. **You run it centrally** — one `game_server.py` process per pair, all on your machine. Manageable for up to ~5 pairs; just open multiple terminals.
2. **One student per pair runs it** — lower coordination overhead, scales to any class size. The "server student" runs all three scripts on their machine (server + their own agent), while the partner runs only their agent.
3. **One student per pair, separate** — dedicated third student per group of three acts as game master. Good for exploring the game master role.

Option 2 is recommended for most classes.

---

## Session plan

### Phase 1 — Human experiment (~45 min)

1. **Brief introduction (~10 min)**
   - Explain the setup: two roles, fixed vocabulary, no prior agreement
   - Emphasise: signals have *no inherent meaning*
   - Run one demo round on the projector (you as sender, volunteer as receiver via chat)

2. **Pairs play (~25 min)**
   - Students share their Google Sheet, play 40 rounds
   - Circulate and check:
     - Is the Receiver hiding column B?
     - Are they moving at a reasonable pace?
     - Are they resisting the urge to chat strategy?

3. **Quick debrief (~10 min)**
   - Ask 2–3 pairs: what convention did you converge on?
   - Write their mappings on the board — are any the same?
   - Key question: *why are the mappings different across pairs?*

### Phase 2 — Implementation (~2h 15min)

#### Part A — Agent implementation (~60 min)

Students work individually on Task 0 (implement `Sender`/`Receiver`) and Tasks 1–3 (wire to the network layer).

**Common mistakes to watch for:**
- Forgetting to store `_last` in `send_message`/`act` (breaks learning)
- Not subtracting the row max before `exp` (overflow with large weights)
- Initialising weights to zero instead of `eps` (causes division by zero in softmax at round 0)
- Using `=` instead of `+=` in `learn_from_feedback`

**Checkpoint before moving on:** ask each student to run a quick offline sanity check in a Python shell:

```python
import numpy as np
rng = np.random.default_rng(0)
# paste their Sender class
s = Sender(4, 4)
m = s.send_message(2)
s.learn_from_feedback(1)
print(s.message_weights[2])   # should show one entry slightly above 1e-6
```

#### Part B — Network game, cold start (~30 min)

Pairs run Experiment A: both agents start from uninitialised weights.

- Ensure all three scripts are running with the **same room ID** before the server starts
- 50 rounds takes about 30–40 seconds
- Students copy the reward log to a text file

**What to expect:** accuracy stays near 25% (chance level) for most of the game, occasionally drifting to 30–40%. Full coordination is unlikely in 50 rounds from cold start with random partners.

#### Part C — Network game, warm start (optional, ~20 min)

Students implement Task 4 (load pre-trained weights from the notebook) and re-run.

**What to expect:** two agents that trained together in the notebook will coordinate immediately (~100% accuracy). Two agents from different pairs will fail initially, then adapt.

#### Part D — Analysis and discussion (~25 min)

Students answer the reflection questions in `lab_network_game.md`. Close with a whole-class discussion:

**Key discussion points:**

1. *Cold start failure.* Both agents learned a valid signalling system in isolation — so why do they fail together? Draw out: a convention is not a property of an individual, it's a property of a *pair*. Language is inherently social.

2. *Warm start.* If they used pre-trained weights from a pair that trained *together*, they coordinate perfectly. If weights came from different pairs, one agent has to "abandon" its convention. Which one? Usually the receiver, because senders persist in using their own signals — this matches how dominant languages spread.

3. *Human vs. agent.* In the human experiment, pairs converged in ~40 rounds. How does this compare to the agent game? Why might humans converge faster (or slower)?

4. *Implications.* What does this model miss about real language? (Possible answers: no compositionality, no shared physical context, no pragmatic inference, vocabulary is pre-defined.)

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Agents connect but no rounds start | Server started before agents | Restart server *after* both agents are connected |
| `Connection failed (reason_code=...)` | Firewall or network blocks port 1883 | Try port 8883 (TLS) or switch to `test.mosquitto.org` |
| Round 1 always times out | Agents slow to subscribe | Increase `STARTUP_DELAY` in `game_server.py` (line ~30) |
| Rewards received by only one agent | Wrong room ID on one side | Check all three terminals use exactly the same string |
| `NotImplementedError` at start | Student missed a task | Check Tasks 0–3 are all implemented |
| Weights go NaN | Weights grew very large before softmax | Check the `- W[i].max()` subtraction is in place |

---

## Files summary

```
signalling/
├── lewis_signalling.ipynb          ← main notebook (Phase 1 of the whole lab)
├── lewis_signalling_filled.ipynb   ← instructor reference
├── lab_human_experiment.md         ← student instructions for Google Sheets game
└── network_game/
    ├── game_server.py              ← given; runs the world
    ├── sender_agent.py             ← scaffolded; students implement Tasks 0–3
    ├── receiver_agent.py           ← scaffolded; students implement Tasks 0–3
    ├── lab_agent_implementation.md ← student implementation guide
    ├── lab_network_game.md         ← student experiment + analysis questions
    └── instructor_guide.md         ← this file
```
