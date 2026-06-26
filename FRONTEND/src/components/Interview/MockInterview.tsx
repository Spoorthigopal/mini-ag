import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import styles from './interview.module.css';
import { Send, Sparkles, BookOpen, ChevronRight, Layers, Trophy, RotateCcw, ArrowRight, ArrowLeft, SkipForward } from 'lucide-react';
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

const ROLES = [
  { id: '1', title: 'Frontend Developer' },
  { id: '2', title: 'Backend / Data Engineer' },
  { id: '3', title: 'Fullstack / Django' },
  { id: '4', title: 'UI/UX Designer' },
  { id: '5', title: 'DevOps / Cloud Engineer' },
  { id: '6', title: 'Mobile App Developer' },
];

const SKILL_MAP: Record<string, string[]> = {
  '1': ['React', 'TypeScript', 'Node.js', 'Redux', 'REST APIs'],
  '2': ['Python', 'SQL', 'Data Visualization', 'Pandas', 'Machine Learning Basics'],
  '3': ['Django', 'PostgreSQL', 'REST API Design', 'Docker', 'Authentication'],
  '4': ['Figma', 'CSS Modules', 'JavaScript', 'Responsive Design', 'Animations'],
  '5': ['Kubernetes', 'AWS', 'CI/CD Pipelines', 'Terraform', 'Linux Administration'],
  '6': ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Mobile UI/UX'],
};

const LEVELS = ['Beginner', 'Intermediate', 'Expert'];

const levelColors: Record<string, string> = {
  Beginner: '#30d158',
  Intermediate: '#ff9f0a',
  Expert: '#ff2d55',
};

