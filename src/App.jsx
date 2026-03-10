import { useState, useEffect, useRef } from "react";

const GTMLanding = () => {
  const [scrollY, setScrollY] = useState(0);
  const [hoveredFeature, setHoveredFeature] = useState(null);
  const [hoveredDiff, setHoveredDiff] = useState(null);
  const [lineProgress, setLineProgress] = useState(0);
  const journeyRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
      const doc = document.documentElement;
      const progress = window.scrollY / (doc.scrollHeight - doc.clientHeight);
      setLineProgress(Math.min(progress * 1.5, 1));

      if (journeyRef.current) {
        const rect = journeyRef.current.getBoundingClientRect();
        const sectionProgress = Math.max(0, Math.min(1, (window.innerHeight - rect.top) / (window.innerHeight + rect.height)));
        setLineProgress(sectionProgress);
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const features = [
    { id: 1, label: "01", title: "ICP DEFINITION", desc: "Laser-sharp ideal customer profiles built from real signal, not guesswork." },
    { id: 2, label: "02", title: "MESSAGING SYSTEM", desc: "Positioning and copy that converts across every channel and touchpoint." },
    { id: 3, label: "03", title: "DISTRIBUTION ENGINE", desc: "Outbound + inbound sequences that run without you in the loop." },
    { id: 4, label: "04", title: "PIPELINE ARCHITECTURE", desc: "CRM structure, scoring models, and handoff logic built for scale." },
    { id: 5, label: "05", title: "FEEDBACK LOOPS", desc: "Win/loss analysis and iteration cadence baked into the system." },
    { id: 6, label: "06", title: "TRAINING + HANDOFF", desc: "Your team runs this. No retainer dependency. You own it." },
  ];

  const differentiators = [
    "SYSTEMS, NOT TACTICS",
    "NO RETAINER LOCK-IN",
    "BUILT FOR B2B / SAAS",
    "FOUNDER-LED INSTALLS",
    "4 WEEKS, NOT 4 MONTHS",
    "YOU OWN EVERYTHING",
  ];

  const timeline = [
    { week: "WEEK 1", title: "DISCOVERY + ICP", items: ["Founder interviews", "Market positioning audit", "ICP hypothesis mapping", "Competitor messaging teardown"] },
    { week: "WEEK 2", title: "MESSAGING + ASSETS", items: ["Core value proposition", "Outbound sequence copy", "Landing page copy", "LinkedIn profile overhaul"] },
    { week: "WEEK 3", title: "DISTRIBUTION SETUP", items: ["CRM architecture", "Outbound toolstack", "Sequence automation", "Lead scoring model"] },
    { week: "WEEK 4", title: "LAUNCH + TRAINING", items: ["Live campaign launch", "Team training sessions", "Playbook documentation", "6-month audit roadmap"] },
  ];

  const pipelineSteps = ["ICP", "MESSAGING", "DISTRIBUTION", "PIPELINE", "FEEDBACK"];

  return (
    <div style={{ fontFamily: "'DM Mono', 'Courier New', monospace", background: "#E3E2DE", color: "#141414", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { overflow-x: hidden; }
        .nav-link { text-decoration: none; color: #141414; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; transition: color 0.2s; cursor: pointer; }
        .nav-link:hover { color: #1351AA; }
        .feature-cell { border: 1px solid #141414; padding: 32px; cursor: default; transition: background 0.2s, color 0.2s; }
        .feature-cell:hover { background: #141414; color: #E3E2DE; }
        .diff-item { font-size: clamp(28px, 5vw, 64px); font-weight: 700; letter-spacing: -0.02em; padding: 20px 0; border-bottom: 1px solid #141414; cursor: default; transition: color 0.15s; display: flex; align-items: center; justify-content: space-between; font-family: 'Space Grotesk', sans-serif; }
        .diff-item:hover { color: #1351AA; }
        .diff-item:first-child { border-top: 1px solid #141414; }
        .pipe-step { flex: 1; text-align: center; padding: 24px 12px; border: 1px solid #141414; font-size: 11px; letter-spacing: 0.15em; font-weight: 500; position: relative; transition: background 0.2s, color 0.2s; cursor: default; }
        .pipe-step:hover { background: #1351AA; color: #E3E2DE; }
        .pipe-arrow { display: flex; align-items: center; padding: 0 4px; font-size: 18px; color: #141414; }
        .cta-btn { display: inline-block; background: #141414; color: #E3E2DE; padding: 18px 40px; font-size: 12px; letter-spacing: 0.15em; text-transform: uppercase; text-decoration: none; border: 2px solid #141414; cursor: pointer; transition: background 0.2s, color 0.2s; font-family: 'DM Mono', monospace; }
        .cta-btn:hover { background: #1351AA; border-color: #1351AA; }
        .cta-btn-outline { background: transparent; color: #141414; }
        .cta-btn-outline:hover { background: #141414; color: #E3E2DE; border-color: #141414; }
        .timeline-week { border-left: 3px solid #141414; padding-left: 32px; padding-bottom: 48px; position: relative; }
        .timeline-week::before { content: ''; position: absolute; left: -7px; top: 8px; width: 11px; height: 11px; background: #141414; }
        .timeline-week:last-child { padding-bottom: 0; }
        .timeline-week.active::before { background: #1351AA; }
        .section-label { font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: #141414; opacity: 0.5; margin-bottom: 8px; }
        .grid-line { border-top: 1px solid #141414; }
        .number-accent { font-size: clamp(80px, 15vw, 180px); font-weight: 700; line-height: 0.85; color: transparent; -webkit-text-stroke: 1px #141414; font-family: 'Space Grotesk', sans-serif; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .hero-animate { animation: fadeUp 0.9s ease forwards; }
        .hero-animate-delay { animation: fadeUp 0.9s ease 0.2s forwards; opacity: 0; }
        .hero-animate-delay2 { animation: fadeUp 0.9s ease 0.4s forwards; opacity: 0; }
        .scroll-indicator { animation: bounce 2s infinite; }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(6px); } }
      `}</style>

      {/* NAV */}
      <nav style={{ position: "sticky", top: 0, zIndex: 100, background: "#E3E2DE", borderBottom: "1px solid #141414", display: "grid", gridTemplateColumns: "repeat(12, 1fr)", padding: "0 40px", height: "56px", alignItems: "center" }}>
        <div style={{ gridColumn: "1 / 4", display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "8px", height: "8px", background: "#1351AA" }} />
          <span style={{ fontSize: "11px", letterSpacing: "0.15em", fontWeight: "500" }}>GTM ENGINE</span>
        </div>
        <div style={{ gridColumn: "4 / 10", display: "flex", justifyContent: "center", gap: "40px" }}>
          {["System", "Process", "Pricing", "Contact"].map(l => (
            <span key={l} className="nav-link">{l}</span>
          ))}
        </div>
        <div style={{ gridColumn: "10 / 13", display: "flex", justifyContent: "flex-end" }}>
          <span className="cta-btn" style={{ padding: "10px 24px", fontSize: "10px" }}>APPLY NOW →</span>
        </div>
      </nav>

      {/* HERO */}
      <section style={{ borderBottom: "1px solid #141414", display: "grid", gridTemplateColumns: "repeat(12, 1fr)", minHeight: "92vh", padding: "0 40px" }}>
        <div style={{ gridColumn: "1 / 2", borderRight: "1px solid #141414", display: "flex", flexDirection: "column", justifyContent: "flex-end", paddingBottom: "40px", paddingRight: "16px" }}>
          <div style={{ writingMode: "vertical-rl", transform: "rotate(180deg)", fontSize: "9px", letterSpacing: "0.2em", opacity: 0.4, textTransform: "uppercase" }}>GTM INSTALL 2025</div>
        </div>

        <div style={{ gridColumn: "2 / 10", padding: "80px 40px 80px 40px", display: "flex", flexDirection: "column", justifyContent: "center", borderRight: "1px solid #141414" }}>
          <div className="section-label hero-animate">B2B / SAAS GROWTH INFRASTRUCTURE</div>
          <h1 className="hero-animate" style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(52px, 8vw, 110px)", fontWeight: 700, lineHeight: 0.9, letterSpacing: "-0.03em", marginTop: "24px", marginBottom: "40px" }}>
            THE GTM<br />
            <span style={{ color: "#1351AA" }}>ENGINE</span><br />
            INSTALL.
          </h1>
          <p className="hero-animate-delay" style={{ fontSize: "15px", lineHeight: 1.6, maxWidth: "480px", opacity: 0.75, marginBottom: "48px" }}>
            A complete go-to-market system built, installed, and handed to your team in 4 weeks. ICP to pipeline. Messaging to distribution. You own it all.
          </p>
          <div className="hero-animate-delay2" style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
            <span className="cta-btn">GET THE SYSTEM →</span>
            <span className="cta-btn cta-btn-outline">SEE HOW IT WORKS</span>
          </div>
        </div>

        <div style={{ gridColumn: "10 / 13", padding: "80px 32px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <div>
            <div className="section-label">INSTALL DETAILS</div>
            <div style={{ marginTop: "24px" }}>
              {[["DURATION", "3–4 WEEKS"], ["FORMAT", "DONE-WITH-YOU"], ["CONTRACTS", "NONE"], ["RETAINER", "NOT REQUIRED"]].map(([k, v]) => (
                <div key={k} style={{ borderBottom: "1px solid rgba(20,20,20,0.2)", padding: "14px 0", display: "flex", justifyContent: "space-between", fontSize: "11px" }}>
                  <span style={{ opacity: 0.5, letterSpacing: "0.1em" }}>{k}</span>
                  <span style={{ fontWeight: "500", letterSpacing: "0.08em" }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="section-label">STARTING AT</div>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "42px", fontWeight: 700, letterSpacing: "-0.02em", marginTop: "8px" }}>$2,000<span style={{ fontSize: "16px", fontWeight: 400, opacity: 0.5 }}>+</span></div>
          </div>
        </div>
      </section>

      {/* PIPELINE VISUALIZATION */}
      <section style={{ borderBottom: "1px solid #141414", padding: "80px 40px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", marginBottom: "48px" }}>
          <div style={{ gridColumn: "1 / 3" }}>
            <div className="section-label">THE ENGINE</div>
            <div style={{ fontSize: "11px", marginTop: "8px", opacity: 0.5 }}>HOW IT FLOWS</div>
          </div>
          <div style={{ gridColumn: "3 / 13" }}>
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(28px, 4vw, 48px)", fontWeight: 700, letterSpacing: "-0.02em", lineHeight: 1 }}>
              FIVE INTERLOCKING<br />SYSTEMS. ONE ENGINE.
            </h2>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "stretch", gap: "0" }}>
          {pipelineSteps.map((step, i) => (
            <div key={step} style={{ display: "flex", alignItems: "center", flex: 1 }}>
              <div className="pipe-step" style={{ flex: 1 }}>
                <div style={{ fontSize: "9px", opacity: 0.4, marginBottom: "8px", letterSpacing: "0.2em" }}>0{i + 1}</div>
                <div>{step}</div>
              </div>
              {i < pipelineSteps.length - 1 && (
                <div className="pipe-arrow">→</div>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "0", marginTop: "0", borderTop: "1px solid #141414" }}>
          {[
            "Who you're selling to and why they buy.",
            "What you say and how you say it.",
            "How you reach them at scale.",
            "How deals move and close.",
            "How you get smarter every quarter.",
          ].map((desc, i) => (
            <div key={i} style={{ padding: "24px 20px", borderRight: i < 4 ? "1px solid #141414" : "none", fontSize: "12px", lineHeight: 1.6, opacity: 0.65 }}>{desc}</div>
          ))}
        </div>
      </section>

      {/* SYSTEM GRID */}
      <section style={{ borderBottom: "1px solid #141414", padding: "80px 40px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", marginBottom: "48px" }}>
          <div style={{ gridColumn: "1 / 3" }}>
            <div className="section-label">WHAT YOU GET</div>
          </div>
          <div style={{ gridColumn: "3 / 10" }}>
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(28px, 4vw, 52px)", fontWeight: 700, letterSpacing: "-0.02em", lineHeight: 1 }}>
              EVERY COMPONENT,<br />BUILT AND INSTALLED.
            </h2>
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0" }}>
          {features.map((f) => (
            <div
              key={f.id}
              className="feature-cell"
              onMouseEnter={() => setHoveredFeature(f.id)}
              onMouseLeave={() => setHoveredFeature(null)}
              style={{ borderRight: f.id % 3 === 0 ? "1px solid #141414" : "1px solid #141414", borderBottom: f.id > 3 ? "1px solid #141414" : "1px solid #141414" }}
            >
              <div style={{ fontSize: "10px", letterSpacing: "0.2em", opacity: 0.4, marginBottom: "20px" }}>{f.label}</div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "18px", fontWeight: 700, letterSpacing: "-0.01em", marginBottom: "12px" }}>{f.title}</div>
              <div style={{ fontSize: "12px", lineHeight: 1.7, opacity: 0.7 }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* 4-WEEK TIMELINE */}
      <section style={{ borderBottom: "1px solid #141414", padding: "80px 40px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: "40px" }}>
          <div style={{ gridColumn: "1 / 4", borderRight: "1px solid #141414", paddingRight: "40px" }}>
            <div className="section-label">THE PROCESS</div>
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(24px, 3vw, 40px)", fontWeight: 700, letterSpacing: "-0.02em", lineHeight: 1.1, marginTop: "16px" }}>
              WHAT GETS<br />INSTALLED<br />IN 4 WEEKS.
            </h2>
            <p style={{ fontSize: "12px", lineHeight: 1.8, marginTop: "24px", opacity: 0.65 }}>
              Every week has a clear deliverable. Every deliverable has a clear owner. You don't wait. You build.
            </p>
            <div style={{ marginTop: "32px", padding: "20px", border: "1px solid #141414", background: "rgba(19,81,170,0.05)" }}>
              <div className="section-label" style={{ marginBottom: "8px" }}>INCLUDED</div>
              <div style={{ fontSize: "11px", lineHeight: 2 }}>
                {["Full playbook documentation", "Team training sessions", "6-month audit cadence", "Async support channel"].map(i => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div style={{ width: "6px", height: "6px", background: "#1351AA", flexShrink: 0 }} />
                    {i}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div style={{ gridColumn: "4 / 13", paddingLeft: "40px" }}>
            {timeline.map((phase, idx) => (
              <div key={phase.week} className="timeline-week" style={{ borderLeft: `3px solid ${idx === 0 ? "#1351AA" : "#141414"}` }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: "16px", marginBottom: "16px" }}>
                  <span style={{ fontSize: "10px", letterSpacing: "0.2em", color: "#1351AA", fontWeight: 500 }}>{phase.week}</span>
                  <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "22px", fontWeight: 700, letterSpacing: "-0.01em" }}>{phase.title}</span>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "8px" }}>
                  {phase.items.map(item => (
                    <div key={item} style={{ fontSize: "12px", padding: "10px 14px", border: "1px solid rgba(20,20,20,0.2)", lineHeight: 1.4 }}>{item}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WHY DIFFERENT */}
      <section style={{ borderBottom: "1px solid #141414", padding: "80px 40px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", marginBottom: "48px" }}>
          <div style={{ gridColumn: "1 / 3" }}>
            <div className="section-label">WHY DIFFERENT</div>
          </div>
          <div style={{ gridColumn: "3 / 10" }}>
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(28px, 4vw, 52px)", fontWeight: 700, letterSpacing: "-0.02em", lineHeight: 1 }}>
              NOT AN AGENCY.<br />NOT A CONSULTANT.<br />
              <span style={{ color: "#1351AA" }}>A SYSTEM INSTALL.</span>
            </h2>
          </div>
        </div>
        <div>
          {differentiators.map((d, i) => (
            <div key={d} className="diff-item" onMouseEnter={() => setHoveredDiff(i)} onMouseLeave={() => setHoveredDiff(null)}>
              <span>{d}</span>
              <span style={{ fontSize: "14px", opacity: hoveredDiff === i ? 1 : 0, color: "#1351AA", transition: "opacity 0.15s", letterSpacing: "0.1em" }}>→</span>
            </div>
          ))}
        </div>
      </section>

      {/* FOUNDER TRUST */}
      <section style={{ borderBottom: "1px solid #141414", padding: "80px 40px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: "40px" }}>
          <div style={{ gridColumn: "1 / 3", borderRight: "1px solid #141414", paddingRight: "40px" }}>
            <div className="section-label">BUILT FOR</div>
            <div className="number-accent" style={{ marginTop: "24px" }}>B2B</div>
          </div>
          <div style={{ gridColumn: "3 / 8", paddingRight: "40px", borderRight: "1px solid #141414" }}>
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(24px, 3vw, 40px)", fontWeight: 700, letterSpacing: "-0.02em", lineHeight: 1.2, marginBottom: "24px" }}>
              MADE FOR FOUNDERS WHO WANT TO STOP GUESSING.
            </h2>
            <p style={{ fontSize: "13px", lineHeight: 1.8, opacity: 0.7 }}>
              You know your product works. The problem is everything around it — the messaging is scattered, the outbound is inconsistent, the pipeline is unpredictable. We fix the infrastructure so your team can execute.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "16px", marginTop: "32px" }}>
              {["B2B SaaS", "Early-stage", "Series A", "Founder-led sales", "No GTM team", "First 10 customers"].map(tag => (
                <div key={tag} style={{ border: "1px solid #141414", padding: "10px 16px", fontSize: "11px", letterSpacing: "0.1em" }}>{tag}</div>
              ))}
            </div>
          </div>
          <div style={{ gridColumn: "8 / 13" }}>
            <div className="section-label" style={{ marginBottom: "24px" }}>THE PROMISE</div>
            {[
              ["SYSTEMS OVER TACTICS", "We don't give you a list of things to try. We install a machine."],
              ["NO LONG CONTRACTS", "Engage for the install. Optimize on your own. Return if needed."],
              ["YOU OWN THE SYSTEM", "Every doc, every playbook, every sequence is yours forever."],
            ].map(([title, desc]) => (
              <div key={title} style={{ borderBottom: "1px solid rgba(20,20,20,0.2)", paddingBottom: "20px", marginBottom: "20px" }}>
                <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "14px", fontWeight: 700, marginBottom: "6px" }}>{title}</div>
                <div style={{ fontSize: "12px", opacity: 0.65, lineHeight: 1.6 }}>{desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section style={{ borderBottom: "1px solid #141414", padding: "80px 40px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: "0" }}>
          <div style={{ gridColumn: "1 / 3", borderRight: "1px solid #141414", paddingRight: "40px" }}>
            <div className="section-label">INVESTMENT</div>
          </div>
          <div style={{ gridColumn: "3 / 13", paddingLeft: "40px" }}>
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(28px, 3.5vw, 52px)", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: "48px" }}>
              ONE PRICE.<br />EVERYTHING INCLUDED.
            </h2>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)" }}>
          <div style={{ gridColumn: "3 / 13", paddingLeft: "40px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0", border: "2px solid #141414" }}>
              <div style={{ padding: "48px", borderRight: "1px solid #141414" }}>
                <div className="section-label" style={{ marginBottom: "24px" }}>GTM ENGINE INSTALL</div>
                <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(52px, 8vw, 96px)", fontWeight: 700, letterSpacing: "-0.04em", lineHeight: 1 }}>
                  $2,000
                  <span style={{ fontSize: "24px", fontWeight: 400, opacity: 0.4 }}>+</span>
                </div>
                <div style={{ marginTop: "8px", fontSize: "12px", opacity: 0.5 }}>Scoped to your business</div>
                <div style={{ marginTop: "40px" }}>
                  <span className="cta-btn" style={{ display: "block", textAlign: "center" }}>APPLY FOR AN INSTALL →</span>
                </div>
              </div>
              <div style={{ padding: "48px" }}>
                <div className="section-label" style={{ marginBottom: "24px" }}>WHAT'S INCLUDED</div>
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  {[
                    "3–4 week system build",
                    "ICP + messaging framework",
                    "Distribution sequences",
                    "CRM + pipeline architecture",
                    "Team training sessions",
                    "Full playbook documentation",
                    "6-month optimization audits",
                    "Async support (30 days)",
                  ].map(item => (
                    <div key={item} style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "13px", borderBottom: "1px solid rgba(20,20,20,0.15)", paddingBottom: "12px" }}>
                      <div style={{ width: "6px", height: "6px", background: "#1351AA", flexShrink: 0 }} />
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: "120px 40px", background: "#141414", color: "#E3E2DE" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)" }}>
          <div style={{ gridColumn: "1 / 3", borderRight: "1px solid rgba(227,226,222,0.2)", paddingRight: "40px" }}>
            <div style={{ fontSize: "10px", letterSpacing: "0.2em", opacity: 0.4, textTransform: "uppercase" }}>READY TO BUILD</div>
          </div>
          <div style={{ gridColumn: "3 / 11", paddingLeft: "40px", paddingRight: "40px" }}>
            <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: "clamp(36px, 6vw, 86px)", fontWeight: 700, letterSpacing: "-0.03em", lineHeight: 0.9, marginBottom: "48px" }}>
              STOP RUNNING<br />TACTICS.<br />
              <span style={{ color: "#1351AA" }}>BUILD THE SYSTEM.</span>
            </h2>
            <p style={{ fontSize: "14px", lineHeight: 1.8, opacity: 0.6, maxWidth: "480px", marginBottom: "48px" }}>
              Applications are reviewed within 48 hours. If there's a fit, we'll schedule a 30-minute scoping call and get started within the week.
            </p>
            <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
              <span style={{ display: "inline-block", background: "#1351AA", color: "#E3E2DE", padding: "18px 40px", fontSize: "12px", letterSpacing: "0.15em", textTransform: "uppercase", cursor: "pointer" }}>
                APPLY NOW →
              </span>
              <span style={{ display: "inline-block", border: "1px solid rgba(227,226,222,0.4)", color: "#E3E2DE", padding: "18px 40px", fontSize: "12px", letterSpacing: "0.15em", textTransform: "uppercase", cursor: "pointer" }}>
                BOOK A CALL
              </span>
            </div>
          </div>
          <div style={{ gridColumn: "11 / 13", display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "flex-end" }}>
            <div style={{ fontSize: "10px", letterSpacing: "0.15em", opacity: 0.3, textAlign: "right" }}>
              <div>LIMITED</div>
              <div>SPOTS</div>
              <div>AVAILABLE</div>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{ borderTop: "1px solid rgba(227,226,222,0.2)", background: "#141414", padding: "32px 40px", display: "grid", gridTemplateColumns: "repeat(12, 1fr)", color: "#E3E2DE" }}>
        <div style={{ gridColumn: "1 / 5", fontSize: "11px", opacity: 0.4, letterSpacing: "0.1em" }}>
          © 2025 GTM ENGINE. ALL RIGHTS RESERVED.
        </div>
        <div style={{ gridColumn: "5 / 9", display: "flex", gap: "32px", justifyContent: "center" }}>
          {["PRIVACY", "TERMS", "CONTACT"].map(l => (
            <span key={l} style={{ fontSize: "10px", letterSpacing: "0.15em", opacity: 0.4, cursor: "pointer" }}>{l}</span>
          ))}
        </div>
        <div style={{ gridColumn: "9 / 13", display: "flex", justifyContent: "flex-end", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "6px", height: "6px", background: "#1351AA" }} />
          <span style={{ fontSize: "10px", letterSpacing: "0.15em", opacity: 0.4 }}>SYSTEMS OVER TACTICS</span>
        </div>
      </footer>
    </div>
  );
};

function App() {
  return <GTMLanding />;
}

export default App;