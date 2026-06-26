import React, { useState, useMemo } from 'react';
import styles from './interview.module.css';
import { SkillData } from './interviewData';
import { QuestionCard } from './QuestionCard';
import { ArrowLeft, RefreshCw } from 'lucide-react';

interface QuestionBankProps {
  skill: SkillData;
  onBack: () => void;
}

type Difficulty = 'easy' | 'moderate' | 'difficult';

export const QuestionBank: React.FC<QuestionBankProps> = ({ skill, onBack }) => {
  const [activeTab, setActiveTab] = useState<Difficulty>('easy');
  const [displayCount, setDisplayCount] = useState(50);

  // Reset display count when changing tabs
  const handleTabChange = (tab: Difficulty) => {
    setActiveTab(tab);
    setDisplayCount(50);
  };

  // Filter questions by current tab difficulty
  const currentQuestions = useMemo(() => {
    return skill.questions.filter(q => q.difficulty === activeTab);
  }, [skill, activeTab]);

  // Get only the currently displayed subset of questions
  const displayedQuestions = useMemo(() => {
    return currentQuestions.slice(0, displayCount);
  }, [currentQuestions, displayCount]);

  const hasMore = displayCount < currentQuestions.length;

  const loadMore = () => {
    setDisplayCount(prev => prev + 20);
  };

  return (
    <div>
      <div className={styles.bankHeader}>
        <div>
          <button className={styles.backButton} onClick={onBack}>
            <ArrowLeft size={20} /> Back to Skills
          </button>
          <h2 className={styles.bankTitle}>
            <span style={{ fontSize: '2.5rem' }}>{skill.icon}</span> {skill.name} Interview Questions
          </h2>
        </div>
        
        <div className={styles.tabs}>
          <button 
            className={`${styles.tab} ${styles.easy} ${activeTab === 'easy' ? styles.active : ''}`}
            onClick={() => handleTabChange('easy')}
          >
            Easy
          </button>
          <button 
            className={`${styles.tab} ${styles.moderate} ${activeTab === 'moderate' ? styles.active : ''}`}
            onClick={() => handleTabChange('moderate')}
          >
            Moderate
          </button>
          <button 
            className={`${styles.tab} ${styles.difficult} ${activeTab === 'difficult' ? styles.active : ''}`}
            onClick={() => handleTabChange('difficult')}
          >
            Difficult
          </button>
        </div>
      </div>

      <div className={styles.questionList}>
        {displayedQuestions.map((q, index) => (
          <QuestionCard key={q.id} question={q} index={index} />
        ))}
      </div>

      {hasMore && (
        <div className={styles.loadMoreContainer}>
          <button className={styles.loadMoreBtn} onClick={loadMore}>
            <RefreshCw size={18} /> Load Next 20 Questions
          </button>
        </div>
      )}
    </div>
  );
};
