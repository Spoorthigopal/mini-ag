import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { addWelfareChatMessage } from '../../redux/slices/welfareSlice';
import { sendWelfareChatMessage } from '../../services/welfareService';
import { MessageCircle, X, Maximize2, Minimize2, Send, Sparkles, ExternalLink, GripVertical } from 'lucide-react';
import styles from './welfare.module.css';

const MIN_WIDTH = 320;
const MIN_HEIGHT = 380;
const DEFAULT_WIDTH = 380;
const DEFAULT_HEIGHT = 500;

export const SchemeAssistChatbot: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const chatHistory = useSelector((state: RootState) => state.welfare.chatHistory);

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const hasInitialized = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Drag state
  const [position, setPosition] = useState({ x: window.innerWidth - DEFAULT_WIDTH - 32, y: window.innerHeight - DEFAULT_HEIGHT - 100 });
  const isDragging = useRef(false);
  const dragOffset = useRef({ x: 0, y: 0 });

  // Resize state
  const [size, setSize] = useState({ width: DEFAULT_WIDTH, height: DEFAULT_HEIGHT });
  const isResizing = useRef(false);
  const resizeStart = useRef({ x: 0, y: 0, width: 0, height: 0 });

  const cardRef = useRef<HTMLDivElement>(null);

  // Initialize welcome message
  useEffect(() => {
    if (chatHistory.length === 0 && !hasInitialized.current) {
      hasInitialized.current = true;
      dispatch(addWelfareChatMessage({
        sender: 'bot',
        text: "Hi! 👋 I'm Scheme Assist — your welfare & scholarship guide. Tell me your academic profile (e.g. UG, SC/ST, Minority) and I'll find the best schemes for you!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    }
  }, [dispatch, chatHistory.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isTyping]);

  // Drag handlers
  const handleDragStart = useCallback((e: React.MouseEvent) => {
    isDragging.current = true;
    dragOffset.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    };
    e.preventDefault();
  }, [position]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging.current) {
        const newX = Math.max(0, Math.min(window.innerWidth - size.width, e.clientX - dragOffset.current.x));
        const newY = Math.max(0, Math.min(window.innerHeight - 60, e.clientY - dragOffset.current.y));
        setPosition({ x: newX, y: newY });
      }
      if (isResizing.current) {
        const dx = e.clientX - resizeStart.current.x;
        const dy = e.clientY - resizeStart.current.y;
        const newWidth = Math.max(MIN_WIDTH, resizeStart.current.width + dx);
        const newHeight = Math.max(MIN_HEIGHT, resizeStart.current.height + dy);
        setSize({ width: newWidth, height: newHeight });
      }
    };

    const handleMouseUp = () => {
      isDragging.current = false;
      isResizing.current = false;
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [size.width]);

  const handleResizeStart = (e: React.MouseEvent) => {
    isResizing.current = true;
    resizeStart.current = {
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height,
    };
    e.preventDefault();
    e.stopPropagation();
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMsgText = inputText;
    setInputText('');

    dispatch(addWelfareChatMessage({
      sender: 'user',
      text: userMsgText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }));

    setIsTyping(true);

    try {
      const data = await sendWelfareChatMessage({ query: userMsgText });
      dispatch(addWelfareChatMessage({
        sender: 'bot',
        text: data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    } catch {
      dispatch(addWelfareChatMessage({
        sender: 'bot',
        text: "I'm having trouble connecting right now. Please try again shortly.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    } finally {
      setIsTyping(false);
    }
  };

  const handleExpandToPage = () => {
    navigate('/welfare/chat');
  };

  return (
    <>
      {/* Floating FAB Button */}
      {!isOpen && (
        <button
          className={styles.chatFab}
          onClick={() => setIsOpen(true)}
          title="Open Scheme Assist"
          aria-label="Open Scheme Assist chatbot"
        >
          <Sparkles size={22} />
          <span className={styles.chatFabLabel}>Scheme Assist</span>
        </button>
      )}

      {/* Floating Chat Card */}
      {isOpen && (
        <div
          ref={cardRef}
          className={styles.floatingCard}
          style={{
            left: position.x,
            top: position.y,
            width: size.width,
            height: isMinimized ? 56 : size.height,
          }}
        >
          {/* Drag Handle / Header */}
          <div
            className={styles.floatingHeader}
            onMouseDown={handleDragStart}
            style={{ cursor: 'grab' }}
          >
            <div className={styles.floatingHeaderLeft}>
              <GripVertical size={14} style={{ color: 'rgba(255,255,255,0.3)', flexShrink: 0 }} />
              <div className={styles.floatingBotAvatar}>
                <Sparkles size={14} />
              </div>
              <div>
                <div className={styles.floatingBotName}>Scheme Assist</div>
                <div className={styles.floatingBotStatus}>
                  <span className={styles.chatStatusDot} />
                  AI Powered
                </div>
              </div>
            </div>
            <div className={styles.floatingHeaderActions}>
              <button
                className={styles.floatingHeaderBtn}
                onClick={(e) => { e.stopPropagation(); handleExpandToPage(); }}
                title="Open in full page"
              >
                <ExternalLink size={14} />
              </button>
              <button
                className={styles.floatingHeaderBtn}
                onClick={(e) => { e.stopPropagation(); setIsMinimized(m => !m); }}
                title={isMinimized ? 'Expand' : 'Minimize'}
              >
                {isMinimized ? <Maximize2 size={14} /> : <Minimize2 size={14} />}
              </button>
              <button
                className={`${styles.floatingHeaderBtn} ${styles.floatingCloseBtn}`}
                onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
                title="Close"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          {/* Chat Body */}
          {!isMinimized && (
            <>
              <div className={styles.floatingMessageList}>
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`${styles.messageRow} ${msg.sender === 'user' ? styles.userRow : styles.botRow}`}>
                    <div className={`${styles.messageBubble} ${msg.sender === 'user' ? styles.userBubble : styles.botBubble}`}>
                      <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
                      <span className={styles.messageTime}>{msg.timestamp}</span>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className={`${styles.messageRow} ${styles.botRow}`}>
                    <div className={styles.typingIndicator}>
                      <div className={styles.typingDot} />
                      <div className={styles.typingDot} />
                      <div className={styles.typingDot} />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={handleSend} className={styles.floatingInputArea}>
                <input
                  type="text"
                  placeholder="Ask about schemes, scholarships..."
                  className={styles.floatingInput}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  disabled={isTyping}
                />
                <button type="submit" className={styles.floatingSendBtn} disabled={!inputText.trim() || isTyping}>
                  <Send size={15} />
                </button>
              </form>

              {/* Resize Handle */}
              <div
                className={styles.resizeHandle}
                onMouseDown={handleResizeStart}
                title="Drag to resize"
              />
            </>
          )}
        </div>
      )}
    </>
  );
};

export default SchemeAssistChatbot;
