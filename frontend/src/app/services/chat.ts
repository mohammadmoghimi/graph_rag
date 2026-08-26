import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChatWebsite {
  id: number;
  name: string;
  url: string;
}

export interface ChatSession {
  id: number;
  title: string;
  websites: ChatWebsite[];
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://127.0.0.1:8000/api/chats';

  constructor(private http: HttpClient) {}

  createChat(
    title: string,
    websiteIds: number[]
  ): Observable<ChatSession> {
    return this.http.post<ChatSession>(`${this.apiUrl}/`, {
      title,
      website_ids: websiteIds
    });
  }

  getChat(id: number): Observable<ChatSession> {
  return this.http.get<ChatSession>(`${this.apiUrl}/${id}/`);
}
}