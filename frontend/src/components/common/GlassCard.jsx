import styles from "./GlassCard.module.css";

export default function GlassCard({ children, className = "", ...props }) {
  return (
    <div className={`${styles.glass} ${className}`} {...props}>
      {children}
    </div>
  );
}
