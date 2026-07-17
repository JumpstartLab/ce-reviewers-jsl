# Jeff's Voice Guide

The single source of truth for what "sounds like Jeff" means. Every writing
reviewer cites this file by section. Maxwell Perkins (the orchestrator) drafts
against it and appends new rules to the Changelog every time Jeff corrects a
draft. When this guide and a reviewer's instinct disagree, **this guide wins** —
and if the guide is wrong, fix the guide, don't override it silently.

> Derived from real samples: the "Is This Working?" JTBD essay (essay voice) and
> `server-admin/docs/miren-feedback.md` (docs voice), plus the standing no-filler
> rule. Email voice is **under-sampled** — treat email guidance as provisional
> until Jeff supplies examples.

---

## 1. Core stance

Write to make one reader think, then act. Lead with the idea that governs
everything else, then earn it. Compress relentlessly — every sentence either
advances the argument or gets cut. Be concrete before abstract, honest about
what you don't know, and unafraid to land a hard point plainly. The voice is a
smart colleague who respects the reader's time and intelligence: direct, warm
enough, never chatty, never hedged.

## 2. Conventions (the enforceable rules)

Reviewers cite these by number.

1. **Lead with the governing idea.** State the principle, the answer, or the
   thesis before the supporting detail. Don't bury it under setup.
2. **Cut every needless word.** No throat-clearing, no hedges, no filler
   ("honestly," "I think," "just," "very," "in order to," "it's worth noting").
   See [[writing-style-no-filler]].
3. **Concrete before abstract.** Name the real person, the real number, the real
   example. "A degreed director doing cough-timestamping," not "misallocated
   senior talent."
4. **Prefer verbs of compression and motion.** narrow, collapse, absorb, land,
   resolve, gate, ship, cut. Verbs carry the sentence; adjectives don't.
5. **Mark uncertainty; don't hedge it.** Flag an inference with ⚠ or a plain
   "unconfirmed" rather than softening the whole sentence into mush.
6. **End sections on a clincher.** The last line should land the point, not
   trail off into qualification.
7. **Structure carries meaning.** Use triads, tables, numbered jobs, and bold
   inline labels to compress — don't narrate what a table could show.
8. **Say the hard thing plainly.** If quality will slip, say "quality slips."
   No euphemism, no cushioning.

## 3. Signature moves (what makes it unmistakably Jeff)

These are the patterns to *reach for* — a draft that sounds like Jeff uses
several of them.

- **The triad.** Group into threes: "Automated / Delegated / Eliminated,"
  "Keep / Remove," "narrow to three things." Three is the default cardinality.
- **The aphoristic clincher.** A standalone declarative that crystallizes the
  section: *"Every hour Connor is not in the ops loop is an hour he can spend in
  another room doing the interview that generates the value."*
- **The em-dash sharpener.** An em-dash that adds a vivid, concrete, sometimes
  pointed clarification — the reframe that makes the abstract land.
- **The framing-question header.** A header that poses the real question and
  names the stakes in a parenthetical: *"The linchpin question (a trust
  decision, not a tool decision)."*
- **The stakes sentence.** "If no one owns it, X silently fails and Y slips." —
  make the consequence of inaction explicit.
- **The X, not Y reframe.** "A trust decision, not a tool decision." Sharp,
  earned, corrective. (This is *allowed and encouraged* — do not confuse it with
  the banned AI-tell in §5.)
- **Honesty markers.** ⚠ for inferences, "ruled out: …" to show the negative
  space of reasoning, explicit "unconfirmed."
- **Bold inline labels.** `Keep (irreducible):`, `Remove from his plate:`,
  `How to sell it:` — a bolded lead-in that does a heading's work inside a list.

## 4. Rhythm

- **Vary sentence length hard.** Follow a long, clause-stacked sentence with a
  three-word hammer. Monotone length is the tell of lifeless prose.
- **Fragments are allowed** when deliberate and punchy. "Narrow to interview
  plus relationship." "Eliminated."
- **Read it aloud.** If you run out of breath or stumble, re-cut. The clincher
  especially must be sayable in one breath.
- **No comma splices standing in for structure** — if two ideas are both load-
  bearing, give them their own sentences or an em-dash, not a lazy comma.

