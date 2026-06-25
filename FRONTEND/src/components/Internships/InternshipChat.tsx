import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { addInternshipChatMessage } from '../../redux/slices/internshipSlice';
import styles from './internships.module.css';
import { Send, Sparkles } from 'lucide-react';

export const InternshipChat: React.FC = () => {
  const dispatch = useDispatch();
  const chatHistory = useSelector((state: RootState) => state.internship.chatHistory);
  const { resumeData } = useSelector((state: RootState) => state.internship);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isTyping]);

  useEffect(() => {
    if (chatHistory.length === 0) {
      dispatch(addInternshipChatMessage({
        sender: 'bot',
        text: "Hello! I'm your STU-MINI Internship & Resume Assistant. Upload your resume in the uploader tab, or tell me what roles you're searching for (e.g. Frontend, Data Analyst), and I will provide tailored job advice and resume enhancement tips!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    }
  }, [dispatch, chatHistory.length]);

  useEffect(() => {
    // React to resume upload
    if (resumeData.fileName && chatHistory.length > 0 && chatHistory[chatHistory.length - 1].text.indexOf(resumeData.fileName) === -1) {
      dispatch(addInternshipChatMessage({
        sender: 'bot',
        text: `I noticed you uploaded your resume: **${resumeData.fileName}**! Based on my quick parse, I found skills like: **${resumeData.parsedData?.skills?.join(', ')}**.\n\nI recommend applying for: \n1. **Software Engineer Intern** at TechCorp Solutions (92% match)\n2. **Frontend Developer Intern** at PixelPerfect Web (89% match)\n\nWould you like me to help draft a cover letter or optimize your resume for these roles?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    }
  }, [resumeData.fileName, resumeData.parsedData]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMsgText = inputText;
    setInputText('');

    dispatch(addInternshipChatMessage({
      sender: 'user',
      text: userMsgText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }));

    setIsTyping(true);

    setTimeout(() => {
      let botResponse = "I can guide you through career opportunities. Have you uploaded your resume yet?";
      const inputLower = userMsgText.toLowerCase();

      if (inputLower.includes('frontend') || inputLower.includes('react') || inputLower.includes('ui')) {
        botResponse = "For Frontend development, we highly recommend focusing on **React, TypeScript, and CSS Modules**. We have an opening at **PixelPerfect Web** offering ₹25,000/month which matches frontend skills perfectly. Would you like some mock interview questions on React?";
      } else if (inputLower.includes('backend') || inputLower.includes('python') || inputLower.includes('api')) {
        botResponse = "For Backend roles, deep knowledge of **Python, databases (PostgreSQL/SQL), and REST APIs** is crucial. **Innovate Digital** is seeking a Backend Intern in Mumbai (₹30,000/month). I can help you prepare backend mock questions!";
      } else if (inputLower.includes('cover letter') || inputLower.includes('coverletter')) {
        botResponse = "Sure! Here is a simple, premium template you can customize:\n\n*\"Dear Hiring Team, I am writing to express my strong interest in the Frontend Intern position. Having worked with React, TypeScript, and state-management tools like Redux, I am excited to contribute...\"*\n\nWould you like me to tailor it specifically for TechCorp Solutions?";
      } else if (inputLower.includes('thank') || inputLower.includes('bye')) {
        botResponse = "My pleasure! Don't hesitate to ask if you need further career mentoring. Good luck!";
      }

      dispatch(addInternshipChatMessage({
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
        <Sparkles size={20} style={{ color: '#30d158' }} />
        <div>
          <h3 className={styles.chatTitle}>Internship Assistant AI</h3>
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
          placeholder="Ask for resume optimization, cover letters, or job advice..."
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

export default InternshipChat;
