# The Lewis Signalling Game — Human Experiment

## Background: Can meaning arise from nothing?

Imagine you and a partner need to coordinate, but you have never agreed on a shared language — and you are not allowed to speak or write freely. All you can do is send one symbol from a fixed set. Your partner receives that symbol and must decide what to do. If they guess right, you both get a point.

This is the **Lewis Signalling Game**, introduced by philosopher David Lewis in 1969. It is a minimal model of how **language conventions can emerge** purely through repeated interaction, without anyone designing them in advance.

The game has two roles:

- **Sender** — sees the current state of the world and sends a signal.
- **Receiver** — sees only the signal and must guess the state.

Neither player knows in advance which signal should mean which state. They must discover a convention by playing many rounds together.

---

## The Rules

### Players and setup

- Work in pairs. One person plays **Sender**, the other plays **Receiver**.
- You will play **40 rounds**.
- There are **4 possible world states**: `1`, `2`, `3`, `4`.
- There are **4 possible signals**: `A`, `B`, `C`, `D`.
  - Signals are arbitrary labels — they carry no inherent meaning.
- There are **4 possible actions** the Receiver can take: `1`, `2`, `3`, `4`.

### Each round

1. The **world state** for that round is pre-filled in the shared sheet (column B). The Sender reads it. The Receiver must **not** look at column B.
2. The **Sender** types one signal (`A`, `B`, `C`, or `D`) into column C.
3. The **Receiver** watches column C, then types one action (`1`, `2`, `3`, or `4`) into column D.
4. The round is a **success** if the Receiver's action matches the world state (`action == state`). Column E shows the result automatically.
5. Move to the next row.

### What you cannot do

- Agree on a code beforehand.
- Communicate outside the signal column (no chat, no gestures, no hints).
- Look at the other player's column (Receiver must not look at column B; Sender must not look at column D until they have committed to their signal).

---

## Google Sheets Setup

One person in the pair creates the shared sheet; the other joins via link.

### Step 1 — Create the sheet

Make a new Google Sheet with these columns:

| A | B | C | D | E |
|---|---|---|---|---|
| Round | State | Signal | Action | Match? |

### Step 2 — Pre-fill the states

Paste the following 40 states into column B (rows 2–41). These were drawn uniformly at random:

```
3, 1, 4, 2, 3, 4, 1, 2, 4, 3,
2, 1, 3, 4, 1, 2, 4, 3, 1, 4,
2, 3, 1, 4, 3, 2, 4, 1, 2, 3,
4, 1, 3, 2, 1, 4, 2, 3, 4, 1
```

Fill column A with round numbers 1–40.

### Step 3 — Auto-calculate the result

In cell E2, enter:

```
=IF(B2=D2,"✓","✗")
```

Then drag it down to E41.

### Step 4 — Hide column B from the Receiver

The Receiver should right-click column B header → **Hide column**. On their screen, the state is now invisible. The Sender should not hide it.

> **Trust the process.** The Receiver's job is to not look at column B. Since you are on separate computers, this is easy — just do not scroll there.

### Step 5 — Share the sheet

The Sender shares the sheet with the Receiver (edit access). Both now have a live, shared workspace.

---

## During the Game

Work at a comfortable pace — there is no time pressure per round, but try to keep the experiment moving. Do not discuss strategy between rounds.

Keep a rough mental note of what signal you are sending for each state (Sender) or what action you associate with each signal (Receiver). You will need this for the analysis.

---

## After the Game — Analysis

Answer the following questions in your notebook or a shared document.

**1. Learning curve**

Plot your match results over rounds (✓ = 1, ✗ = 0). Use a 5-round rolling average to smooth the curve. Do you see improvement over time?

**2. The emerged convention**

Write down the mapping your pair converged on:

| Signal | State it came to mean |
|--------|----------------------|
| A      |                      |
| B      |                      |
| C      |                      |
| D      |                      |

Did the mapping feel intentional, or did it "just happen"?

**3. Arbitrariness**

Is there any reason why, say, `A` should mean state `1` rather than state `3`? What does this tell you about the relationship between a signal and its meaning?

**4. Compare with another pair**

Find another pair in the class. Compare your conventions. Did you converge on the same mapping? What would happen if a Sender from one pair had to communicate with a Receiver from the other pair?

**5. Reflection**

The agents you will implement in the next part of the lab face exactly this problem. They start with no convention and must discover one through interaction. Before you look at the code: what strategy do you think an agent should use to improve from one round to the next?

---

## What comes next

In the programming part of this lab, you will implement agents that play this game automatically — and communicate with your partner's agent **over the network**. Your agent will act as either Sender or Receiver, connected to your partner's agent running on a different computer.

The key question you will explore: if each student trains their agent independently (against a random partner), can the two agents coordinate when they meet for the first time?
