import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { addWelfareChatMessage } from '../../redux/slices/welfareSlice';
import { sendWelfareChatMessage } from '../../services/welfareService';
import styles from './welfare.module.css';
import { Send, Sparkles } from 'lucide-react';

export const WelfareChat: React.FC = () => {
  const dispatch = useDispatch();
  const chatHistory = useSelector((state: RootState) => state.welfare.chatHistory);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasInitialized = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isTyping]);

  useEffect(() => {
    // Add initial message if history is empty
    if (chatHistory.length === 0 && !hasInitialized.current) {
      hasInitialized.current = true;
      dispatch(addWelfareChatMessage({
        sender: 'bot',
        text: "Hello! I'm your GradSphere Welfare Assistant. Describe your academic profile (e.g. Undergraduate, SC/ST, Minority, General) and I'll recommend the best schemes and scholarships for you!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    }
  }, [dispatch, chatHistory.length]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMsgText = inputText;
    setInputText('');

    // Add user message
    dispatch(addWelfareChatMessage({
      sender: 'user',
      text: userMsgText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }));

    // Trigger typing indicator
    setIsTyping(true);

    try {
      const data = await sendWelfareChatMessage({ query: userMsgText });
      
      dispatch(addWelfareChatMessage({
        sender: 'bot',
        text: data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    } catch (error) {
      console.error("Error sending message to welfare bot:", error);
      dispatch(addWelfareChatMessage({
        sender: 'bot',
        text: "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <Sparkles size={20} style={{ color: '#0a84ff' }} />
        <div>
          <h3 className={styles.chatTitle}>Welfare Assistant AI</h3>
          <span className={styles.chatStatus}>
            <span className={styles.chatStatusDot}></span> Online
          </span>
        </div>
      </div>

      <div className={styles.messageList}>
        {chatHistory.map((msg, index) => (
          <div 
            key={index} 
            className={`${styles.messageRow} ${msg.sender === 'user' ? styles.userRow : styles.botRow}`}
          >
            <div className={`${styles.messageBubble} ${msg.sender === 'user' ? styles.userBubble : styles.botBubble}`}>
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
              <span className={styles.messageTime}>{msg.timestamp}</span>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className={`${styles.messageRow} ${styles.botRow}`}>
            <div className={styles.typingIndicator}>
              <div className={styles.typingDot}></div>
              <div className={styles.typingDot}></div>
              <div className={styles.typingDot}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className={styles.inputArea}>
        <input
          type="text"
          placeholder="Ask about scholarships, grants, or eligibility..."
          className={styles.chatInput}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isTyping}
        />
        <button type="submit" className={styles.sendBtn} disabled={!inputText.trim() || isTyping}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};

export default WelfareChat;
