# Animations Used in the Project — With Code and Where They Are

This document lists **every animation** used in the frontend, **where** it is used (which page or component and which CSS class), and the **actual code** so you can understand and explain them easily.

All animations are defined in **`frontend/src/styles.css`**. There are **no** separate animation libraries (e.g. Framer Motion); everything is **CSS only** (keyframes + `animation` / `transition`).

---

## 1. List of All Animations and Transitions

| Name | Type | Where used | What it does |
|------|------|------------|--------------|
| **honeycombFloat** | @keyframes | body::before, auth-page::before | Honeycomb pattern slowly moves and fades in/out |
| **glowPulse** | @keyframes | body::after, auth-page::after | Red glow fades in and out (opacity) |
| **bgFloat** | @keyframes | .auth-bg | Background gradient drifts slightly |
| **orbFloat** | @keyframes | .glow-orb, .orb-two | Orbs move up and down |
| **fadeUp** | @keyframes | .page, .landing-panel, .landing-title, .auth-branding, .auth-form-wrap, cards | Element fades in and moves up a little |
| **fadeUpDelay** | @keyframes | .landing-subtitle, .landing-support | Same as fadeUp but with delay (staggered) |
| **floatIn** | @keyframes | .auth-card | Card floats in from slightly below |
| **cardFade** | @keyframes | .info-card | Card fades in and moves up |
| **splitOut** | @keyframes | .honeycomb-split.active .split-panel | Four panels move apart when “Enter” is clicked |
| **flashGlow** | @keyframes | .bright-flash.active | Brief red flash when leaving Welcome |
| **slideInRight** | @keyframes | .auth-panel-slide | Login/register panel slides in from the right |
| **pulseRed** | @keyframes | .status-dot | Red dot pulses (used on login/auth status) |
| **gridDrift** | @keyframes | (defined, may be used elsewhere) | Background grid position shifts |
| **transition (various)** | transition | nav links, buttons, inputs, cards, sidebar | Smooth hover/focus (0.2s ease, etc.) |

---

## 2. Where Each Animation Is Used — With Code

### 2.1 Global (All Pages) — Body Background

**File:** `frontend/src/styles.css`

**body::before** — Honeycomb pattern on the whole site:
```css
body::before {
  content: "";
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,..."); /* honeycomb SVG */
  background-size: 140px 121px;
  opacity: 0.12;
  animation: honeycombFloat 38s ease-in-out infinite;
  pointer-events: none;
  z-index: -1;
}
```
**What it does:** The honeycomb pattern **moves** (background-position) and **opacity** changes slowly over 38 seconds, looped. So the background feels slightly moving on every page.

**body::after** — Red glow overlay:
```css
body::after {
  content: "";
  position: fixed;
  inset: 0;
  background: radial-gradient(...);
  opacity: 0.2;
  animation: glowPulse 14s ease-in-out infinite;
  pointer-events: none;
  z-index: -1;
}
```
**What it does:** The red glow **pulses** (opacity goes up and down) over 14 seconds, infinite. Used on: **all pages** (global).

---

### 2.2 Welcome Page (`/`)

**Component:** `frontend/src/pages/Welcome.tsx`  
**Classes used:** `.welcome-page`, `.auth-bg`, `.honeycomb-split`, `.bright-flash`, `.glow-orb`, `.landing-panel`, `.landing-title`, `.landing-subtitle`, `.landing-support`, `.enter-button`, `.premium-button`, `.gradient-aura`, `.split-panel`, `.bright-flash.active`, `.honeycomb-split.active`.

- **.auth-bg** — `animation: bgFloat 40s ease-in-out infinite;`  
  **Code (styles.css):**
  ```css
  .auth-bg {
    position: absolute;
    inset: -10%;
    background: radial-gradient(circle at center, rgba(255, 26, 26, 0.18), transparent 55%);
    transform: translate(var(--bg-shift-x), var(--bg-shift-y));
    animation: bgFloat 40s ease-in-out infinite;
  }
  ```
  **What it does:** Background gradient **drifts** (translate) over 40s. Welcome.tsx also sets `--bg-shift-x` and `--bg-shift-y` on **mouse move** so the background shifts with the cursor.

- **.auth-page::before** — `animation: honeycombFloat 38s ease-in-out infinite;`  
  Same honeycomb as body, stronger on auth/welcome.

- **.auth-page::after** — `animation: glowPulse 14s ease-in-out infinite;`  
  Same glow pulse as body.

- **.glow-orb, .orb-one, .orb-two** — `animation: orbFloat 12s ease-in-out infinite;`  
  **Code:**
  ```css
  .glow-orb {
    position: absolute;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    filter: blur(40px);
    opacity: 0.6;
    animation: orbFloat 12s ease-in-out infinite;
  }
  .orb-two {
    animation-delay: 2s;  /* second orb starts 2s later */
  }
  ```
  **What it does:** Blurred orbs **move up and down** (translateY) over 12s. Second orb is delayed 2s.

