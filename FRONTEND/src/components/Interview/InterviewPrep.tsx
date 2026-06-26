import React, { useState } from 'react';
import styles from './interview.module.css';
import { interviewData, SkillData } from './interviewData';
import { QuestionBank } from './QuestionBank';
import { Sparkles, MessageSquare } from 'lucide-react';

export const InterviewPrep: React.FC = () => {
  const [selectedSkill, setSelectedSkill] = useState<SkillData | null>(null);

  if (selectedSkill) {
    return <QuestionBank skill={selectedSkill} onBack={() => setSelectedSkill(null)} />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          <Sparkles className={styles.titleIcon} style={{ color: '#0a84ff' }} />
          Interview Prep
        </h1>
        <p className={styles.subtitle}>
          Master your technical interviews. Browse comprehensive question banks across core technical skills.
          Questions are graded by difficulty and include both simple explanations and technical deep dives.
        </p>
      </div>

      <div className={styles.skillGrid}>
        {interviewData.map((skill) => (
          <div 
            key={skill.id} 
            className={styles.skillCard}
            onClick={() => setSelectedSkill(skill)}
          >
            <div className={styles.skillIcon}>
              {skill.icon}
            </div>
            <div className={styles.skillName}>{skill.name}</div>
            <div className={styles.skillStats}>
              <MessageSquare size={14} />
              {skill.questions.length} Questions
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InterviewPrep;
