import React from 'react';
import { useNavigate } from 'react-router-dom';
import HeroSection from '../components/Layout/HeroSection';
import { Card } from '../components/Common/Card';
import { Button } from '../components/Common/Button';
import styles from './Dashboard.module.css';
import { useSelector } from 'react-redux';
import { RootState } from '../redux/store';
import { Gift, Briefcase, Sparkles, Shield, ArrowRight } from 'lucide-react';

const modules = [
  {
    title: 'Welfare Schemes',
    description: 'Discover, filter, and apply for government and university financial aids, scholarships, and grants tailored to your profile.',
    features: ['Search 70+ Schemes', 'AI Scheme Recommendations', 'Direct Apply Links', 'Eligibility Checker'],
    icon: <Gift size={32} style={{ color: '#ff2d55' }} />,
    path: '/welfare',
    color: '#ff2d55',
  },
  {
    title: 'Internships Portal',
    description: 'Explore  job and internship opportunities.',
    features: ['Live Job Listings', 'Smart Skill Matching', 'Direct Application'],
    icon: <Briefcase size={32} style={{ color: '#30d158' }} />,
    path: '/internships',
    color: '#30d158',
  },
  {
    title: 'Interview Prep',
    description: 'Master your technical interviews with comprehensive question banks, difficulty levels, and detailed technical explanations.',
    features: ['Must Have Technical Skills', 'Easy, Moderate, Difficult Qs', 'Technical Explanations'],
    icon: <Sparkles size={32} style={{ color: '#0a84ff' }} />,
    path: '/interview',
    color: '#0a84ff',
  },
  {
    title: 'DigiLocker',
    description: 'Safeguard your academic transcripts, certificates, identity cards, and financial documents with ease and privacy.',
    features: ['Secure Cloud Storage', 'Encrypted Documents', 'Quick Share Links', 'Auto Verification'],
    icon: <Shield size={32} style={{ color: '#ff9f0a' }} />,
    path: '/digilocker',
    color: '#ff9f0a',
  },
];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);

  const welcomeMessage = user?.name ? `Welcome, ${user.name}!` : 'Welcome to GradSphere!';

  return (
    <div className={styles.container}>
      <HeroSection
        title={welcomeMessage}
        subtitle="Your intelligent university student assistance platform. Explore our specialized modules below."
      />

      <section className={styles.grid}>
        {modules.map((mod) => (
          <Card key={mod.title} className={styles.card} hoverable={true}>
            <div className={styles.cardHeader}>
              <div
                className={styles.iconWrapper}
                style={{
                  background: `rgba(${mod.color === '#ff2d55' ? '255, 45, 85' : mod.color === '#30d158' ? '48, 209, 88' : mod.color === '#0a84ff' ? '10, 132, 255' : '255, 159, 10'}, 0.15)`
                }}
              >
                {mod.icon}
              </div>
              <h3 className={styles.title}>{mod.title}</h3>
            </div>

            <p className={styles.desc}>{mod.description}</p>

            <ul className={styles.featuresList}>
              {mod.features.map((feature, idx) => (
                <li key={idx} className={styles.featureItem}>
                  <ArrowRight size={14} className={styles.featureIcon} style={{ color: mod.color }} />
                  {feature}
                </li>
              ))}
            </ul>

            <Button
              variant="primary"
              onClick={() => navigate(mod.path)}
              className={styles.button}
              style={{
                background: `linear-gradient(135deg, ${mod.color} 0%, rgba(0, 0, 0, 0.4) 100%)`,
                border: 'none',
                marginTop: 'auto',
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
              }}
            >
              Explore
            </Button>
          </Card>
        ))}
      </section>
    </div>
  );
};

export default Dashboard;