## 5. Diction — reach for / kill

**Reach for:** narrow, collapse, absorb, land, resolve, gate, irreducible,
linchpin, load-bearing, textbook (as in "textbook misallocation"), plainly,
ship, cut. Plain Anglo-Saxon verbs over Latinate abstractions.

**Kill on sight (AI-slop and filler):**
- delve, tapestry, realm, landscape, testament, underscore, boasts, leverage
  (as a verb), utilize, myriad, plethora, robust (as filler), seamless.
- **"It's not just X — it's Y"** / "not merely X but Y" as an inflation device.
  (Distinct from the allowed sharp "X, not Y" reframe in §3.)
- Rhetorical throat-clearing: "In today's fast-paced world," "It's worth noting
  that," "At the end of the day."
- Hedges: "honestly," "I think," "arguably," "somewhat," "fairly," "quite."
- Empty intensifiers: "very," "really," "extremely," "incredibly."
- Em-dash *overuse* — the em-dash is a signature tool, so it loses force if
  every sentence has one. One sharpener per idea, not per clause.

## 6. Structure

- **Answer first.** The reader should get the point in the first paragraph (or
  the first row of the table) and spend the rest confirming it — never hunting
  for it. (Minto's pyramid.)
- **Scaffold, then fill.** Docs use a repeatable skeleton: Summary → Evidence →
  Why it matters → Options/Suggested fixes → What we did. Essays use: governing
  principle → the map (table) → the human decisions → what's perishable.
- **One idea per section.** If a section argues two things, split it.
- **Tables compress; prose persuades.** Put structured, parallel data in a
  table. Reserve prose for the argument the table can't make.

## 7. Formatting — the "looks"

- **Scannable by design.** A skim of headers, bold labels, and table rows should
  convey the spine of the argument without reading a full sentence.
- **Bold inline labels** to open list items that carry a category.
- **Framing-question or noun-phrase headers**, not generic ("Overview,"
  "Introduction," "Conclusion" are banned).
- **⚠ / status tags** to mark confidence inline.
- **Short paragraphs.** Three to five sentences max in essays; often one in
  docs. White space is a feature.
- **No decorative emoji.** Functional markers only (⚠, mode legends, status).

## 8. By medium

- **Essay / blog** — governing principle up top, an aphoristic clincher per
  section, more voice and rhythm, willing to be pointed. The JTBD doc is the
  reference.
- **Docs / README** — the Summary→Evidence→Why-it-matters skeleton, heavy on
  concrete numbers and "ruled out" reasoning, minimal adjectives. `miren-feedback.md`
  is the reference. Voice is present but subordinate to precision.
- **Email** — *under-sampled.* Provisional guidance: open with the ask or the
  answer, one screen max, end with the single next action and who owns it.
  Replace this section with real examples when available.

## 9. Audience & terms of art

- Default reader: a **smart, busy peer** — a technical founder, a senior
  engineer, a client decision-maker. Assume intelligence; don't assume they
  share your context. Bridge, don't condescend.
- **Use the right term of art, once.** JSL/dev-tooling/education vocabulary
  (jobs-to-be-done, irreducible, gate, slate, tier triage) is correct *when the
  audience shares it*. Define a term on first use only if the audience might not.
- **Never jargon as decoration.** A term of art must be load-bearing. If a plain
  word works and the audience isn't expecting the jargon, use the plain word.
- Match register to the reader: a funder-facing narrative is not an ops doc.

## 10. Anti-patterns (kill these)

- Buried lead — the point arrives in paragraph four.
- Hedged thesis — "This might possibly be worth considering."
- Adjective inflation standing in for a concrete example.
- Monotone rhythm — every sentence the same length.
- AI-slop vocabulary (§5) and the "not just X, it's Y" inflation.
- Generic headers, decorative emoji, walls of unbroken text.
- Euphemism where a plain hard statement belongs.

## 11. Changelog (Perkins appends here)

Every correction Jeff makes to a draft becomes a rule here, dated. This is how
the team compounds toward his voice.

- 2026-07-16 — Guide created from the JTBD essay + Miren docs + the no-filler
  memory. Email voice flagged as under-sampled.
