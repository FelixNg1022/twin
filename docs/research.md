# Research — Twin

## The problem

College dating on mainstream apps is broken in a specific way: swiping commodifies users into thumbnails competing against hundreds of other thumbnails. The matching surface has no signal for who someone actually is — only a handful of photos, a one-line bio, and a prompt answer. Pew's 2023 research on Americans' experiences with online dating finds that roughly half of users under 30 describe recent dating-app experiences as more negative than positive; common complaints cluster around superficial interactions and message fatigue before a date ever happens.

Ditto's bet is that an AI-native matchmaker can skip the swipe surface entirely: users text an agent their preferences, an AI persona represents them in simulated matching, and a single date is proposed per week. For that bet to work, the AI persona has to be an accurate enough representation of a user that downstream matching isn't garbage-in-garbage-out. **Twin is the feature that produces that representation.**

## Why self-report fails for personality matching

Finkel et al.'s 2012 review of online-dating matching algorithms (*Online Dating: A Critical Analysis From the Perspective of Psychological Science*) found no published evidence that matching based on self-reported preferences or demographic similarity predicts long-term relationship outcomes beyond chance. Self-report is noisy: people describe the partner they think they should want, not the partner they actually pick. Behavioral signals — how someone describes a concrete recent event, how they respond to a friend's hypothetical crisis — reveal dispositions that self-report hides.

## Why MBTI and Big Five together

MBTI isn't scientifically rigorous — its factor structure doesn't replicate cleanly and its test-retest reliability is mediocre. But it has dramatically more cultural footprint than Big Five: college students know their MBTI letters, share them in Instagram bios, and take BuzzFeed-style quizzes for fun. Big Five is the validated science — continuous, replicable, and correlated with relationship outcomes.

Twin probes on Big-Five-adjacent behavioral dimensions under the hood (extraversion, openness/intuition, agreeableness/feeling, conscientiousness/judging), aggregates scores, and returns **both** surface artifacts the user will screenshot (MBTI label + dimension bars) **and** structured continuous scores downstream matching will consume. User-facing fun, downstream-rigorous.

## Design implications

1. **Behavioral probes only.** "What did you do last Saturday night?" instead of "Are you extraverted?" The self-report mode is explicitly banned.
2. **iMessage-native styling.** Ditto lives in iMessage; an onboarding flow that looks like a form is off-brand on day one.
3. **Channel abstraction.** The agent logic must be decoupled from delivery (web for this demo, Photon Spectrum SDK for real iMessage), because Ditto is actively making this decoupling real.
4. **Structured persona output.** Downstream matching consumes JSON, not prose. Persona is the contract.

## What's next (V2)

Humor compatibility — see README "What's next" section. Gottman's marriage-stability research and Hall 2017's meta-analysis on humor-in-romance position shared humor as a stronger predictor than shared hobbies. No major dating app matches on this today.
