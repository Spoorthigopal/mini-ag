import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import styles from './interview.module.css';
import { Send, Sparkles, BookOpen, ChevronRight, Layers, Trophy, RotateCcw, ArrowRight } from 'lucide-react';
import api from '../../services/api';

type Phase = 'setup' | 'plan' | 'learning' | 'complete';

interface StudySession {
  session_id: string;
  skill: string;
  level: string;
  topics: string[];
  current_topic_index: number;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const SKILL_MAP: Record<string, string[]> = {
  '1': ['React', 'TypeScript', 'Node.js', 'Redux', 'REST APIs'],
  '2': ['Python', 'SQL', 'Data Visualization', 'Pandas', 'Machine Learning Basics'],
  '3': ['Django', 'PostgreSQL', 'REST API Design', 'Docker', 'Authentication'],
  '4': ['React', 'CSS Modules', 'JavaScript', 'Responsive Design', 'Animations'],
};

const LEVELS = ['Beginner', 'Intermediate', 'Expert'];

const levelColors: Record<string, string> = {
  Beginner: '#30d158',
  Intermediate: '#ff9f0a',
  Expert: '#ff2d55',
};

// Simple markdown renderer (bold, code blocks, headers)
const renderMarkdown = (text: string): React.ReactNode => {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    if (line.startsWith('### ')) {
      return <h4 key={i} style={{ color: '#f8fafc', margin: '1rem 0 0.5rem', fontSize: '1rem', fontWeight: 700 }}>{line.slice(4)}</h4>;
    }
    if (line.startsWith('## ')) {
      return <h3 key={i} style={{ color: '#f8fafc', margin: '1rem 0 0.5rem', fontSize: '1.1rem', fontWeight: 700 }}>{line.slice(3)}</h3>;
    }
    if (line.startsWith('**') && line.endsWith('**')) {
      return <p key={i} style={{ fontWeight: 700, color: '#e2e8f0', margin: '0.5rem 0' }}>{line.slice(2, -2)}</p>;
    }
    if (line.startsWith('```') || line === '```') {
      return null;
    }
    // Inline bold
    const boldParts = line.split(/\*\*(.*?)\*\*/g);
    if (boldParts.length > 1) {
      return (
        <p key={i} style={{ margin: '0.35rem 0', lineHeight: 1.7, color: '#cbd5e1' }}>
          {boldParts.map((part, j) => j % 2 === 1 ? <strong key={j} style={{ color: '#f1f5f9' }}>{part}</strong> : part)}
        </p>
      );
    }
    if (line.trim() === '') return <br key={i} />;
    return <p key={i} style={{ margin: '0.35rem 0', lineHeight: 1.7, color: '#cbd5e1' }}>{line}</p>;
  });
};

