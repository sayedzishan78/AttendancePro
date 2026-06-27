import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const Welcome = () => {
  const navigate = useNavigate();
  const authRef = useRef<HTMLDivElement>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const target = authRef.current;
    if (!target) return;
    const rect = target.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    target.style.setProperty("--bg-shift-x", `${x * 40}px`);
    target.style.setProperty("--bg-shift-y", `${y * 40}px`);
  };

  const handleMouseLeave = () => {
    const target = authRef.current;
    if (!target) return;
    target.style.setProperty("--bg-shift-x", "0px");
    target.style.setProperty("--bg-shift-y", "0px");
  };

  const handleEnter = () => {
    if (isTransitioning) return;
    setIsTransitioning(true);
    window.setTimeout(() => {
      navigate("/auth");
    }, 900);
  };

  return (
    <div
      className="auth-page welcome-page"
      ref={authRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="auth-bg" />
      <div className={isTransitioning ? "honeycomb-split active" : "honeycomb-split"}>
        <div className="split-panel top-left" />
        <div className="split-panel top-right" />
        <div className="split-panel bottom-left" />
        <div className="split-panel bottom-right" />
      </div>
      <div className={isTransitioning ? "bright-flash active" : "bright-flash"} />
      <div className="glow-orb orb-one" />
      <div className="glow-orb orb-two" />
      <div className="landing-panel">
        <div className="brand-bar">
          <div className="logo-icon" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div className="logo-text">AttendancePro</div>
        </div>
        <div className="landing-glow" />
        <h1 className="landing-title">
          <span className="gradient-aura">Welcome to AttendancePro</span>
        </h1>
        <p className="landing-subtitle">AI-Based Webcam Attendance System</p>
        <button
          className="primary enter-button premium-button"
          onClick={handleEnter}
          disabled={isTransitioning}
        >
          Enter System
        </button>
      </div>
    </div>
  );
};

export default Welcome;
