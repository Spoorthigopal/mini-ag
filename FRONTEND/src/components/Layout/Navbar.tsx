import React, { useState } from  react;
import styles from ./Navbar.module.css;
import { Search, Bell, Menu } from lucide-react;

const Navbar: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const toggleMenu = () => setMobileOpen(!mobileOpen);

  return (
    <nav className={styles.navbar}>
      <div className={styles.brand}>MyApp</div>
      <div className={styles.actions}>
        <button className={styles.iconButton} aria-label=Search><Search size={20} /></button>
        <button className={styles.iconButton} aria-label=Notifications><Bell size={20} /></button>
        <div className={styles.avatar}>U</div>
        <button className={styles.menuButton} onClick={toggleMenu} aria-label=Menu><Menu size={24} /></button>
      </div>
      {mobileOpen && (
        <div className={styles.mobileMenu}>/* Mobile links can go here */</div>
      )}
    </nav>
  );
};

export default Navbar;
