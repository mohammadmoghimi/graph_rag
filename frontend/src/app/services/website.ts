import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Website {
  id: number;
  name: string;
  url: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  last_crawled_at: string | null;
}

@Injectable({
  providedIn: 'root',
})
export class Website {
    private apiUrl = 'http://127.0.0.1:8000/api/websites';

  constructor(private http: HttpClient) {}

  getWebsites(): Observable<Website[]> {
    return this.http.get<Website[]>(`${this.apiUrl}/`);
  }

  createWebsite(
    name: string,
    url: string,
    description: string
  ): Observable<Website> {

    return this.http.post<Website>(
      `${this.apiUrl}/`,
      {
        name,
        url,
        description
      }
    );
  }

  deleteWebsite(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/${id}/`
    );
  }

  crawlWebsite(id: number): Observable<any> {
  return this.http.post(
    `${this.apiUrl}/${id}/crawl/`,
    {}
  );
}
  
}
