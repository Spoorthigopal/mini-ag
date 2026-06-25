import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: '2rem',
            background: 'rgba(255, 69, 58, 0.1)',
            border: '1px solid rgba(255, 69, 58, 0.2)',
            borderRadius: '0.75rem',
            margin: '1.5rem 0',
            color: '#ff453a',
            fontFamily: 'system-ui, sans-serif',
          }}
        >
          <h2 style={{ marginTop: 0, fontSize: '1.25rem' }}>Something went wrong.</h2>
          <details style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem', opacity: 0.8 }}>
            {this.state.error && this.state.error.toString()}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}
