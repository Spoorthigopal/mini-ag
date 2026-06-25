import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { addMessage, setFeedback, endSession } from '../../redux/slices/interviewSlice';
import styles from './interview.module.css';
import { Send, Sparkles, CheckCircle2, Award, ShieldAlert, ArrowRight } from 'lucide-react';

export const MockInterview: React.FC = () => {
  const dispatch = useDispatch();
  const { currentJob, messages, feedback, isActive } = useSelector((state: RootState) => state.interview);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [questionIndex, setQuestionIndex] = useState(0);

  const questions: Record<string, string[]> = {
    '1': [
      "Welcome to the Software Engineer Intern mock interview! Let's start: Can you explain the difference between state and props in React?",
      "Excellent. Next question: What is the benefit of using Redux Toolkit over vanilla Redux?",
      "Great. Last question: How does TypeScript help prevent bugs in large react applications?",
    ],
    '2': [
      "Welcome to the Data Analyst Intern mock interview! First question: How do you handle missing or null values in a dataset using Python or SQL?",
      "Understood. Next question: What is the difference between a left join and an inner join in SQL?",
      "Last question: Can you describe a scenario where you would use a line chart versus a bar chart?",
    ],
    '3': [
      "Welcome to the Backend Developer Intern mock interview! Let's begin: Can you explain how REST APIs handle CRUD operations?",
      "Great. Next question: How do you optimize slow database queries in PostgreSQL or MySQL?",
      "Last question: What is the difference between synchronous and asynchronous code execution in a backend environment?",
    ],
  };

  const activeQuestions = currentJob ? questions[currentJob.id] || [] : [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    // Inject first question when interview starts
    if (isActive && messages.length === 0 && activeQuestions.length > 0) {
      setIsTyping(true);
      setTimeout(() => {
        dispatch(addMessage({
          sender: 'bot',
          text: activeQuestions[0],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }));
        setIsTyping(false);
      }, 1000);
    }
  }, [isActive, dispatch, currentJob, messages.length]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userAns = inputText;
    setInputText('');

    // Add user's answer
    dispatch(addMessage({
      sender: 'user',
      text: userAns,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }));

    setIsTyping(true);

    setTimeout(() => {
      const nextIndex = questionIndex + 1;
      if (nextIndex < activeQuestions.length) {
        setQuestionIndex(nextIndex);
        dispatch(addMessage({
          sender: 'bot',
          text: `Got it. Let's move on. \n\n${activeQuestions[nextIndex]}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }));
        setIsTyping(false);
      } else {
        // Interview complete, generate feedback
        dispatch(endSession());
        
        let score = 85;
        let strengths = ["Clear technical vocabulary and concepts.", "Demonstrated understanding of core tools.", "Logical structuring of answers."];
        let improvements = ["Could include practical, real-world examples to substantiate theories.", "Can expand on specific edge cases in React state lifecycle."];
        
        if (currentJob?.id === '2') {
          score = 80;
          strengths = ["Strong SQL join understanding.", "Accurate descriptions of chart choices."];
          improvements = ["Be more specific about pandas functions like fillna() or dropna().", "Explain how outliers can impact statistical aggregates."];
        } else if (currentJob?.id === '3') {
          score = 88;
          strengths = ["Excellent grasp of REST methodologies.", "Database optimization strategies were spot-on."];
          improvements = ["Briefly touch upon indexing mechanism and explain plans.", "Mention async/await event loops for asynchronous questions."];
        }

        dispatch(setFeedback({
          score,
          strengths,
          improvements,
          summary: "You did a fantastic job! You showed thorough understanding of key domain concepts. Implementing minor improvements around practical edge cases will elevate your scores further.",
        }));
        setIsTyping(false);
      }
    }, 1500);
  };

  if (feedback) {
    return (
      <div className={styles.feedbackCard}>
        <h3 className={styles.feedbackTitle}>
          <CheckCircle2 size={24} style={{ color: '#30d158' }} /> Interview Feedback & Evaluation
        </h3>
        
        <div className={styles.scoreContainer}>
          <div className={styles.scoreGauge} style={{
            background: `conic-gradient(#0a84ff 0%, #0a84ff ${feedback.score}%, rgba(255, 255, 255, 0.1) ${feedback.score}%, rgba(255, 255, 255, 0.1) 100%)`
          }}>
            <div className={styles.scoreInner}>{feedback.score}%</div>
          </div>
          <div className={styles.scoreText}>
            <span className={styles.scoreLabel}>Overall Score</span>
            <h4 className={styles.scoreHeading}>Awesome performance!</h4>
          </div>
        </div>

        <p style={{ fontStyle: 'italic', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
          {feedback.summary}
        </p>

        <div className={styles.feedbackGrid}>
          <div className={styles.feedbackSection}>
            <h4 className={`${styles.sectionHeader} ${styles.strengthTitle}`}>
              <Award size={18} /> Strengths
            </h4>
            <ul className={styles.bulletList}>
              {feedback.strengths.map((str, i) => (
                <li key={i}>{str}</li>
              ))}
            </ul>
          </div>

          <div className={styles.feedbackSection}>
            <h4 className={`${styles.sectionHeader} ${styles.improvementTitle}`}>
              <ShieldAlert size={18} /> Areas of Improvement
            </h4>
            <ul className={styles.bulletList}>
              {feedback.improvements.map((imp, i) => (
                <li key={i}>{imp}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <div className={styles.headerInfo}>
          <Sparkles size={20} style={{ color: '#0a84ff' }} />
          <div>
            <h3 className={styles.chatTitle}>AI Interview Coach</h3>
            <p className={styles.chatSubtitle}>Role: {currentJob?.title} at {currentJob?.company}</p>
          </div>
        </div>
        <span className={styles.systemBadge}>Session Active</span>
      </div>

      <div className={styles.messageList}>
        {messages.map((msg, index) => (
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
          placeholder="Type your answer here..."
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

export default MockInterview;
