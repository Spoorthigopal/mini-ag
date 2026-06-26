import realInterviewData from './realInterviewData.json';

export interface Question {
  id: string;
  question: string;
  answer: string;
  difficulty: 'easy' | 'moderate' | 'difficult';
  isHighlyAsked: boolean;
}

export interface SkillData {
  id: string;
  name: string;
  icon: string;
  questions: Question[];
}

// Map icons back to the skills from JSON
const skillIcons: Record<string, string> = {
  'javascript': 'JS',
  'python': 'PY',
  'react': '⚛️',
  'nodejs': '🟢',
  'sql': '🗄️',
  'dsa': '🧬',
  'system-design': '🏗️',
  'git-devops': '⚙️',
  'ml': '🤖',
  'os': '💻'
};

// Use the generated real data instead of dummy data
export const interviewData: SkillData[] = (realInterviewData as SkillData[]).map(skill => ({
  ...skill,
  icon: skillIcons[skill.id] || '❓'
}));