- **.landing-panel** — `animation: fadeUp 0.8s ease;`  
  **What it does:** The whole welcome block (logo, title, button) **fades in and moves up** once when the page loads.

- **.landing-title** — `animation: fadeUp 0.8s ease;`  
  Same fade-up for the main title.

- **.landing-subtitle** — `animation: fadeUpDelay 0.8s ease 0.3s both;`  
  **What it does:** Same as fadeUp but **starts after 0.3s** so it appears after the title.

- **.landing-support** — `animation: fadeUpDelay 0.8s ease 0.4s both;`  
  Same idea, **0.4s delay** for a third step.

- **.honeycomb-split** — When user clicks “Enter System”, Welcome.tsx sets `honeycomb-split active` and `bright-flash active`:
  ```tsx
  // Welcome.tsx
  <div className={isTransitioning ? "honeycomb-split active" : "honeycomb-split"}>
    <div className="split-panel top-left" />
    <div className="split-panel top-right" />
    ...
  </div>
  <div className={isTransitioning ? "bright-flash active" : "bright-flash"} />
  ```
  **.honeycomb-split.active .split-panel** — `animation: splitOut 0.85s ease forwards;`  
  **Code (keyframes):**
  ```css
  @keyframes splitOut {
    0%   { transform: scale(1); }
    70%  { transform: translate(calc(var(--split-x) * 0.7), calc(var(--split-y) * 0.7)) scale(1.05); }
    100% { transform: translate(var(--split-x), var(--split-y)) scale(1.1); }
  }
  ```
  **What it does:** The four panels **move outward** (each has --split-x, --split-y) and **scale up** in 0.85s when leaving Welcome.

- **.bright-flash.active** — `animation: flashGlow 0.8s ease-out forwards;`  
  **Code (keyframes):**
  ```css
  @keyframes flashGlow {
    0%   { opacity: 0; transform: scale(0.98); }
    35%  { opacity: 0.85; transform: scale(1.01); }
    100% { opacity: 0; transform: scale(1.06); }
  }
  ```
  **What it does:** A **short red flash** (opacity up then down) and slight scale when transitioning to Login.

- **.premium-button** — `transition: transform 0.2s ease, box-shadow 0.2s ease;` and on hover `transform: scale(1.05)`.  
  **Where:** “Enter System” button. **What it does:** Button **scales up** and shadow changes on hover.

---

### 2.3 Login / Auth Page (`/auth`)

**Component:** `frontend/src/pages/Login.tsx`  
**Classes:** `.auth-page`, `.auth-panel-slide`, `.auth-card`, `.auth-branding`, `.auth-form-wrap`, `.status-dot`, `.template-card`, etc.

- **.auth-panel-slide** — `animation: slideInRight 0.6s ease;`  
  **Code (keyframes):**
  ```css
  @keyframes slideInRight {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  ```
  **What it does:** The **login/register panel** **slides in from the right** (40px → 0) and fades in when the auth page loads.

- **.auth-card** — `animation: floatIn 0.7s ease;`  
  **Code (keyframes):**
  ```css
  @keyframes floatIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  ```
  **What it does:** The **card** (form container) **floats up** a bit and fades in.

- **.auth-branding** — `animation: fadeUp 0.6s ease;`  
  **What it does:** Left-side branding block **fades up** when the page loads.

- **.auth-form-wrap** — `animation: fadeUp 0.6s ease;`  
  **What it does:** Form wrapper **fades up** when the page loads.

- **.status-dot** — `animation: pulseRed 1.4s ease-in-out infinite;`  
  **Where:** Login page “system status” dot. **What it does:** Red dot **pulses** (typically opacity or scale) to show “live” status. (If `pulseRed` keyframes are not in your styles.css, the name is still used here; you can add a simple keyframe that changes opacity or transform.)

- **.tab, .role-card, .primary, .toggle-visibility** — `transition: ... 0.2s ease` (or similar).  
  **What it does:** **Smooth hover/focus** on tabs, role cards, buttons, and inputs.

---

### 2.4 App Layout and Dashboard (After Login)

**Components:** `AppLayout.tsx`, `Dashboard.tsx`, etc.  
**Classes:** `.page`, `.card`, `.action-card`, `.info-card`, `.hero-card`, `.primary`, `.danger`, sidebar links.

- **.page** — `animation: fadeUp 0.4s ease;`  
  **Code:**
  ```css
  .page {
    padding: 24px;
    animation: fadeUp 0.4s ease;
  }
  ```
  **What it does:** **Every** app page content (Dashboard, People, Attendance, etc.) **fades up** when you open that page (because the content is inside `.page`).

- **.card** — No entrance animation; has **border/shadow transition** on hover in some variants.

