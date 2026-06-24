import React from " react\;
import { useNavigate } from \react-router-dom\;
import HeroSection from \../components/Layout/HeroSection\;
import Card from \../components/Common/Card\;
import Button from \../components/Common/Button\;
import styles from \./Dashboard.module.css\;
import { useAppSelector } from \../redux/store\; // adjust import path if needed

const modules = [
 { title: \Welfare\, description: \Explore welfare schemes and resources.\, icon: \??\, path: \/welfare\ },
 { title: \Internships\, description: \Find and apply for internships.\, icon: \??\, path: \/internships\ },
 { title: \Interview\, description: \Practice interview questions and get feedback.\, icon: \??\, path: \/interview\ },
 { title: \DigiLocker\, description: \Access your documents securely.\, icon: \??\, path: \/digilocker\ },
];

const Dashboard: React.FC = () => {
 const navigate = useNavigate();
 const user = useAppSelector((state) => state.auth?.user);

 const welcome = Welcome!;

 return (
 <div className={styles.container}>
 <HeroSection title={welcome} subtitle=\Your personalized dashboard\ />
 <section className={styles.grid}>
 {modules.map((mod) => (
 <Card key={mod.title} className={styles.card}>
 <div className={styles.icon}>{mod.icon}</div>
 <h3 className={styles.title}>{mod.title}</h3>
 <p className={styles.desc}>{mod.description}</p>
 <Button variant=\primary\ onClick={() => navigate(mod.path)} className={styles.button}>
 Go to {mod.title}
 </Button>
 </Card>
 ))}
 </section>
 </div>
 );
};

export default Dashboard;
