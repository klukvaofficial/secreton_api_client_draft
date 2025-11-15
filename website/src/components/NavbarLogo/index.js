import React from 'react';
import styles from './styles.module.css';

export default function NavbarLogo() {
  return (
    <p className={styles.logo}>
      secret<span className={styles.logoGradient}>On</span>
    </p>
  );
}

