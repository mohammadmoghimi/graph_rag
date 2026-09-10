import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface DisplayMessage {
  role: 'user' | 'assistant';
  content: string;
  mostRelevantChunk?: string;
}

export interface ChatWebsite {
  id: number;
  name: string;
  url: string;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  mostRelevantChunk?: string;
  created_at: string;
}

export interface ChatDocument {
  id: number;
  name: string;
  description: string;
}

export interface ChatSession {
  id: number;
  title: string;
  websites: ChatWebsite[];
  documents: ChatDocument[];
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface ChatAnswer {
  answer: string;
  most_relevant_chunk: string;

}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
}

export interface ChatGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://127.0.0.1:8000/api/chats';

  constructor(private http: HttpClient) {}

  getChats(): Observable<ChatSession[]> {
    return this.http.get<ChatSession[]>(`${this.apiUrl}/`);
  }

  createChat(
    title: string,
    websiteIds: number[] = [],
    documentIds: number[] = []
  ): Observable<ChatSession> {
    return this.http.post<ChatSession>(`${this.apiUrl}/`, {
      title,
      website_ids: websiteIds,
      document_ids: documentIds
    });
  }

  getChat(id: number): Observable<ChatSession> {
  return this.http.get<ChatSession>(`${this.apiUrl}/${id}/`);
}

  ask(id: number, question: string): Observable<ChatAnswer> {
    return this.http.post<ChatAnswer>(`${this.apiUrl}/${id}/ask/`,{ question });
  }

  getGraph(id: number): Observable<ChatGraph> {
    return this.http.get<ChatGraph>(`${this.apiUrl}/${id}/graph/`);
  }
}