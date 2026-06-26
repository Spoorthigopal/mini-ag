import api from './api';

export interface ChatRequest {
  query: string;
  session_id?: string;
  filters?: {
    scheme_type?: string;
    amount_min?: number;
    amount_max?: number;
    provider?: string;
  };
}

export interface SchemeResponse {
  id: string;
  name: string;
  description: string;
  scheme_type: string;
  provider: string;
  states: string;
  category: string;
  tags: string;
  application_url: string;
  scheme_status: string;
  amount: string;
  deadline: string;
  eligibility: string[];
}

export interface ChatResponse {
  response: string;
  schemes: SchemeResponse[];
  session_id: string;
}

export const sendWelfareChatMessage = async (data: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post('/welfare/chat', data);
  return response.data;
};
