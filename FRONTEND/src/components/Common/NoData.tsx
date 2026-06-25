import React from 'react';
import { Inbox } from 'lucide-react';

export interface NoDataProps {
  message?: string;
}

export const NoData: React.FC<NoDataProps> = ({
  message = 'No data available at the moment.',
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 1.5rem',
        textAlign: 'center',
        color: 'rgba(255, 255, 255, 0.5)',
      }}
    >
      <Inbox size={48} strokeWidth={1.5} style={{ marginBottom: '1rem' }} />
      <p style={{ fontSize: '0.9375rem', margin: 0 }}>{message}</p>
    </div>
  );
};