// Markdown renderer
const renderMarkdown = (text: string): React.ReactNode => {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    if (line.startsWith('### ')) return <h4 key={i} style={{ color: '#f8fafc', margin: '1rem 0 0.5rem', fontSize: '1rem', fontWeight: 700 }}>{line.slice(4)}</h4>;
    if (line.startsWith('## ')) return <h3 key={i} style={{ color: '#f8fafc', margin: '1rem 0 0.5rem', fontSize: '1.1rem', fontWeight: 700 }}>{line.slice(3)}</h3>;
    if (line.startsWith('# ')) return <h2 key={i} style={{ color: '#f8fafc', margin: '1rem 0 0.5rem', fontSize: '1.2rem', fontWeight: 700 }}>{line.slice(2)}</h2>;
    if (line.startsWith('```') || line === '```') return null;
    if (line.startsWith('- ') || line.startsWith('* ')) {
      const content = line.slice(2);
      const boldParts = content.split(/\*\*(.*?)\*\*/g);
      return (
        <p key={i} style={{ margin: '0.3rem 0 0.3rem 1rem', lineHeight: 1.7, color: '#cbd5e1' }}>
          {'• '}
          {boldParts.length > 1
            ? boldParts.map((p, j) => j % 2 === 1 ? <strong key={j} style={{ color: '#f1f5f9' }}>{p}</strong> : p)
            : content}
        </p>
      );
    }
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
  const [selectedJobId, setSelectedJobId] = useState(currentJob?.id || '1');
  const [selectedSkill, setSelectedSkill] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  // Map of skill -> session (for this job role)
  const [skillSessions, setSkillSessions] = useState<Record<string, StudySession>>({});
  const [session, setSession] = useState<StudySession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentTopicLabel, setCurrentTopicLabel] = useState('');
  const [isDeepMode, setIsDeepMode] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const skills = SKILL_MAP[selectedJobId] || SKILL_MAP['1'];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Fetch all saved sessions for this job role whenever job role changes
  useEffect(() => {
    setPhase('setup');
    setSession(null);
    setSelectedSkill('');
    setSelectedLevel('');
    setErrorMsg('');
    api.get(`/interview/study/user-sessions?job_id=${selectedJobId}`)
      .then(res => {
        if (res.data && typeof res.data === 'object' && !res.data.session_id) {
          // Dict of skill -> session
          setSkillSessions(res.data as Record<string, StudySession>);
        } else {
          setSkillSessions({});
        }
      })
      .catch(() => setSkillSessions({}));
  }, [selectedJobId]);

  // When a skill is selected, restore existing session if any
  const handleSkillSelect = (skill: string) => {
    setSelectedSkill(skill);
    setErrorMsg('');
    const existingSession = skillSessions[skill];
    if (existingSession) {
      setSelectedLevel(existingSession.level);
    }
  };

  const handleGeneratePlan = async () => {
    if (!selectedSkill || !selectedLevel) return;
    setIsLoading(true);
    setErrorMsg('');
    try {
      const res = await api.post('/interview/study/plan', {
        job_id: selectedJobId,
        skill: selectedSkill,
        user_level: selectedLevel,
      });
      if (res.data && res.data.session_id) {
        const newSession: StudySession = res.data;
        setSession(newSession);
        setSkillSessions(prev => ({ ...prev, [selectedSkill]: newSession }));
        setPhase('plan');
      } else {
        setErrorMsg('Failed to generate study plan. Please try again.');
      }
    } catch (e: any) {
      const detail = e?.response?.data?.detail || 'Server error. Please try again.';
      setErrorMsg(detail);
    } finally {
      setIsLoading(false);
    }
  };

  // View plan for selected skill (existing or after generating)
  const handleViewPlan = () => {
    const existingSession = skillSessions[selectedSkill];
    if (existingSession) {
      setSession(existingSession);
      setPhase('plan');
    }
  };

  const fetchTopicAtIndex = useCallback(async (sess: StudySession, targetIndex: number) => {
    setIsLoading(true);
    setIsDeepMode(false);
    try {
      let res;
      if (targetIndex === sess.current_topic_index) {
        // Just teach the current index
        res = await api.post('/interview/study/teach', { session_id: sess.session_id });
      } else {
        // Jump to a specific topic
        res = await api.post('/interview/study/interact', {
          session_id: sess.session_id,
          action: 'jump_to_topic',
          message: String(targetIndex),
        });
      }
      const data = res.data;
      if (data.is_complete) setPhase('complete');
      setCurrentTopicLabel(data.topic);
      setSession(prev => prev ? { ...prev, current_topic_index: data.current_index } : prev);
      setSkillSessions(prev => {
        if (!prev[sess.skill]) return prev;
        return { ...prev, [sess.skill]: { ...prev[sess.skill], current_topic_index: data.current_index } };
      });
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `### 📖 Topic ${data.current_index + 1}: ${data.topic}\n\n${data.explanation}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ **AI Error**\n\n${e?.response?.data?.detail || e.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleStartFromTopic = async (topicIndex: number) => {
    if (!session) return;
    setPhase('learning');
    setMessages([]);
    await fetchTopicAtIndex(session, topicIndex);
  };

  const handleMoveNext = async () => {
    if (!session || isLoading) return;
    const nextIdx = (session.current_topic_index || 0) + 1;
    if (nextIdx >= session.topics.length) {
      setPhase('complete');
      return;
    }
    setMessages(prev => [...prev, {
      role: 'user', content: '➡️ Move to next topic',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
    await fetchTopicAtIndex(session, nextIdx);
  };

  const handleMovePrev = async () => {
    if (!session || isLoading) return;
    const prevIdx = (session.current_topic_index || 0) - 1;
    if (prevIdx < 0) return;
    setMessages(prev => [...prev, {
      role: 'user', content: '⬅️ Going back to previous topic',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
    await fetchTopicAtIndex(session, prevIdx);
  };

  const handleSkipToTopic = async (idx: number) => {
    if (!session || isLoading) return;
    setMessages(prev => [...prev, {
      role: 'user', content: `⏭️ Jumping to: ${session.topics[idx]}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
    await fetchTopicAtIndex(session, idx);
  };

  const handleSendQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !session || isLoading) return;
    const question = inputText.trim();
    setInputText('');
    setMessages(prev => [...prev, {
      role: 'user', content: question,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
    setIsLoading(true);
    try {
      const res = await api.post('/interview/study/interact', {
        session_id: session.session_id, action: 'go_deeper', message: question,
      });
      setMessages(prev => [...prev, {
        role: 'assistant', content: res.data.explanation,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ **AI Error**\n\n${e?.response?.data?.detail || e.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestart = () => {
    setPhase('setup');
    setSession(null);
    setMessages([]);
    setSelectedSkill('');
    setSelectedLevel('');
    setCurrentTopicLabel('');
    setIsDeepMode(false);
  };

  const currentIdx = session?.current_topic_index || 0;
  const totalTopics = session?.topics.length || 1;
  const progress = Math.round((currentIdx / totalTopics) * 100);

  // ─── SETUP PHASE ──────────────────────────────────────────────────────────
  if (phase === 'setup') {
    return (
      <div className={styles.setupContainer}>
        <div className={styles.setupCard}>
          <div className={styles.setupHeader}>
            <div className={styles.setupIcon}><Sparkles size={28} /></div>
            <h2 className={styles.setupTitle}>AI Study Coach</h2>
            <p className={styles.setupSubtitle}>Pick a role, skill, and level — I'll build a personalised curriculum just for you.</p>
          </div>

          {/* Job Role */}
          <div className={styles.setupSection}>
            <label className={styles.setupLabel}>1. Select a Job Role</label>
            <select
              value={selectedJobId}
              onChange={(e) => { setSelectedJobId(e.target.value); setSelectedSkill(''); setSelectedLevel(''); }}
              style={{ width: '100%', padding: '0.85rem', borderRadius: '8px', border: '1px solid #334155', background: '#1e293b', color: '#f8fafc', marginBottom: '1.5rem', outline: 'none', fontSize: '1rem', cursor: 'pointer' }}
            >
              {ROLES.map(role => <option key={role.id} value={role.id}>{role.title}</option>)}
            </select>

            {/* Skills — show chips with badge if a saved plan exists */}
            <label className={styles.setupLabel}>2. Choose a skill to master</label>
            <div className={styles.skillGrid}>
              {skills.map(skill => {
                const hasSession = !!skillSessions[skill];
                const savedProgress = skillSessions[skill]?.current_topic_index || 0;
                const savedTotal = skillSessions[skill]?.topics.length || 0;
                return (
                  <button
                    key={skill}
                    className={`${styles.skillChip} ${selectedSkill === skill ? styles.skillChipActive : ''}`}
                    onClick={() => handleSkillSelect(skill)}
                    style={{ position: 'relative' }}
                  >
                    {skill}
                    {hasSession && (
                      <span style={{
                        position: 'absolute', top: '-6px', right: '-6px',
                        background: '#0ea5e9', color: '#fff', borderRadius: '99px',
                        fontSize: '0.6rem', padding: '1px 5px', fontWeight: 700,
                      }}>
                        {savedProgress}/{savedTotal}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Level */}
          <div className={styles.setupSection}>
            <label className={styles.setupLabel}>3. Rate your current level</label>
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

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '0.75rem', flexDirection: 'column' }}>
            {/* If saved session exists for chosen skill, show "View Plan" */}
            {selectedSkill && skillSessions[selectedSkill] && (
              <button
                className={styles.startBtn}
                style={{ background: 'linear-gradient(135deg,#0ea5e9,#6366f1)' }}
                onClick={handleViewPlan}
              >
                <RotateCcw size={18} /> Resume Saved Plan ({skillSessions[selectedSkill].level})
              </button>
            )}
            <button
              className={styles.startBtn}
              onClick={handleGeneratePlan}
              disabled={!selectedSkill || !selectedLevel || isLoading}
            >
              {isLoading
                ? <span>Generating your study plan...</span>
                : <><BookOpen size={18} /> {skillSessions[selectedSkill] ? 'Generate New Plan' : 'Generate Study Plan'}</>}
            </button>
          </div>

          {errorMsg && (
            <p style={{ color: '#ff453a', fontSize: '0.85rem', textAlign: 'center', margin: '0.5rem 0 0' }}>
              ⚠️ {errorMsg}
            </p>
          )}
        </div>
      </div>
    );
  }

  // ─── PLAN PHASE ───────────────────────────────────────────────────────────
  if (phase === 'plan' && session) {
    return (
      <div className={styles.setupContainer}>
        <div className={styles.setupCard} style={{ maxWidth: '600px' }}>
          <div className={styles.planHeader}>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
              <div className={styles.planBadge} style={{ background: `${levelColors[session.level]}25`, color: levelColors[session.level], border: `1px solid ${levelColors[session.level]}50` }}>
                {session.level}
              </div>
              <div className={styles.planBadge} style={{ background: '#0ea5e920', color: '#0ea5e9', border: '1px solid #0ea5e950' }}>
                {ROLES.find(r => r.id === selectedJobId)?.title || 'Developer'}
              </div>
            </div>
            <h2 className={styles.setupTitle}>Your {session.skill} Study Plan</h2>
            <p className={styles.setupSubtitle}>{session.topics.length} topics — click any to jump directly to it</p>
          </div>

          {/* Topics list — each is clickable */}
          <div className={styles.topicsList}>
            {session.topics.map((topic, idx) => (
              <div
                key={idx}
                className={`${styles.topicItem} ${idx < session.current_topic_index ? styles.topicDone : ''} ${idx === session.current_topic_index ? styles.topicCurrent : ''}`}
                style={{ cursor: 'pointer' }}
                onClick={() => handleStartFromTopic(idx)}
                title={`Start from "${topic}"`}
              >
                <div className={styles.topicNumber}>{idx < session.current_topic_index ? '✓' : idx + 1}</div>
                <span className={styles.topicLabel}>{topic}</span>
                <ChevronRight size={14} style={{ opacity: 0.4, marginLeft: 'auto' }} />
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            <button className={styles.startBtn} onClick={() => handleStartFromTopic(session.current_topic_index)} disabled={isLoading} style={{ flex: 1 }}>
              {session.current_topic_index > 0
                ? <><RotateCcw size={18} /> Resume (Topic {session.current_topic_index + 1})</>
                : <><ChevronRight size={18} /> Start Learning</>}
            </button>
            <button
              className={styles.startBtn}
              style={{ background: '#1e293b', border: '1px solid #334155', flex: '0 0 auto' }}
              onClick={() => { setPhase('setup'); setSession(null); }}
            >
              ← Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ─── LEARNING PHASE ───────────────────────────────────────────────────────
  return (
    <div className={styles.coachContainer}>
      {/* Progress header */}
      <div className={styles.progressBar}>
        <div className={styles.progressInfo}>
          <div className={styles.progressLabel}>
            <Layers size={14} />
            <span><strong>{session?.skill}</strong> · Topic {currentIdx + 1}/{totalTopics}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div className={styles.progressPercent}>{progress}%</div>
            <button
              onClick={() => setPhase('plan')}
              title="Back to plan"
              style={{ background: 'none', border: '1px solid #334155', borderRadius: '6px', color: '#94a3b8', padding: '2px 8px', cursor: 'pointer', fontSize: '0.75rem' }}
            >
              📋 Plan
            </button>
          </div>
        </div>
        <div className={styles.progressTrack}>
          <div className={styles.progressFill} style={{ width: `${progress}%` }} />
        </div>
        {/* Topic pills — clickable to jump */}
        <div className={styles.topicPills}>
          {session?.topics.map((t, i) => (
            <div
              key={i}
              title={`Jump to: ${t}`}
              className={`${styles.topicPill} ${i < currentIdx ? styles.pillDone : ''} ${i === currentIdx ? styles.pillActive : ''}`}
              style={{ cursor: 'pointer' }}
              onClick={() => !isLoading && handleSkipToTopic(i)}
            />
          ))}
        </div>
      </div>

      {/* Chat window */}
      <div className={styles.coachChat}>
        <div className={styles.messageList}>
          {messages.map((msg, i) => (
            <div key={i} className={`${styles.messageRow} ${msg.role === 'user' ? styles.userRow : styles.botRow}`}>
              <div className={`${styles.messageBubble} ${msg.role === 'user' ? styles.userBubble : styles.botBubble}`}>
                {msg.role === 'assistant'
                  ? <div>{renderMarkdown(msg.content)}</div>
                  : <span>{msg.content}</span>}
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

        {/* Action area — shown after bot responds */}
        {!isLoading && messages.length > 0 && phase === 'learning' && (
          <div className={styles.actionArea}>
            {isDeepMode ? (
              <form onSubmit={handleSendQuestion} className={styles.deepModeForm}>
                <input
                  autoFocus
                  type="text"
                  placeholder={`Ask anything about "${currentTopicLabel}"...`}
                  className={styles.chatInput}
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                />
                <button type="submit" className={styles.sendBtn} disabled={!inputText.trim()}><Send size={18} /></button>
                <button type="button" className={styles.cancelDeepBtn} onClick={() => setIsDeepMode(false)}>Cancel</button>
              </form>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {/* Dive deeper / Move next */}
                <div className={styles.choiceRow}>
                  <button className={styles.deeperBtn} onClick={() => setIsDeepMode(true)}>🔍 Dive Deeper</button>
                  <button className={styles.nextBtn} onClick={handleMoveNext} disabled={currentIdx >= totalTopics - 1}>
                    Move Next <ArrowRight size={16} />
                  </button>
                </div>
                {/* Navigation row */}
                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                  <button
                    onClick={handleMovePrev}
                    disabled={currentIdx === 0}
                    style={{ background: '#1e293b', border: '1px solid #334155', color: currentIdx === 0 ? '#475569' : '#94a3b8', borderRadius: '8px', padding: '0.4rem 0.85rem', cursor: currentIdx === 0 ? 'not-allowed' : 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <ArrowLeft size={14} /> Prev
                  </button>
                  <button
                    onClick={() => setPhase('plan')}
                    style={{ background: '#1e293b', border: '1px solid #334155', color: '#94a3b8', borderRadius: '8px', padding: '0.4rem 0.85rem', cursor: 'pointer', fontSize: '0.8rem' }}
                  >
                    📋 View Plan
                  </button>
                  <button
                    onClick={handleRestart}
                    style={{ background: '#1e293b', border: '1px solid #334155', color: '#94a3b8', borderRadius: '8px', padding: '0.4rem 0.85rem', cursor: 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <RotateCcw size={14} /> New Plan
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Complete */}
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
