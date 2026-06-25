import React from 'react';
import styles from './HeroSection.module.css';

interface HeroSectionProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ title, subtitle, children }) => (
  <section className={styles.hero}>
    <div className={styles.orbContainer}>
      <div className={`${styles.orb} ${styles.orb1}`} />
      <div className={`${styles.orb} ${styles.orb2}`} />
      <div className={`${styles.orb} ${styles.orb3}`} />
    </div>
    <div className={styles.content}>
      <h1 className={styles.title}>{title}</h1>
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      {children}
    </div>
  </section>
);

export default HeroSection;
