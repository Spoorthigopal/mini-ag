import React, { useState, useEffect } from 'react';
import styles from './interview.module.css';
import { Question } from './interviewData';
import { ChevronDown, MessageSquare, CheckCircle, Flame, X } from 'lucide-react';

interface QuestionCardProps {
  question: Question;
  index: number;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({ question, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isRead, setIsRead] = useState(false);
  const [showComment, setShowComment] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [tempComment, setTempComment] = useState('');

  // Load state from localStorage on mount
  useEffect(() => {
    const savedReadState = localStorage.getItem(`read-${question.id}`);
    if (savedReadState === 'true') setIsRead(true);

    const savedComment = localStorage.getItem(`comment-${question.id}`);
    if (savedComment) setCommentText(savedComment);
  }, [question.id]);

  const toggleRead = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent expanding the card when clicking the icon
    const newState = !isRead;
    setIsRead(newState);
    localStorage.setItem(`read-${question.id}`, newState.toString());
  };

  const toggleComment = (e: React.MouseEvent) => {
    e.stopPropagation();
    setTempComment(commentText);
    setShowComment(!showComment);
  };

  const saveComment = () => {
    setCommentText(tempComment);
    localStorage.setItem(`comment-${question.id}`, tempComment);
    setShowComment(false);
  };

  return (
    <div className={`${styles.questionCard} ${isRead ? styles.read : ''}`}>
      <div className={styles.questionHeader} onClick={() => setIsExpanded(!isExpanded)}>
        <div className={styles.questionTitleArea}>
          <div className={styles.questionNumber}>{index + 1}</div>
          <div>
            <h3 className={styles.questionText}>{question.question}</h3>
            <div className={styles.badges}>
              {question.isHighlyAsked && (
                <span className={`${styles.badge} ${styles.highlyAsked}`}>
                  <Flame size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
                  Highly Asked
                </span>
              )}
              <span className={`${styles.badge} ${styles[question.difficulty]}`}>
                {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
              </span>
            </div>
          </div>
        </div>
        
        <div className={styles.cardActions}>
          <button 
            className={`${styles.actionBtn} ${showComment || commentText ? styles.commentActive : ''}`} 
            onClick={toggleComment}
            title="Add note"
          >
            <MessageSquare size={18} />
          </button>
          <button 
            className={`${styles.actionBtn} ${isRead ? styles.active : ''}`} 
            onClick={toggleRead}
            title="Mark as read"
          >
            <CheckCircle size={18} />
          </button>
          <button className={`${styles.actionBtn} ${styles.expandBtn} ${isExpanded ? styles.expanded : ''}`}>
            <ChevronDown size={20} />
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className={styles.answersArea}>
          <div className={styles.answerSection}>
            <h4>💡 Explanation</h4>
            <p style={{ whiteSpace: 'pre-wrap' }}>{question.answer}</p>
          </div>
        </div>
      )}

      {showComment && (
        <div className={styles.modalOverlay} onClick={() => setShowComment(false)}>
          <div className={styles.commentModal} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3>Note for Question {index + 1}</h3>
              <button className={styles.closeModalBtn} onClick={() => setShowComment(false)}>
                <X size={20} />
              </button>
            </div>
            <textarea 
              className={styles.commentInput}
              placeholder="Add your personal notes here..."
              value={tempComment}
              onChange={(e) => setTempComment(e.target.value)}
            />
            <div className={styles.commentActions}>
              <button className={styles.cancelCommentBtn} onClick={() => setShowComment(false)}>
                Cancel
              </button>
              <button className={styles.saveCommentBtn} onClick={saveComment}>
                Save Note
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
