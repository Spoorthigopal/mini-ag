/**
 * Application Constants
 */

export const API_ROUTES = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  WELFARE_SCHEMES: '/welfare/schemes',
  INTERNSHIPS: '/internships/jobs',
  RESUME_UPLOAD: '/internships/resume/upload',
  INTERVIEW_START: '/interview/start',
  DOCUMENTS: '/documents',
};

export const DOCUMENT_CATEGORIES = {
  ACADEMIC: 'Academic',
  PROFESSIONAL: 'Professional',
  IDENTITY: 'Identity',
  FINANCIAL: 'Financial',
} as const;

export const MAX_FILE_SIZE_MB = 10;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
