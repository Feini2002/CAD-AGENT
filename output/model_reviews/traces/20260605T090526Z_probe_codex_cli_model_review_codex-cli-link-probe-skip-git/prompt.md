You are running a connectivity probe for a CAD Agent model-review bridge.
Do not inspect files, do not call tools, do not execute CAD, and do not make
any claim about a real drawing.

Return exactly one JSON object matching the provided schema.
For this synthetic probe only, set status to pass, all boolean fields to true,
blockingReasons and visualProblems to empty arrays, and repairRecommendation to
{"mode":"none","reason":"synthetic connectivity probe only","targetZone":"none","targetHandles":[],"nextChecks":[]}.
Set lookHereFirst to ["synthetic probe only"].
Also include decision, assumptions, alternativesConsidered, blockingReasons,
nextRequiredEvidence, learningCandidate, statePatch, finalResponseAllowedClaims,
evidenceUsed, and evidenceMissing. statePatch must contain phase,
phaseLabelForUser, completedEvidence, pendingEvidence, pendingUserAction,
blockedReason, and nextSafeAction. Include toolIntent and set it to null.