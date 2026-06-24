import React from 'react';
import styles from './Button.module.css';
import { Loader2 } from 'lucide-react';

export type ButtonVariant = 'primary' | 'secondary' | 'danger';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  loading = false,
  disabled,
  children,
  ...rest
}) => {
  const isDisabled = disabled || loading;
  return (
    <button
      className={`
        ${styles.button}
        ${styles[variant]}
        ${isDisabled ? styles.disabled : ''}
        ${loading ? styles.loading : ''}
      `}
      disabled={isDisabled}
      {...rest}
    >
      {loading && <Loader2 size={16} className="spin" />}
      {children}
    </button>
  );
};
