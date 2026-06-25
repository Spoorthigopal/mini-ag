import React from 'react';
import InternshipChat from '../../components/Internships/InternshipChat';
import ResumeUploader from '../../components/Internships/ResumeUploader';
import { useDispatch } from 'react-redux';
import { setResumeData } from '../../redux/slices/internshipSlice';

export const ChatPage: React.FC = () => {
  const dispatch = useDispatch();

  const handleUploadSuccess = (fileName: string, parsedData: any) => {
    dispatch(setResumeData({
      fileName,
      parsedData,
      parsedAt: new Date().toISOString(),
    }));
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0 }}>Internship & Resume Assistant</h2>
        <p style={{ color: 'rgba(255, 255, 255, 0.5)', margin: '0.25rem 0 0 0', fontSize: '0.9375rem' }}>
          Upload your resume to receive AI feedback, parse key skills, and chat with our assistant for cover letters or prep help.
        </p>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '2rem', alignItems: 'flex-start' }}>
        <ResumeUploader onUploadSuccess={handleUploadSuccess} />
        <InternshipChat />
      </div>
    </div>
  );
};

export default ChatPage;
