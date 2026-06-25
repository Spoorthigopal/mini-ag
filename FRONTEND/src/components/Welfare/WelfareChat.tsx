import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { addWelfareChatMessage } from '../../redux/slices/welfareSlice';
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

    // Simulate bot response
    setTimeout(() => {
      let botResponse = "I can help you find scholarships. Could you specify if you are in Undergraduate or Postgraduate studies?";
      const inputLower = userMsgText.toLowerCase();

      if (inputLower.includes('undergrad') || inputLower.includes('ug') || inputLower.includes('bachelor')) {
        botResponse = "Excellent! For undergraduates, we have two prime matching schemes:\n\n1. **National Merit Scholarship Program** (₹50,000/yr) - open to all general categories.\n2. **Post-Matric Financial Aid** (₹25,000/sem) - specifically for SC/ST students.\n\nWhich of these would you like to explore or apply for?";
      } else if (inputLower.includes('postgrad') || inputLower.includes('pg') || inputLower.includes('master') || inputLower.includes('research')) {
        botResponse = "Great! For postgraduate and research students, we recommend the **University Excellence Grant for Research** (₹75,000). It is open to all categories and has a deadline of August 30, 2026. Would you like assistance with applying?";
      } else if (inputLower.includes('sc') || inputLower.includes('st')) {
        botResponse = "For SC/ST students, you are highly eligible for the **Post-Matric Financial Aid for SC/ST Students** which offers ₹25,000 per semester. The deadline is September 15, 2026. Let me know if you'd like to start your application!";
      } else if (inputLower.includes('minority')) {
        botResponse = "For minority group students, the **Minority Student Subsidy Fund** provided by Corporate CSR offers ₹15,000/year. The application is currently open until December 1, 2026. Would you like me to help you fill the form?";
      } else if (inputLower.includes('thank') || inputLower.includes('bye')) {
        botResponse = "You're welcome! Let me know if you need anything else. Good luck with your academics!";
      }

      dispatch(addWelfareChatMessage({
        sender: 'bot',
        text: botResponse,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
      setIsTyping(false);
    }, 1500);
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