export const MockInterview: React.FC = () => {
  const { currentJob } = useSelector((state: RootState) => state.interview);

  const [phase, setPhase] = useState<Phase>('setup');
  const [selectedSkill, setSelectedSkill] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [session, setSession] = useState<StudySession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('');
  const [isDeepMode, setIsDeepMode] = useState(false);
  const [resumeChecked, setResumeChecked] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const jobId = currentJob?.id || '1';
  const skills = SKILL_MAP[jobId] || SKILL_MAP['1'];

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, isLoading]);

  useEffect(() => {
    if (resumeChecked) return;
    setResumeChecked(true);
    api.get(`/interview/study/user-sessions?job_id=${jobId}`)
      .then(res => {
        if (res.data && res.data.session_id) {
          setSession(res.data);
          setPhase('plan');
        }
      })
      .catch(() => {});
  }, [jobId, resumeChecked]);

  const handleGeneratePlan = async () => {
    if (!selectedSkill || !selectedLevel) return;
    setIsLoading(true);
    try {
      const res = await api.post('/interview/study/plan', { job_id: jobId, skill: selectedSkill, user_level: selectedLevel });
      setSession(res.data);
      setPhase('plan');
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  };

  const fetchTopicExplanation = useCallback(async (sess: StudySession) => {
    setIsLoading(true);
    setIsDeepMode(false);
    try {
      const res = await api.post('/interview/study/teach', { session_id: sess.session_id });
      const data = res.data;
      if (data.is_complete) {
        setPhase('complete');
      }
      setCurrentTopic(data.topic);
      setSession(prev => prev ? { ...prev, current_topic_index: data.current_index } : prev);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `### 📖 Topic ${data.current_index + 1}: ${data.topic}\n\n${data.explanation}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  }, []);

  const handleStartLearning = async () => {
    if (!session) return;
    setPhase('learning');
    setMessages([]);
    await fetchTopicExplanation(session);
  };

  const handleMoveNext = async () => {
    if (!session || isLoading) return;
    setIsLoading(true);
    setIsDeepMode(false);
    setMessages(prev => [...prev, { role: 'user', content: '➡️ Move to next topic', timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
    try {
      const res = await api.post('/interview/study/interact', { session_id: session.session_id, action: 'move_next', message: '' });
      const data = res.data;
      if (data.is_complete) setPhase('complete');
      setCurrentTopic(data.topic);
      setSession(prev => prev ? { ...prev, current_topic_index: data.current_index } : prev);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `### 📖 Topic ${data.current_index + 1}: ${data.topic}\n\n${data.explanation}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  };

  const handleSendQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !session || isLoading) return;
    const question = inputText.trim();
    setInputText('');
    setMessages(prev => [...prev, { role: 'user', content: question, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
    setIsLoading(true);
    try {
      const res = await api.post('/interview/study/interact', { session_id: session.session_id, action: 'go_deeper', message: question });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.explanation, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  };

  const handleRestart = () => {
    setPhase('setup'); setSession(null); setMessages([]); setSelectedSkill(''); setSelectedLevel(''); setCurrentTopic(''); setIsDeepMode(false); setResumeChecked(true);
  };

  const progress = session ? Math.round((session.current_topic_index / (session.topics.length || 1)) * 100) : 0;

  // ─── SETUP PHASE ──────────────────────────────────────────────────────────
  if (phase === 'setup') {
    return (
      <div className={styles.setupContainer}>
        <div className={styles.setupCard}>
          <div className={styles.setupHeader}>
            <div className={styles.setupIcon}><Sparkles size={28} /></div>
            <h2 className={styles.setupTitle}>AI Study Coach</h2>
            <p className={styles.setupSubtitle}>Pick a skill and your level — I'll build a personalised curriculum just for you.</p>
          </div>
          <div className={styles.setupSection}>
            <label className={styles.setupLabel}>1. Choose a skill to master</label>
            <div className={styles.skillGrid}>
              {skills.map(skill => (
                <button key={skill} className={`${styles.skillChip} ${selectedSkill === skill ? styles.skillChipActive : ''}`} onClick={() => setSelectedSkill(skill)}>{skill}</button>
              ))}
            </div>
          </div>
          <div className={styles.setupSection}>
            <label className={styles.setupLabel}>2. Rate your current level</label>
            <div className={styles.levelGrid}>
              {LEVELS.map(level => (
                <button
                  key={level}
                  className={`${styles.levelBtn} ${selectedLevel === level ? styles.levelBtnActive : ''}`}
                  style={selectedLevel === level ? { borderColor: levelColors[level], color: levelColors[level], background: `${levelColors[level]}20` } : {}}
                  onClick={() => setSelectedLevel(level)}
                >
                  {level === 'Beginner' && '🌱'} {level === 'Intermediate' && '⚡'} {level === 'Expert' && '🔥'}
                  <span>{level}</span>
                </button>
              ))}
            </div>
          </div>
          <button className={styles.startBtn} onClick={handleGeneratePlan} disabled={!selectedSkill || !selectedLevel || isLoading}>
            {isLoading ? <span>Generating your study plan...</span> : <><BookOpen size={18} /> Generate Study Plan</>}
          </button>
        </div>
      </div>
    );
  }

  // ─── PLAN PHASE ───────────────────────────────────────────────────────────
  if (phase === 'plan' && session) {
    return (
      <div className={styles.setupContainer}>
        <div className={styles.setupCard} style={{ maxWidth: '580px' }}>
          <div className={styles.planHeader}>
            <div className={styles.planBadge} style={{ background: `${levelColors[session.level]}25`, color: levelColors[session.level], border: `1px solid ${levelColors[session.level]}50` }}>{session.level}</div>
            <h2 className={styles.setupTitle}>Your {session.skill} Study Plan</h2>
            <p className={styles.setupSubtitle}>{session.topics.length} topics — tailored for your level. Ready to begin?</p>
          </div>
          <div className={styles.topicsList}>
            {session.topics.map((topic, idx) => (
              <div key={idx} className={`${styles.topicItem} ${idx < session.current_topic_index ? styles.topicDone : ''} ${idx === session.current_topic_index ? styles.topicCurrent : ''}`}>
                <div className={styles.topicNumber}>{idx < session.current_topic_index ? '✓' : idx + 1}</div>
                <span className={styles.topicLabel}>{topic}</span>
              </div>
            ))}
          </div>
          <button className={styles.startBtn} onClick={handleStartLearning} disabled={isLoading}>
            {session.current_topic_index > 0 ? <><RotateCcw size={18} /> Resume from Topic {session.current_topic_index + 1}</> : <><ChevronRight size={18} /> Start Learning</>}
          </button>
        </div>
      </div>
    );
  }

  // ─── LEARNING PHASE ───────────────────────────────────────────────────────
  const totalTopics = session?.topics.length || 1;
  const currentIdx = session?.current_topic_index || 0;

  return (
    <div className={styles.coachContainer}>
      <div className={styles.progressBar}>
        <div className={styles.progressInfo}>
          <div className={styles.progressLabel}><Layers size={14} /><span>Progress — <strong>{currentTopic || session?.topics[0]}</strong></span></div>
          <div className={styles.progressPercent}>{progress}%</div>
        </div>
        <div className={styles.progressTrack}>
          <div className={styles.progressFill} style={{ width: `${progress}%` }} />
        </div>
        <div className={styles.topicPills}>
          {session?.topics.map((t, i) => (
            <div key={i} title={t} className={`${styles.topicPill} ${i < currentIdx ? styles.pillDone : ''} ${i === currentIdx ? styles.pillActive : ''}`} />
          ))}
        </div>
      </div>

      <div className={styles.coachChat}>
        <div className={styles.messageList}>
          {messages.map((msg, i) => (
            <div key={i} className={`${styles.messageRow} ${msg.role === 'user' ? styles.userRow : styles.botRow}`}>
              <div className={`${styles.messageBubble} ${msg.role === 'user' ? styles.userBubble : styles.botBubble}`}>
                {msg.role === 'assistant' ? <div>{renderMarkdown(msg.content)}</div> : <span>{msg.content}</span>}
                <span className={styles.messageTime}>{msg.timestamp}</span>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className={`${styles.messageRow} ${styles.botRow}`}>
              <div className={styles.typingIndicator}>
                <div className={styles.typingDot} /><div className={styles.typingDot} /><div className={styles.typingDot} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {!isLoading && messages.length > 0 && phase === 'learning' && (
          <div className={styles.actionArea}>
            {isDeepMode ? (
              <form onSubmit={handleSendQuestion} className={styles.deepModeForm}>
                <input autoFocus type="text" placeholder={`Ask anything about "${currentTopic}"...`} className={styles.chatInput} value={inputText} onChange={e => setInputText(e.target.value)} />
                <button type="submit" className={styles.sendBtn} disabled={!inputText.trim()}><Send size={18} /></button>
                <button type="button" className={styles.cancelDeepBtn} onClick={() => setIsDeepMode(false)}>Cancel</button>
              </form>
            ) : (
              <div className={styles.choiceRow}>
                <button className={styles.deeperBtn} onClick={() => setIsDeepMode(true)}>🔍 Go Deeper</button>
                <button className={styles.nextBtn} onClick={handleMoveNext}>Move Next <ArrowRight size={16} /></button>
              </div>
            )}
          </div>
        )}

        {phase === 'complete' && (
          <div className={styles.completeActions}>
            <Trophy size={36} style={{ color: '#ff9f0a' }} />
            <p>You completed the entire study plan! 🎉</p>
            <button className={styles.startBtn} onClick={handleRestart}>Start a New Topic</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MockInterview;
