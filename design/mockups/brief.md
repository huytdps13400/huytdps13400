# Shared brief — GitHub profile README redesign (Trần Đình Huy)

You are producing high-fidelity DESIGN MOCKUP IMAGES (not code) with your built-in image generation tool.
Pass design/mockups/ref-current.png as a reference image: it is the CURRENT README (content + section order only).
Its look is being REPLACED — do not copy its rainbow mesh, its colour-per-card gradients or its navy.

Context: a GitHub profile README for a Senior React Native Engineer. It renders inside GitHub's ~830px-wide
column as a vertical stack of wide images. Goal: luxury, premium, pixel-perfect, world-class — the level of
Stripe / Linear / Apple product pages. Restraint over decoration: ONE accent colour, generous negative space,
crisp hairlines, a single hero render as the "gasp" moment, perfect alignment to a 12-column grid,
consistent 24px gutters, concentric corner radii (outer = inner + padding).

New section order (show it exactly like this, each section as a wide rounded card on the page background):
1. HERO card (16:8). Left: small eyebrow "React Native · iOS · Android", name "Trần Đình Huy" very large,
   "Senior React Native Engineer", one-line bio "I build secure, production-grade mobile apps — and
   open-source the infrastructure behind them." Under it a stats strip with thin vertical dividers:
   "5+ YEARS SHIPPING", "4 OPEN-SOURCE LIBS", "3 PAYMENT GATEWAYS". Right: the hero 3D render (see direction).
   Under the hero card: a row of 3 pill buttons: "Follow on X" (the only filled/primary one), "LinkedIn", "npm packages".
2. Section header "01 — Expertise" / big title "Built for the hard parts of mobile." then a 2×2 grid of cards:
   "Mobile security", "Payments", "Release engineering", "New Architecture" — each with ONE icon in the SAME
   material/colour (no rainbow), a 2-line description and small tag chips
   (SSL Pinning · Biometrics · Keystore / VNPay · ZaloPay · Payoo / Fastlane · Expo Updates · TestFlight /
   Nitro · TurboModules · Reanimated).
3. "02 — Open source" / "Libraries born in production." — one wide flagship card "react-native-ssl-manager"
   (left copy + 4 check features, right a terminal/code window with JSON pin config), then a 2×2 grid:
   "react-native-iconify", "sms-retriever-nitro-module", "supabase-expo-ota-updates", "More on npm",
   each with star + download counts top-right and a one-line code snippet bar at the bottom.
4. "03 — Activity" / "Shipping, consistently." — stats row (1,847 contributions · 10 days streak ·
   229 days longest · 104 best day) above a GitHub contribution heatmap tinted in the accent ramp.
5. Footer CTA card: "Let's build something people trust." + "Open to senior React Native roles, consulting
   and open-source collaboration." + button "Say hello on X". (The old separate "On X" section is removed.)

Rules for the images:
- Spell every word exactly as given; Vietnamese diacritics in "Trần Đình Huy" must be correct.
- Flat front-on screenshot of the page, no perspective, no device frame, no browser chrome, no hands.
- Text must be sharp and legible; prefer fewer words over garbled words.
