import { NavLink } from "react-router-dom";
import styles from "./Layout.module.css";

const navItems = [
  { to: "/dashboard", label: "Live", icon: "◉" },
  { to: "/analytics", label: "Analytics", icon: "◈" },
  { to: "/alerts", label: "Alerts", icon: "⚠" },
  { to: "/settings", label: "Settings", icon: "⚙" },
];

export default function Sidebar({ onCameraSelect }) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>CrowdSense AI</div>
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.linkActive : ""}`
            }
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
