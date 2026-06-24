import React from  react;
import styles from ./HeroSection.module.css;

interface HeroSectionProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
}

const HeroSection: React.FC<HeroSectionProps> = ({ title, subtitle, children }) => (
  <section className={styles.hero}>
    <div className={styles.orbContainer}>
      <div className={styles.orb} />
      <div className={styles.orb} />
      <div className={styles.orb} />
    </div>
    <div className={styles.content}>
      <h1 className={styles.title}>{title}</h1>
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      {children}
    </div>
  </section>
);

export default HeroSection;