- **.action-card** — `transition: transform 0.2s ease, box-shadow 0.2s ease;` and hover `transform: translateY(-2px)`.  
  **Where:** Dashboard “Quick Actions” cards. **What it does:** Card **lifts** a bit on hover.

- **.info-card** — `animation: cardFade 0.8s ease both;` and `transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;`.  
  **Code (keyframes):**
  ```css
  @keyframes cardFade {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  ```
  **What it does:** Info cards **fade up** once, then **smooth hover** (lift + shadow).

- **.primary, .danger** — `transition: transform 0.15s ease, box-shadow 0.2s ease;` and hover `transform: translateY(-1px)`.  
  **Where:** Buttons across the app. **What it does:** Buttons **lift slightly** and shadow changes on hover.

- **.sidebar nav a** — `transition: all 0.2s ease;`.  
  **Where:** Sidebar (Dashboard, Live Monitoring, People, Attendance, Settings). **What it does:** **Smooth** background/color change on hover and for active state.

---

### 2.5 Transitions (No Keyframes) — Used Everywhere

These are **transitions** (smooth change on hover/focus), not keyframe animations:

| Class | Property | Where used |
|-------|----------|------------|
| `.sidebar nav a` | `transition: all 0.2s ease` | Sidebar links |
| `.ghost-button` | `transition: all 0.2s ease` | Logout button |
| `.action-card` | `transition: transform 0.2s ease, box-shadow 0.2s ease` | Dashboard action cards |
| `.primary`, `.danger` | `transition: transform 0.15s ease, box-shadow 0.2s ease` | Buttons |
| `input`, `select` | `transition: border 0.2s ease, box-shadow 0.2s ease` | Form fields (focus) |
| `.info-card` | `transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease` | Info cards hover |
| `.honeycomb-split .split-panel` | `transition: opacity 0.2s ease` | Welcome split panels before active |
| `.role-card` | `transition: all 0.2s ease` | Login role selection |
| `.toggle-visibility` | `transition: box-shadow 0.2s ease, border 0.2s ease` | Password show/hide button |
| `.neon-outline` | `transition: transform 0.2s ease, box-shadow 0.2s ease` | Outline buttons on auth |

---

## 3. All @keyframes Definitions (Copy-Paste Reference)

**File:** `frontend/src/styles.css` (around lines 1340–1481)

```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeUpDelay {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes floatIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes bgFloat {
  0%   { transform: translate(-4%, -2%); }
  100% { transform: translate(4%, 3%); }
}

@keyframes honeycombFloat {
  0%, 100% { background-position: 0 0; opacity: 0.24; }
  50%      { background-position: 36px 18px; opacity: 0.3; }
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.18; }
  50%      { opacity: 0.28; }
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-18px); }
}

@keyframes cardFade {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes splitOut {
  0%   { transform: scale(1); }
  70%  { transform: translate(calc(var(--split-x) * 0.7), calc(var(--split-y) * 0.7)) scale(1.05); }
  100% { transform: translate(var(--split-x), var(--split-y)) scale(1.1); }
}

@keyframes flashGlow {
  0%   { opacity: 0; transform: scale(0.98); }
  35%  { opacity: 0.85; transform: scale(1.01); }
  100% { opacity: 0; transform: scale(1.06); }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(40px); }
  to   { opacity: 1; transform: translateX(0); }
}
```

**pulseRed** is used by `.status-dot` but if the keyframe is missing in your file, you can add:
```css
@keyframes pulseRed {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.7; transform: scale(1.1); }
}
```

---

## 4. Quick Summary Table (Animation → Where → File)

| Animation | Where used | Component / element | File |
|-----------|------------|----------------------|------|
| honeycombFloat | Body and auth background | body::before, .auth-page::before | styles.css |
| glowPulse | Body and auth overlay | body::after, .auth-page::after | styles.css |
| bgFloat | Welcome background | .auth-bg | styles.css |
| orbFloat | Welcome orbs | .glow-orb, .orb-one, .orb-two | styles.css |
| fadeUp | App pages, landing, auth blocks | .page, .landing-panel, .landing-title, .auth-branding, .auth-form-wrap | styles.css |
| fadeUpDelay | Landing subtitle/support | .landing-subtitle, .landing-support | styles.css |
| floatIn | Auth form card | .auth-card | styles.css |
| cardFade | Info cards | .info-card | styles.css |
| splitOut | Welcome “Enter” transition | .honeycomb-split.active .split-panel | styles.css |
| flashGlow | Welcome “Enter” flash | .bright-flash.active | styles.css |
| slideInRight | Login/register panel | .auth-panel-slide | styles.css |
| pulseRed | Status dot on login | .status-dot | styles.css |

Use this document to **see which animation is used where** and to **point to the exact code** in `frontend/src/styles.css` and the components (Welcome.tsx, Login.tsx, AppLayout, etc.).
